import AppKit
import CoreGraphics
import ScreenCaptureKit

// The owning PID identifies this capture session even when several VS Code instances are open.
@main
@MainActor
struct WindowCapture {
    static func main() async {
        do {
            NSApplication.shared.setActivationPolicy(.prohibited)
            let arguments = Array(CommandLine.arguments.dropFirst())
            guard arguments.count >= 2, let pid = Int32(arguments[1]),
                  arguments[0] == "list" || arguments[0] == "capture" || arguments[0] == "activate" else {
                throw failure("Use: list PID, activate PID, or capture PID WINDOW_ID OUTPUT.png")
            }
            if arguments[0] == "activate" {
                guard let app = NSRunningApplication(processIdentifier: pid), app.activate(options: []) else {
                    throw failure("Could not activate the isolated editor process")
                }
                return
            }
            let content = try await SCShareableContent.excludingDesktopWindows(true, onScreenWindowsOnly: false)
            let windows = content.windows.filter {
                $0.owningApplication?.processID == pid && !($0.title ?? "").isEmpty
                    && $0.frame.width > 200 && $0.frame.height > 200
            }
            if arguments[0] == "list" {
                let records: [[String: Any]] = windows.map { window in
                    ["id": window.windowID, "pid": pid, "title": window.title ?? "",
                     "width": window.frame.width, "height": window.frame.height,
                     "bundleIdentifier": window.owningApplication?.bundleIdentifier ?? ""]
                }
                let data = try JSONSerialization.data(withJSONObject: records, options: [.sortedKeys])
                guard let json = String(data: data, encoding: .utf8) else {
                    throw failure("Could not encode window inventory")
                }
                print(json)
                return
            }
            guard arguments.count == 4, let id = UInt32(arguments[2]),
                  let window = windows.first(where: { $0.windowID == id }) else {
                throw failure("The requested window does not belong to the capture session")
            }
            let filter = SCContentFilter(desktopIndependentWindow: window)
            let configuration = SCStreamConfiguration()
            configuration.width = Int(filter.contentRect.width * CGFloat(filter.pointPixelScale))
            configuration.height = Int(filter.contentRect.height * CGFloat(filter.pointPixelScale))
            configuration.showsCursor = false
            configuration.ignoreShadowsSingleWindow = true
            let pixels = try await SCScreenshotManager.captureImage(contentFilter: filter, configuration: configuration)
            guard let png = NSBitmapImageRep(cgImage: pixels).representation(using: .png, properties: [:]) else {
                throw failure("Could not encode the native capture as PNG")
            }
            try png.write(to: URL(fileURLWithPath: arguments[3]), options: [.atomic])
            print("Saved \(pixels.width)x\(pixels.height) PNG")
        } catch {
            fputs("Window capture failed: \(error)\n", stderr)
            exit(1)
        }
    }

    static func failure(_ message: String) -> NSError {
        NSError(domain: "window-capture", code: 1, userInfo: [NSLocalizedDescriptionKey: message])
    }
}
