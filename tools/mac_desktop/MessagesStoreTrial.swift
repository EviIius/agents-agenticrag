// Named, exact-build trial helper. No Accessibility, Automation, send, network or model APIs.
import AppKit

let storeIdentity = "dev.agenticrag.aether.messages-reader"
let storeHome = FileManager.default.homeDirectoryForCurrentUser.appendingPathComponent(".local/share/workbench/qa/assistant-messages-store-20261109", isDirectory: true)
struct StoreSelection: Codable, Equatable { let address: String; let scope: String }
struct StoreJob: Decodable {
    let `protocol`: Int
    let request_id: String
    let operation: String
    let expires_at: Double
}
func storePrivateRead(_ file: URL, _ maximum: Int) throws -> Data {
    guard file.standardizedFileURL == file.resolvingSymlinksInPath() else { throw StoreFailure.invalid }
    let descriptor = Darwin.open(file.path, O_RDONLY | O_NOFOLLOW)
    guard descriptor >= 0 else { throw StoreFailure.invalid }
    let handle = FileHandle(fileDescriptor: descriptor, closeOnDealloc: true)
    var info = stat()
    guard fstat(descriptor, &info) == 0, info.st_mode & S_IFMT == S_IFREG,
          info.st_mode & 0o777 == 0o600, info.st_uid == getuid(), info.st_size <= maximum else { throw StoreFailure.invalid }
    let data = handle.readData(ofLength: maximum + 1)
    guard data.count <= maximum else { throw StoreFailure.invalid }
    return data
}
func storePrivateWrite(_ object: Any, _ file: URL) throws {
    let bytes = try JSONSerialization.data(withJSONObject: object, options: [.sortedKeys])
    let descriptor = Darwin.open(file.path, O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW, 0o600)
    guard descriptor >= 0 else { throw StoreFailure.invalid }
    defer { Darwin.close(descriptor) }
    try bytes.withUnsafeBytes { buffer in
        var offset = 0
        while offset < buffer.count {
            let wrote = Darwin.write(descriptor, buffer.baseAddress!.advanced(by: offset), buffer.count - offset)
            guard wrote > 0 else { throw StoreFailure.unavailable }
            offset += wrote
        }
    }
}
func storePrivateDirectory(_ url: URL) throws {
    let info = try FileManager.default.attributesOfItem(atPath: url.path)
    guard url.resolvingSymlinksInPath() == url.standardizedFileURL,
          info[.type] as? FileAttributeType == .typeDirectory,
          (info[.ownerAccountID] as? NSNumber)?.uint32Value == getuid(),
          (info[.posixPermissions] as? NSNumber)?.intValue == 0o700 else { throw StoreFailure.invalid }
}
func storeJob(_ directory: URL) throws -> StoreJob {
    try storePrivateDirectory(storeHome)
    try storePrivateDirectory(directory)
    guard directory.deletingLastPathComponent().standardizedFileURL == storeHome.appendingPathComponent("native").standardizedFileURL else { throw StoreFailure.invalid }
    let bytes = try storePrivateRead(directory.appendingPathComponent("request.json"), 4096)
    guard let raw = try JSONSerialization.jsonObject(with: bytes) as? [String: Any],
          Set(raw.keys) == Set(["protocol", "request_id", "operation", "expires_at"]),
          let version = raw["protocol"] as? NSNumber, CFGetTypeID(version) != CFBooleanGetTypeID(),
          !["d", "f"].contains(String(cString: version.objCType)), version.intValue == 1 else { throw StoreFailure.invalid }
    let job = try JSONDecoder().decode(StoreJob.self, from: bytes)
    guard job.protocol == 1, ["resolve_self", "read_thread"].contains(job.operation),
          job.request_id == directory.lastPathComponent,
          job.request_id.range(of: "^[a-f0-9]{32}$", options: .regularExpression) != nil,
          job.expires_at.isFinite, job.expires_at > Date().timeIntervalSince1970,
          job.expires_at <= Date().timeIntervalSince1970 + 15 else { throw StoreFailure.invalid }
    return job
}
func storeSelection() throws -> StoreSelection {
    let bytes = try storePrivateRead(storeHome.appendingPathComponent("selection.json"), 1024)
    guard let object = try JSONSerialization.jsonObject(with: bytes) as? [String: Any],
          Set(object.keys) == Set(["address", "scope"]) else { throw StoreFailure.invalid }
    let selection = try JSONDecoder().decode(StoreSelection.self, from: bytes)
    guard selection.scope == "self", exactAddress(selection.address) else { throw StoreFailure.invalid }
    return selection
}
func storeTarget() throws -> StoreTarget {
    let bytes = try storePrivateRead(storeHome.appendingPathComponent("target.json"), 2048)
    guard let object = try JSONSerialization.jsonObject(with: bytes) as? [String: Any],
          Set(object.keys) == Set(["chat_guid", "address", "service", "handle_row_id"]) else { throw StoreFailure.invalid }
    let value = try JSONDecoder().decode(StoreTarget.self, from: bytes)
    guard !value.chat_guid.isEmpty, value.chat_guid.utf8.count <= 200, exactAddress(value.address),
          ["iMessage", "SMS", "RCS"].contains(value.service), value.handle_row_id > 0 else { throw StoreFailure.invalid }
    return value
}
func storeObject<T: Encodable>(_ value: T) throws -> Any {
    try JSONSerialization.jsonObject(with: JSONEncoder().encode(value))
}
func executeStore(_ directory: URL) {
    do {
        let job = try storeJob(directory)
        try storePrivateWrite(["request_id": job.request_id, "pid": Int(getpid())], directory.appendingPathComponent("helper.json"))
        DispatchQueue.global().asyncAfter(deadline: .now() + min(12, max(0, job.expires_at - Date().timeIntervalSince1970))) { _exit(75) }
        var result: [String: Any]
        do {
            let selection = try storeSelection()
            let budget = StoreBudget(min(3, job.expires_at - Date().timeIntervalSince1970), cancel: directory.appendingPathComponent("cancel"))
            let path = FileManager.default.homeDirectoryForCurrentUser.appendingPathComponent("Library/Messages/chat.db")
            guard path.standardizedFileURL == path.resolvingSymlinksInPath() else { throw StoreFailure.invalid }
            let store = try MessagesStore(path: path.path, budget: budget)
            if job.operation == "resolve_self" {
                let first = try store.transaction { try store.resolve(selection.address) }
                let second = try store.transaction { try store.resolve(selection.address) }
                guard first == second, try storeSelection() == selection else { throw StoreFailure.stale_selection }
                try storePrivateWrite(try storeObject(first), storeHome.appendingPathComponent("target.json"))
                result = ["status": "ok", "target": try storeObject(first)]
            } else {
                let target = try storeTarget()
                guard target.address == selection.address else { throw StoreFailure.stale_selection }
                let first = try store.read(target)
                let second = try store.read(target)
                guard first == second, try storeSelection() == selection, try storeTarget() == target else { throw StoreFailure.stale_selection }
                result = ["status": "ok", "snapshot": try storeObject(first)]
            }
        } catch let error as StoreFailure { result = ["status": error.rawValue] }
        catch { result = ["status": "unavailable"] }
        result["protocol"] = 1; result["request_id"] = job.request_id
        result["operation"] = job.operation; result["helper_identity"] = storeIdentity
        result["helper_pid"] = Int(getpid())
        try storePrivateWrite(result, directory.appendingPathComponent("response.json"))
        _exit(0)
    } catch { _exit(64) }
}
@MainActor final class StoreSetup: NSObject, NSApplicationDelegate {
    var window: NSWindow!
    let address = NSTextField(string: "")
    let status = NSTextField(wrappingLabelWithString: "No database is opened during setup. Enter your exact own Messages address, then Save selection. This trial cannot send messages.")
    func applicationDidFinishLaunching(_ notification: Notification) {
        window = NSWindow(contentRect: NSRect(x: 0, y: 0, width: 520, height: 300), styleMask: [.titled, .closable], backing: .buffered, defer: false)
        window.title = "Aether Messages Reader — private trial setup"
        window.isReleasedWhenClosed = false
        let title = NSTextField(labelWithString: "Choose your conversation with yourself")
        title.font = .boldSystemFont(ofSize: 18)
        title.frame = NSRect(x: 24, y: 246, width: 472, height: 28)
        status.frame = NSRect(x: 24, y: 166, width: 472, height: 68)
        address.placeholderString = "+countrycode and number, or your exact iMessage email"
        address.frame = NSRect(x: 24, y: 120, width: 472, height: 30)
        address.setAccessibilityLabel("Your exact own Messages address")
        let save = NSButton(title: "Save selection", target: self, action: #selector(saveSelection))
        save.frame = NSRect(x: 320, y: 64, width: 176, height: 36)
        let cancel = NSButton(title: "Close", target: self, action: #selector(closeSetup))
        cancel.frame = NSRect(x: 24, y: 64, width: 100, height: 36)
        for view in [title, status, address, save, cancel] { window.contentView!.addSubview(view) }
        window.center(); window.makeKeyAndOrderFront(nil)
        NSApp.activate(ignoringOtherApps: true)
    }
    @objc func saveSelection() {
        do {
            try storePrivateDirectory(storeHome)
            guard exactAddress(address.stringValue) else {
                status.stringValue = "Use your exact number including +country code, or your iMessage email. Nothing has been read."
                return
            }
            try storePrivateWrite(["address": address.stringValue, "scope": "self"], storeHome.appendingPathComponent("selection.json"))
            address.stringValue = ""; address.isEnabled = false
            status.stringValue = "Selection saved privately. Now add this exact Aether Messages Reader app in System Settings → Privacy & Security → Full Disk Access. Confirm in Codex when both steps are done. No Messages data has been read."
        } catch { status.stringValue = "Selection could not be saved, or a selection already exists. Nothing has been read; return to Codex." }
    }
    @objc func closeSetup() { NSApp.terminate(nil) }
    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool { true }
}
let arguments = Array(CommandLine.arguments.dropFirst())
if arguments == ["--manifest"] {
    print("{\"protocol\":1,\"identity\":\"dev.agenticrag.aether.messages-reader\",\"operations\":[\"resolve_self\",\"read_thread\"],\"read_only\":true,\"input_or_send\":false,\"model_calls\":0}")
} else if arguments == ["--setup"] {
    guard Bundle.main.bundleIdentifier == storeIdentity else { _exit(64) }
    let app = NSApplication.shared
    app.setActivationPolicy(.regular)
    MainActor.assumeIsolated {
        let delegate = StoreSetup()
        app.delegate = delegate
        withExtendedLifetime(delegate) { app.run() }
    }
} else if arguments.count == 2 && arguments[0] == "--native-job" {
    guard Bundle.main.bundleIdentifier == storeIdentity else { _exit(64) }
    let app = NSApplication.shared
    app.setActivationPolicy(.accessory)
    let directory = URL(fileURLWithPath: arguments[1], isDirectory: true)
    Task { executeStore(directory) }
    app.run()
} else { _exit(64) }
