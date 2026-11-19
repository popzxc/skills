"""Small SVG drawing primitives for the personal sketch-diagram skill."""

from copy import deepcopy
from pathlib import Path
import random
import xml.etree.ElementTree as ET


NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)
PALETTES = {
    "dark": {
        "paper": "#18191b", "ink": "#e7e5e1", "muted": "#858b93",
        "blue": "#8eb8df", "orange": "#dfa47c", "green": "#8bc49a", "red": "#e59389",
    },
    "light": {
        "paper": "#ffffff", "ink": "#252525", "muted": "#9b9fa4",
        "blue": "#416f99", "orange": "#a75f31", "green": "#2f7951", "red": "#ad4944",
    },
}


class Sketch:
    """Keep geometry independent of theme so both exports are the same drawing."""

    def __init__(self, width: float, height: float, title: str, description: str = "") -> None:
        self.root = ET.Element(f"{{{NS}}}svg", {
            "width": str(width), "height": str(height), "viewBox": f"0 0 {width:g} {height:g}",
            "role": "img", "aria-labelledby": "title desc",
        })
        self._seed = 0
        self._element(self.root, "title", id="title").text = title
        self._element(self.root, "desc", id="desc").text = description
        defs = self._element(self.root, "defs")
        self._element(defs, "style").text = (
            'text { font-family: "Chalkboard", "Comic Sans MS", cursive; }'
        )
        # Explicit role-colored markers also work in renderers without context-stroke support.
        for role in PALETTES["dark"]:
            if role == "paper":
                continue
            marker = self._element(defs, "marker", id=f"arrow-{role}", viewBox="0 0 12 12",
                                   markerWidth=12, markerHeight=12, refX=11, refY=6,
                                   orient="auto-start-reverse", markerUnits="userSpaceOnUse")
            self._element(marker, "path", d="M 1.1 1.4 Q 5.3 4.6 10.8 6.1 M 10.8 6.1 Q 5.6 8.4 1.5 11",
                          fill="none", stroke=f"@{role}", stroke_width=1.65,
                          stroke_linecap="round", stroke_linejoin="round")
        self._element(self.root, "rect", width=width, height=height, fill="@paper")

    @staticmethod
    def _element(parent: ET.Element, tag: str, **attrs: object) -> ET.Element:
        return ET.SubElement(parent, f"{{{NS}}}{tag}", {
            key.replace("_", "-"): str(value) for key, value in attrs.items() if value is not None
        })

    def group(self, *, id: str | None = None, transform: str | None = None,
              parent: ET.Element | None = None) -> ET.Element:
        """Group related marks without adding a visible container."""
        return self._element(self.root if parent is None else parent, "g", id=id, transform=transform)

    def text(self, x: float, y: float, value: str, *, role: str = "ink", size: float = 24,
             anchor: str = "middle", parent: ET.Element | None = None) -> ET.Element:
        """Place a short label; use explicit line positions for multiline labels."""
        element = self._element(self.root if parent is None else parent, "text", x=x, y=y,
                                fill=f"@{role}", font_size=size, text_anchor=anchor)
        element.text = value
        return element

    def path(self, d: str, *, role: str = "ink", fill: str | None = None, width: float = 1.8,
             arrow: bool = False, both: bool = False, dashed: bool = False, opacity: float = 1,
             parent: ET.Element | None = None) -> ET.Element:
        """Draw an authored connector, outline, or mark; routing remains a layout decision."""
        return self._element(self.root if parent is None else parent, "path", d=d,
                             fill="none" if fill is None else f"@{fill}", stroke=f"@{role}",
                             stroke_width=width, stroke_linecap="round", stroke_linejoin="round",
                             opacity=opacity, stroke_dasharray="8 7 6 8" if dashed else None,
                             marker_end=f"url(#arrow-{role})" if arrow or both else None,
                             marker_start=f"url(#arrow-{role})" if both else None)

    def box(self, x: float, y: float, width: float, height: float, *, role: str = "ink",
            fill: str | None = "paper", seed: int | None = None, tilt: float = 0,
            parent: ET.Element | None = None) -> ET.Element:
        """Draw two light pen passes; a fixed seed preserves an outline across repeated stages."""
        self._seed += 1
        rng = random.Random(self._seed if seed is None else seed)
        group = self.group(parent=parent, transform=f"rotate({tilt:g} {x + width / 2:g} {y + height / 2:g})" if tilt else None)
        for stroke in range(2):
            jitter = [rng.uniform(-1.4, 1.4) for _ in range(16)]

            def point(px: float, py: float, pair: int) -> str:
                return f"{px + jitter[pair * 2]:.2f} {py + jitter[pair * 2 + 1]:.2f}"

            outline = (
                f"M {point(x, y, 0)} "
                f"Q {point(x + width * .48, y, 1)} {point(x + width, y, 2)} "
                f"Q {point(x + width, y + height * .51, 3)} {point(x + width, y + height, 4)} "
                f"Q {point(x + width * .52, y + height, 5)} {point(x, y + height, 6)} "
                f"Q {point(x, y + height * .45, 7)} {point(x, y, 0)}"
            )
            self.path(outline, role=role, fill=fill if stroke == 0 else None,
                      width=1.8 if stroke == 0 else 1, opacity=1 if stroke == 0 else .38, parent=group)
        return group

    def ellipse(self, cx: float, cy: float, rx: float, ry: float, *, role: str = "ink",
                fill: str | None = "paper", parent: ET.Element | None = None) -> ET.Element:
        """Draw a loose ellipse with the same paired pen strokes as the boxes."""
        group = self.group(parent=parent)
        for stroke, offset in enumerate([0, .9]):
            outline = (
                f"M {cx - rx + offset:g} {cy - offset:g} "
                f"C {cx - rx - offset:g} {cy - ry * 1.33:g} {cx + rx + offset:g} {cy - ry * 1.31:g} {cx + rx:g} {cy + offset:g} "
                f"C {cx + rx - offset:g} {cy + ry * 1.32:g} {cx - rx:g} {cy + ry * 1.34:g} {cx - rx + offset:g} {cy - offset:g}"
            )
            self.path(outline, role=role, fill=fill if stroke == 0 else None,
                      width=1.8 if stroke == 0 else 1, opacity=1 if stroke == 0 else .38, parent=group)
        return group

    def save(self, path: str | Path, *, theme: str = "dark", colors: dict[str, str] | None = None) -> Path:
        """Resolve color roles on a copy; saving never changes the original geometry."""
        palette = PALETTES[theme] | (colors or {})
        output = deepcopy(self.root)
        for element in output.iter():
            for key, value in element.attrib.items():
                if value.startswith("@"):
                    element.set(key, palette[value[1:]])
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        ET.indent(output, space="  ")
        ET.ElementTree(output).write(destination, encoding="unicode")
        return destination

    def save_pair(self, prefix: str | Path) -> tuple[Path, Path]:
        """Export a matching pair named prefix-light.svg and prefix-dark.svg."""
        prefix = Path(prefix)
        light = self.save(prefix.parent / f"{prefix.name}-light.svg", theme="light")
        dark = self.save(prefix.parent / f"{prefix.name}-dark.svg", theme="dark")
        return light, dark
