"""Capture all before scenes, then all after scenes, in an isolated macOS VS Code window."""

import argparse
import datetime
import json
import os
import plistlib
import re
import secrets
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from compose import compose_pair, sha256

SKILL = Path(__file__).resolve().parent.parent
DEFAULT_HOOKS = {
    "configuration": "rust-glancer",
    "serverPathSetting": "server.path",
    "start": "rust-glancer.startServer",
    "stop": "rust-glancer.stopServer",
    "state": "rust-glancer.test.getState",
    "output": "rust-glancer.test.getOutput",
}


def resolve_path(value: str, base: Path) -> Path:
    expanded = Path(os.path.expandvars(value)).expanduser()
    return (expanded if expanded.is_absolute() else base / expanded).resolve()


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n")


def discover_extension(extension_id: str) -> Path:
    candidates = []
    for directory in (Path.home() / ".vscode/extensions").glob(extension_id + "-*"):
        package = directory / "package.json"
        if package.is_file():
            manifest = json.loads(package.read_text())
            version = manifest.get("version", "")
            if (
                re.fullmatch(r"\d+\.\d+\.\d+", version)
                and f"{manifest.get('publisher')}.{manifest.get('name')}"
                == extension_id
            ):
                candidates.append((tuple(map(int, version.split("."))), directory))
    if not candidates:
        raise ValueError(
            f"No stable installed {extension_id} extension; supply extension.path"
        )
    return max(candidates, key=lambda candidate: candidate[0])[1]


def prepare_plan(path: Path) -> dict[str, Any]:
    plan = json.loads(path.read_text())
    base = path.resolve().parent
    plan["workspace"] = str(resolve_path(plan["workspace"], base))
    plan["readyRoot"] = str(
        resolve_path(plan.get("readyRoot", plan["workspace"]), base)
    )
    if not Path(plan["workspace"]).is_dir():
        raise ValueError("workspace must be an existing directory")
    extension = plan.setdefault("extension", {})
    extension_id = extension.setdefault("id", "rust-glancer.rust-glancer")
    extension_path = (
        resolve_path(extension["path"], base)
        if extension.get("path")
        else discover_extension(extension_id)
    )
    extension["path"] = str(extension_path)
    package = json.loads((extension_path / "package.json").read_text())
    if f"{package.get('publisher')}.{package.get('name')}" != extension_id:
        raise ValueError("extension.path does not match extension.id")
    servers = plan["servers"]
    before = servers.get("before") or str(extension_path / "server/rust-glancer")
    plan["servers"] = {
        "before": str(resolve_path(before, base)),
        "after": str(resolve_path(servers["after"], base)),
    }
    for phase, executable in plan["servers"].items():
        if not Path(executable).is_file() or not os.access(executable, os.X_OK):
            raise ValueError(
                f"{phase} server is not an existing executable: {executable}"
            )
    plan["hooks"] = DEFAULT_HOOKS | plan.get("hooks", {})
    settings = plan.get("settings", {})
    setting = plan["hooks"]["configuration"] + "." + plan["hooks"]["serverPathSetting"]
    if setting in settings:
        raise ValueError("Set per-phase servers instead of the server path in settings")
    for name, default in [("readyTimeoutSeconds", 150), ("queryTimeoutSeconds", 10)]:
        plan.setdefault(name, default)
        if not isinstance(plan[name], (int, float)) or not 0 < plan[name] <= 600:
            raise ValueError(f"{name} must be positive and at most 600")
    if not plan["scenes"]:
        raise ValueError("At least one scene is required")
    seen = set()
    for scene in plan["scenes"]:
        if (
            not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,63}", scene["id"])
            or scene["id"] in seen
        ):
            raise ValueError(
                "Scene IDs must be unique, filesystem-safe lowercase names"
            )
        seen.add(scene["id"])
        source = resolve_path(scene["file"], Path(plan["workspace"]))
        source.relative_to(Path(plan["workspace"]))
        if not source.is_file() or not scene.get("marker"):
            raise ValueError(
                f"{scene['id']} needs an existing file and a nonempty marker"
            )
        scene["file"] = str(source.relative_to(Path(plan["workspace"])))
        if scene.get("occurrence", 0) < 0 or scene.get("topLine", 0) < 0:
            raise ValueError("occurrence and topLine must be nonnegative")
    plan["vscodeApp"] = str(
        resolve_path(
            plan.get("vscodeApp", "/Applications/Visual Studio Code.app"), base
        )
    )
    return plan


def process_table() -> dict[int, tuple[int, str]]:
    output = subprocess.run(
        ["ps", "-axo", "pid=,ppid=,command="],
        check=True,
        capture_output=True,
        text=True,
        timeout=10,
    ).stdout
    result = {}
    for line in output.splitlines():
        columns = line.strip().split(None, 2)
        if len(columns) == 3:
            result[int(columns[0])] = (int(columns[1]), columns[2])
    return result


def remember_descendants(pid: int, owned: dict[int, tuple[int, str]]) -> None:
    table = process_table()
    descendants = {pid}
    while True:
        found = {child for child, (parent, _) in table.items() if parent in descendants}
        if found.issubset(descendants):
            break
        descendants.update(found)
    owned.update({child: table[child] for child in descendants if child in table})


def survivors(owned: dict[int, tuple[int, str]]) -> list[int]:
    current = process_table()
    return [
        pid
        for pid, (_, command) in owned.items()
        if pid in current and current[pid][1] == command
    ]


def cleanup_processes(
    process: subprocess.Popen, owned: dict[int, tuple[int, str]]
) -> dict[str, Any]:
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGTERM)
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait(timeout=5)
    # Inspect only the recorded family, including children reparented during editor shutdown.
    remaining = survivors(owned)
    for sig in [signal.SIGTERM, signal.SIGKILL]:
        for pid in remaining:
            try:
                os.kill(pid, sig)
            except ProcessLookupError:
                pass
        deadline = time.monotonic() + 5
        while remaining and time.monotonic() < deadline:
            time.sleep(0.2)
            remaining = survivors(owned)
        if not remaining:
            break
    return {
        "mainExitCode": process.returncode,
        "ownedPids": sorted(owned),
        "remainingPids": remaining,
        "verifiedEmpty": not remaining,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--capture-only", action="store_true")
    args = parser.parse_args()
    if sys.platform != "darwin":
        parser.error(
            "Native capture is macOS-only; use compose.py with externally captured originals"
        )
    plan = prepare_plan(args.plan)
    output = args.output.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    for scene in plan["scenes"]:
        for phase in ["before", "after"]:
            if (output / scene["id"] / f"{phase}.png").exists() and not args.overwrite:
                parser.error(
                    "Original captures already exist; choose a fresh output or use --overwrite"
                )
    manifest: dict[str, Any] = {
        "status": "running",
        "capturedAtUtc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "plan": plan,
        "servers": {
            phase: {"path": value, "sha256": sha256(Path(value))}
            for phase, value in plan["servers"].items()
        },
        "scenes": {},
    }
    package = json.loads((Path(plan["extension"]["path"]) / "package.json").read_text())
    entrypoint = Path(plan["extension"]["path"]) / package["main"]
    manifest["extension"] = {
        "id": plan["extension"]["id"],
        "version": package["version"],
        "path": plan["extension"]["path"],
        "entrypointSha256": sha256(entrypoint),
    }
    manifest_path = output / "manifest.json"
    write_json(manifest_path, manifest)
    scratch = Path(tempfile.mkdtemp(prefix="vscode-before-after-"))
    process = None
    port = None
    owned: dict[int, tuple[int, str]] = {}
    token = secrets.token_urlsafe(24)
    log = (output / "vscode-launch.log").open("w")

    def request(
        endpoint: str, method: str = "GET", timeout: float | None = None
    ) -> Any:
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}{endpoint}",
            method=method,
            headers={"Authorization": f"Bearer {token}"},
        )
        try:
            with urllib.request.urlopen(
                req, timeout=timeout or plan["readyTimeoutSeconds"] + 30
            ) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            detail = json.load(error)
            write_json(output / "failure.json", detail)
            raise RuntimeError(detail.get("error", detail)) from error

    try:
        capture_tool = scratch / "window-capture"
        print("Compiling native window capture helper", flush=True)
        subprocess.run(
            [
                "xcrun",
                "swiftc",
                "-parse-as-library",
                str(SKILL / "scripts/window-capture.swift"),
                "-o",
                str(capture_tool),
            ],
            check=True,
            timeout=120,
        )
        profile = scratch / "profile"
        (profile / "User").mkdir(parents=True)
        settings = {
            "telemetry.telemetryLevel": "off",
            "update.mode": "none",
            "extensions.autoUpdate": False,
            "workbench.startupEditor": "none",
            "window.restoreWindows": "none",
            "workbench.colorTheme": "Default Dark Modern",
            "workbench.sideBar.location": "left",
            "editor.fontSize": 18,
            "editor.minimap.enabled": False,
            "editor.semanticHighlighting.enabled": True,
            "editor.inlayHints.enabled": "on",
            "editor.foldingHighlight": False,
            "editor.stickyScroll.enabled": False,
        } | plan.get("settings", {})
        settings[
            plan["hooks"]["configuration"] + "." + plan["hooks"]["serverPathSetting"]
        ] = plan["servers"]["before"]
        write_json(profile / "User/settings.json", settings)
        extensions = scratch / "extensions"
        extensions.mkdir()
        copied_extension = extensions / Path(plan["extension"]["path"]).name
        shutil.copytree(plan["extension"]["path"], copied_extension)
        if (
            sha256(copied_extension / package["main"])
            != manifest["extension"]["entrypointSha256"]
        ):
            raise RuntimeError(
                "The extension changed while being copied; use a stable package path"
            )
        controller = scratch / "controller"
        shutil.copytree(SKILL / "assets/controller", controller)
        write_json(
            controller / "run.json",
            plan | {"extensionId": plan["extension"]["id"], "token": token},
        )
        app = Path(plan["vscodeApp"]) / "Contents"
        executable = plistlib.loads((app / "Info.plist").read_bytes())[
            "CFBundleExecutable"
        ]
        cli = app / "Resources/app/bin/code"
        env = os.environ.copy()
        for key in [
            "__RUST_GLANCER_SERVER",
            "ELECTRON_RUN_AS_NODE",
            "VSCODE_IPC_HOOK_CLI",
        ]:
            env.pop(key, None)
        env.update({"RUST_GLANCER_EXTENSION_TEST": "1"} | plan.get("environment", {}))
        first_file = Path(plan["workspace"]) / plan["scenes"][0]["file"]
        command = [
            str(app / "MacOS" / executable),
            "--new-window",
            "--disable-workspace-trust",
            "--skip-welcome",
            "--skip-release-notes",
            "--user-data-dir=" + str(profile),
            "--extensions-dir=" + str(extensions),
            "--extensionDevelopmentPath=" + str(controller),
            plan["workspace"],
            str(first_file),
        ]
        print("Launching isolated VS Code", flush=True)
        process = subprocess.Popen(
            command,
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        manifest["vscodeMainPid"] = process.pid
        write_json(manifest_path, manifest)
        deadline = time.monotonic() + 60
        bridge_file = controller / "bridge-info.json"
        while not bridge_file.exists() and time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError(
                    f"Isolated VS Code exited early: {process.returncode}"
                )
            time.sleep(0.5)
        if not bridge_file.exists():
            raise TimeoutError("VS Code controller did not activate within 60 seconds")
        port = json.loads(bridge_file.read_text())["port"]
        remember_descendants(process.pid, owned)
        for phase in ["before", "after"]:
            print(f"Preparing {phase} server", flush=True)
            if (
                sha256(Path(plan["servers"][phase]))
                != manifest["servers"][phase]["sha256"]
            ):
                raise RuntimeError(
                    f"{phase} binary changed during capture; use a stable build artifact"
                )
            request("/phase?name=" + phase, "POST")
            for scene in plan["scenes"]:
                print(f"Capturing {phase}: {scene['id']}", flush=True)
                subprocess.run(
                    [
                        str(cli),
                        "--user-data-dir",
                        str(profile),
                        "--reuse-window",
                        plan["workspace"],
                    ],
                    env=env,
                    check=True,
                    capture_output=True,
                    timeout=20,
                )
                subprocess.run(
                    [str(capture_tool), "activate", str(process.pid)],
                    check=True,
                    capture_output=True,
                    timeout=20,
                )
                data = request("/scene?id=" + urllib.parse.quote(scene["id"]), "POST")
                windows = json.loads(
                    subprocess.run(
                        [str(capture_tool), "list", str(process.pid)],
                        check=True,
                        capture_output=True,
                        text=True,
                        timeout=20,
                    ).stdout
                )
                if len(windows) != 1:
                    raise RuntimeError(
                        f"Expected one owned editor window, found {len(windows)}; inspect its native inventory"
                    )
                window = windows[0]
                if not data.get("focused"):
                    raise RuntimeError(
                        "The isolated editor lost focus; app switching may be interfering with capture"
                    )
                folder = output / scene["id"]
                folder.mkdir(exist_ok=True)
                write_json(folder / f"{phase}.json", data | {"window": window})
                subprocess.run(
                    [
                        str(capture_tool),
                        "capture",
                        str(process.pid),
                        str(window["id"]),
                        str(folder / f"{phase}.png"),
                    ],
                    check=True,
                    timeout=20,
                )
                info = {
                    "originalSha256": sha256(folder / f"{phase}.png"),
                    "sourceSha256": data["sourceSha256"],
                    "window": window,
                }
                manifest["scenes"].setdefault(scene["id"], {})[phase] = info
                if (
                    phase == "after"
                    and info["sourceSha256"]
                    != manifest["scenes"][scene["id"]]["before"]["sourceSha256"]
                ):
                    raise RuntimeError(
                        f"{scene['id']}: source changed between captures"
                    )
                remember_descendants(process.pid, owned)
                write_json(manifest_path, manifest)
        if not args.capture_only:
            for scene in plan["scenes"]:
                folder = output / scene["id"]
                manifest["scenes"][scene["id"]]["comparison"] = compose_pair(
                    folder / "before.png",
                    folder / "after.png",
                    folder,
                    scene.get("crop"),
                    scene.get("width", 1600),
                )
        manifest["status"] = "captured"
    except BaseException as error:
        manifest["status"] = "failed"
        manifest["error"] = str(error)
        raise
    finally:
        if process:
            remember_descendants(process.pid, owned)
            if port:
                try:
                    (output / "server-output.log").write_text(
                        request("/output", timeout=10)
                    )
                except (OSError, RuntimeError, ValueError) as error:
                    manifest["logCollectionError"] = str(error)
                try:
                    manifest["stoppedState"] = request("/close", "POST", timeout=15)
                except (OSError, RuntimeError, ValueError) as error:
                    manifest["shutdownError"] = str(error)
            manifest["cleanup"] = cleanup_processes(process, owned)
            if not manifest["cleanup"]["verifiedEmpty"]:
                manifest["status"] = "failed"
                manifest["error"] = "Some owned processes survived cleanup"
        log.close()
        write_json(manifest_path, manifest)
        if not process or manifest.get("cleanup", {}).get("verifiedEmpty"):
            shutil.rmtree(scratch)
        else:
            manifest["retainedScratch"] = str(scratch)
            write_json(manifest_path, manifest)
        print(f"Capture status: {manifest['status']}; evidence: {output}", flush=True)
    if not manifest.get("cleanup", {}).get("verifiedEmpty"):
        raise RuntimeError("Some owned processes survived cleanup; see manifest.json")


if __name__ == "__main__":
    main()
