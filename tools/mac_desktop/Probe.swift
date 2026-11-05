// AS1-A only: bounded role metadata. No text, screenshot or input APIs.
import AppKit
import ApplicationServices
import Foundation
import Darwin

let identity = "dev.agenticrag.aether.desktop-trial"
let targets = [
    "messages": ("com.apple.MobileSMS", "/System/Applications/Messages.app"),
    "notes": ("com.apple.Notes", "/System/Applications/Notes.app")
]
let roles: Set<String> = [
    "AXApplication", "AXWindow", "AXGroup", "AXSplitGroup", "AXScrollArea",
    "AXList", "AXOutline", "AXTable", "AXRow", "AXColumn", "AXCell",
    "AXTextArea", "AXTextField", "AXStaticText", "AXButton", "AXCheckBox",
    "AXRadioButton", "AXPopUpButton", "AXMenuButton", "AXToolbar", "AXTabGroup",
    "AXTab", "AXImage", "AXLink", "AXMenu", "AXMenuItem", "AXMenuBar",
    "AXSlider", "AXSplitter", "AXScrollBar", "AXSheet", "AXDialog",
    "AXProgressIndicator", "AXValueIndicator", "AXUnknown"
]
enum ProbeError: Error { case invalid, unavailable, stale, deadline, cancelled, identity }
struct Job: Decodable {
    let `protocol`: Int
    let request_id: String
    let operation: String
    let app: String?
    let expires_at: Double
}
struct Node: Codable {
    let path: [Int]
    let role: String
    let children: Int
}

// Shared by synthetic fixtures and the live reader. Never return arbitrary role strings.
func safeRole(_ value: String) -> String { roles.contains(value) ? value : "AXUnknown" }
func fixture(_ object: [String: Any]) throws -> [String: Any] {
    guard let input = object["tree"] as? [String: Any] else { throw ProbeError.invalid }
    var nodes: [Node] = []
    var truncated = false
    func visit(_ item: [String: Any], _ path: [Int]) {
        guard nodes.count < 160, path.count <= 8 else { truncated = true; return }
        let children = item["children"] as? [[String: Any]] ?? []
        nodes.append(Node(path: path, role: safeRole(item["role"] as? String ?? ""), children: children.count))
        for (index, child) in children.prefix(32).enumerated() { visit(child, path + [index]) }
        if children.count > 32 { truncated = true }
    }
    visit(input, [])
    return ["protocol": 1, "nodes": try JSONSerialization.jsonObject(with: JSONEncoder().encode(nodes)), "truncated": truncated]
}
func check(_ job: Job, _ directory: URL) throws {
    if FileManager.default.fileExists(atPath: directory.appendingPathComponent("cancel").path) {
        throw ProbeError.cancelled
    }
    if Date().timeIntervalSince1970 >= job.expires_at { throw ProbeError.deadline }
}
func readJob(_ directory: URL) throws -> Job {
    let file = directory.appendingPathComponent("request.json")
    let attributes = try FileManager.default.attributesOfItem(atPath: directory.path)
    guard attributes[.type] as? FileAttributeType == .typeDirectory,
          (attributes[.posixPermissions] as? NSNumber)?.intValue == 0o700,
          (attributes[.ownerAccountID] as? NSNumber)?.uint32Value == getuid(),
          directory.resolvingSymlinksInPath().path == directory.standardizedFileURL.path
    else { throw ProbeError.invalid }
    let descriptor = Darwin.open(file.path, O_RDONLY | O_NOFOLLOW)
    guard descriptor >= 0 else { throw ProbeError.invalid }
    let handle = FileHandle(fileDescriptor: descriptor, closeOnDealloc: true)
    var metadata = stat()
    guard fstat(descriptor, &metadata) == 0, metadata.st_mode & S_IFMT == S_IFREG,
          metadata.st_mode & 0o777 == 0o600, metadata.st_uid == getuid(),
          metadata.st_size <= 4096 else { throw ProbeError.invalid }
    let data = handle.readData(ofLength: 4097)
    guard data.count <= 4096 else { throw ProbeError.invalid }
    guard let object = try JSONSerialization.jsonObject(with: data) as? [String: Any],
          Set(object.keys) == Set(["protocol", "request_id", "operation", "app", "expires_at"]),
          object["protocol"] as? Int == 1 else { throw ProbeError.invalid }
    let job = try JSONDecoder().decode(Job.self, from: data)
    guard job.protocol == 1,
          job.request_id.range(of: "^[a-f0-9]{32}$", options: .regularExpression) != nil,
          ["permission", "request_access", "open", "structure"].contains(job.operation),
          job.expires_at.isFinite,
          job.expires_at <= Date().timeIntervalSince1970 + 60,
          (["open", "structure"].contains(job.operation) ? targets[job.app ?? ""] != nil : job.app == nil)
    else { throw ProbeError.invalid }
    try check(job, directory)
    return job
}
func writePrivate(_ object: [String: Any], _ file: URL) throws {
    let data = try JSONSerialization.data(withJSONObject: object, options: [.sortedKeys])
    // O_EXCL refuses a stale/symlinked receipt instead of replacing it.
    let descriptor = Darwin.open(file.path, O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW, 0o600)
    guard descriptor >= 0 else { throw ProbeError.invalid }
    defer { Darwin.close(descriptor) }
    try data.withUnsafeBytes { buffer in
        var offset = 0
        while offset < buffer.count {
            let count = Darwin.write(descriptor, buffer.baseAddress!.advanced(by: offset), buffer.count - offset)
            if count <= 0 { throw ProbeError.unavailable }
            offset += count
        }
    }
}
func running(_ key: String) throws -> NSRunningApplication {
    guard let target = targets[key] else { throw ProbeError.invalid }
    let matches = NSRunningApplication.runningApplications(withBundleIdentifier: target.0)
    guard matches.count == 1, let app = matches.first, !app.isTerminated else { throw ProbeError.unavailable }
    guard app.bundleIdentifier == target.0,
          app.bundleURL?.standardizedFileURL.path == target.1 else { throw ProbeError.identity }
    return app
}
final class Reader {
    let job: Job
    let directory: URL
    let started = ProcessInfo.processInfo.systemUptime
    init(_ job: Job, _ directory: URL) { self.job = job; self.directory = directory }
    func ready(_ element: AXUIElement) throws {
        try check(job, directory)
        guard ProcessInfo.processInfo.systemUptime - started < 3 else { throw ProbeError.deadline }
        guard AXUIElementSetMessagingTimeout(element, 0.15) == .success else { throw ProbeError.unavailable }
    }
    func attribute(_ element: AXUIElement, _ name: CFString) throws -> CFTypeRef? {
        try ready(element)
        var value: CFTypeRef?
        let status = AXUIElementCopyAttributeValue(element, name, &value)
        if status == .noValue || status == .attributeUnsupported { return nil }
        guard status == .success else { throw ProbeError.unavailable }
        return value
    }
    func focused(_ application: AXUIElement) throws -> AXUIElement {
        guard let value = try attribute(application, kAXFocusedWindowAttribute as CFString),
              CFGetTypeID(value) == AXUIElementGetTypeID() else { throw ProbeError.unavailable }
        return unsafeBitCast(value, to: AXUIElement.self)
    }
    func structure(_ process: NSRunningApplication) throws -> ([Node], Bool) {
        let application = AXUIElementCreateApplication(process.processIdentifier)
        let window = try focused(application)
        var nodes: [Node] = []
        var truncated = false
        func visit(_ element: AXUIElement, _ path: [Int]) throws {
            guard nodes.count < 160, path.count <= 8 else { truncated = true; return }
            let role = try attribute(element, kAXRoleAttribute as CFString) as? String ?? ""
            try ready(element)
            var total: CFIndex = 0
            let counted = AXUIElementGetAttributeValueCount(element, kAXChildrenAttribute as CFString, &total)
            if counted == .noValue || counted == .attributeUnsupported { total = 0 }
            else if counted != .success { throw ProbeError.unavailable }
            guard total >= 0, total <= 100_000 else { throw ProbeError.unavailable }
            nodes.append(Node(path: path, role: safeRole(role), children: total))
            if total == 0 { return }
            if path.count == 8 { truncated = true; return }
            try ready(element)
            var values: CFArray?
            guard AXUIElementCopyAttributeValues(element, kAXChildrenAttribute as CFString, 0, min(32, total), &values) == .success,
                  let children = values as? [AXUIElement] else { throw ProbeError.unavailable }
            if total > children.count { truncated = true }
            for (index, child) in children.enumerated() { try visit(child, path + [index]) }
        }
        try visit(window, [])
        guard !process.isTerminated, CFEqual(window, try focused(application)) else { throw ProbeError.stale }
        return (nodes, truncated)
    }
}
func native(_ job: Job, _ directory: URL) async throws -> [String: Any] {
    try check(job, directory)
    if ["permission", "request_access"].contains(job.operation) {
        let options = [kAXTrustedCheckOptionPrompt.takeUnretainedValue() as String: job.operation == "request_access"] as CFDictionary
        let trusted = AXIsProcessTrustedWithOptions(options)
        return ["status": trusted ? "ok" : "permission_required", "trusted": trusted]
    }
    guard let key = job.app, let target = targets[key],
          Bundle(url: URL(fileURLWithPath: target.1))?.bundleIdentifier == target.0 else { throw ProbeError.identity }
    if job.operation == "open" {
        let configuration = NSWorkspace.OpenConfiguration()
        configuration.activates = false
        let opened = try await NSWorkspace.shared.openApplication(at: URL(fileURLWithPath: target.1), configuration: configuration)
        try check(job, directory)
        let verified = try running(key)
        guard opened.processIdentifier == verified.processIdentifier else { throw ProbeError.identity }
        return ["status": "ok", "target_pid": Int(verified.processIdentifier), "bundle_id": target.0]
    }
    guard AXIsProcessTrusted() else { return ["status": "permission_required", "trusted": false] }
    let verified = try running(key)
    let (nodes, truncated) = try Reader(job, directory).structure(verified)
    return ["status": "ok", "trusted": true, "target_pid": Int(verified.processIdentifier),
            "bundle_id": target.0, "nodes": try JSONSerialization.jsonObject(with: JSONEncoder().encode(nodes)), "truncated": truncated]
}

func execute(_ directory: URL) async {
    do {
        let job = try readJob(directory)
        try writePrivate(["request_id": job.request_id, "pid": Int(getpid())], directory.appendingPathComponent("helper.json"))
        // This independent watchdog still exits if the target's AX IPC blocks the main thread.
        DispatchQueue.global().asyncAfter(deadline: .now() + min(12, max(0, job.expires_at - Date().timeIntervalSince1970))) { _exit(75) }
        var result: [String: Any]
        do { result = try await native(job, directory) }
        catch ProbeError.cancelled { result = ["status": "cancelled"] }
        catch ProbeError.deadline { result = ["status": "deadline"] }
        catch ProbeError.stale { result = ["status": "stale_window"] }
        catch ProbeError.identity { result = ["status": "identity_mismatch"] }
        catch { result = ["status": "unavailable"] }
        result["protocol"] = 1; result["request_id"] = job.request_id
        result["operation"] = job.operation; result["app"] = (job.app as Any?) ?? NSNull()
        result["helper_identity"] = identity; result["helper_pid"] = Int(getpid())
        try writePrivate(result, directory.appendingPathComponent("response.json"))
        _exit(0)
    } catch { _exit(64) } // Never print raw errors, paths or source values.
}

let arguments = Array(CommandLine.arguments.dropFirst())
if arguments.isEmpty || arguments == ["--manifest"] {
    let result: [String: Any] = ["protocol": 1, "identity": identity,
        "operations": ["permission", "request_access", "open", "structure"],
        "text_reading": false, "screenshots": false, "input_actions": false]
    print(String(data: try JSONSerialization.data(withJSONObject: result, options: [.sortedKeys]), encoding: .utf8)!)
} else if arguments == ["--fixture"] {
    do {
        let data = FileHandle.standardInput.readData(ofLength: 1_048_577)
        guard data.count <= 1_048_576,
              let object = try JSONSerialization.jsonObject(with: data) as? [String: Any] else { throw ProbeError.invalid }
        print(String(data: try JSONSerialization.data(withJSONObject: fixture(object), options: [.sortedKeys]), encoding: .utf8)!)
    } catch { _exit(64) }
} else if arguments.count == 2 && arguments[0] == "--validate-job" {
    do {
        let job = try readJob(URL(fileURLWithPath: arguments[1], isDirectory: true))
        let result: [String: Any] = ["valid": true, "operation": job.operation,
                                   "app": (job.app as Any?) ?? NSNull(), "native_executed": false]
        print(String(data: try JSONSerialization.data(withJSONObject: result, options: [.sortedKeys]), encoding: .utf8)!)
    } catch { _exit(64) }
} else if arguments.count == 2 && arguments[0] == "--native-job" {
    guard Bundle.main.bundleIdentifier == identity else { _exit(64) }
    let directory = URL(fileURLWithPath: arguments[1], isDirectory: true)
    let application = NSApplication.shared
    application.setActivationPolicy(.accessory)
    Task { await execute(directory) }
    application.run()
} else { _exit(64) }
