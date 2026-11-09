// Fixed app-opening primitive. No AX, Apple Events, screenshots, input or text reads.
import AppKit
import Foundation
import Darwin

let catalog = [
    "notes": ("com.apple.Notes", "/System/Applications/Notes.app"),
    "messages": ("com.apple.MobileSMS", "/System/Applications/Messages.app")
]
let args = Array(CommandLine.arguments.dropFirst())
guard args.count == 1, let target = catalog[args[0]],
      let bundle = Bundle(path: target.1), bundle.bundleIdentifier == target.0,
      URL(fileURLWithPath: target.1).resolvingSymlinksInPath().path == target.1
else { _exit(64) }

// The independent watchdog also bounds a hung AppKit completion callback.
DispatchQueue.global().asyncAfter(deadline: .now() + 6) { _exit(75) }
let application = NSApplication.shared
application.setActivationPolicy(.prohibited)
let workspace = NSWorkspace.shared
var candidate: NSRunningApplication?
var activation: NSObjectProtocol?
func finish() {
    guard let app = candidate, !app.isTerminated,
          app.bundleIdentifier == target.0,
          app.bundleURL?.standardizedFileURL.path == target.1,
          let foreground = workspace.frontmostApplication,
          foreground.processIdentifier == app.processIdentifier,
          foreground.bundleIdentifier == target.0 else { return }
    let receipt: [String: Any] = [
        "protocol": 1, "app": args[0], "status": "ok",
        "bundle_id": target.0, "bundle_path": target.1,
        "pid": Int(app.processIdentifier), "foreground_pid": Int(foreground.processIdentifier)
    ]
    guard let data = try? JSONSerialization.data(withJSONObject: receipt, options: [.sortedKeys])
    else { _exit(65) }
    FileHandle.standardOutput.write(data)
    _exit(0)
}
activation = workspace.notificationCenter.addObserver(
    forName: NSWorkspace.didActivateApplicationNotification, object: nil, queue: .main
) { _ in finish() }
let configuration = NSWorkspace.OpenConfiguration()
configuration.activates = true
configuration.addsToRecentItems = false
workspace.openApplication(at: URL(fileURLWithPath: target.1), configuration: configuration) { app, error in
    // AppKit delivers this callback on a concurrent queue. Serialize candidate
    // state and foreground inspection with the activation observer/main run loop.
    DispatchQueue.main.async {
        guard error == nil, let app = app else { _exit(69) }
        candidate = app
        finish()
    }
}
application.run()
