// Version 2 read-only snapshot: sealed boundary, private bounded text, no input/screenshot APIs.
import AppKit
import ApplicationServices
import Foundation
import Darwin

let identity = "dev.agenticrag.aether.desktop-trial"
let targets = [
    "messages": ("com.apple.MobileSMS", "/System/Applications/Messages.app")
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
enum ReadStage: String { case dispatch, structure, modifiability, character_count, bounded_range, selection_metadata, stability }
var readStage: ReadStage = .dispatch
struct Job: Decodable {
    let `protocol`: Int
    let request_id: String
    let operation: String
    let app: String?
    let expires_at: Double
}
struct Node: Codable, Equatable {
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
    return ["protocol": 2, "nodes": try JSONSerialization.jsonObject(with: JSONEncoder().encode(nodes)), "truncated": truncated]
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
          object["protocol"] as? Int == 2 else { throw ProbeError.invalid }
    let job = try JSONDecoder().decode(Job.self, from: data)
    guard job.protocol == 2,
          job.request_id.range(of: "^[a-f0-9]{32}$", options: .regularExpression) != nil,
          job.operation == "read_selected",
          job.expires_at.isFinite,
          job.expires_at <= Date().timeIntervalSince1970 + 60,
          (job.operation == "read_selected" ? job.app == "messages" : job.app == nil)
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
        readStage = .structure
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
// The selection specification is private numeric role metadata, sealed with this build.
struct BoundarySpec: Decodable {
    let nodes: [Node]
    let boundary: [Int]
    let paths: [[Int]]
}
// Fixed pane ancestry, variable bounded contents. Paths are selection coordinates,
// never recipient/message identities. All selected data stays unqualified/private.
func candidatePaths(_ shape: [Node], _ spec: BoundarySpec) -> [[Int]]? {
    guard shape.count <= 160, shape.first?.role == "AXWindow", shape.first?.path == [],
          !spec.boundary.isEmpty, spec.boundary.count <= 5 else { return nil }
    for depth in 0...spec.boundary.count {
        let path = Array(spec.boundary.prefix(depth))
        guard let expected = spec.nodes.first(where: { $0.path == path }),
              shape.contains(where: { $0.path == path && $0.role == expected.role }) else { return nil }
    }
    guard shape.contains(where: { $0.path == spec.boundary && $0.role == "AXGroup" }) else { return nil }
    let inside = shape.filter({ $0.path.starts(with: spec.boundary) })
    guard !inside.contains(where: { $0.role == "AXTextField" }) else { return nil }
    let areas = inside.filter({ $0.role == "AXTextArea" })
    guard (1...8).contains(areas.count), Set(areas.map({ $0.path })).count == areas.count else { return nil }
    for area in areas {
        guard area.path.count == spec.boundary.count + 3, area.children == 0,
              area.path.suffix(2) == [0, 0], area.path.allSatisfy({ 0 <= $0 && $0 < 32 }) else { return nil }
        for drop in 1...2 {
            let path = Array(area.path.dropLast(drop))
            guard inside.contains(where: { $0.path == path && $0.role == "AXGroup" && $0.children == 1 }) else { return nil }
        }
    }
    return areas.map({ $0.path })
}
func shapeMatches(_ shape: [Node], _ spec: BoundarySpec) -> Bool {
    candidatePaths(shape, spec) != nil
}
struct Area: Codable, Equatable {
    let path: [Int]
    let value: String
    let description: String
    let identifier: String
    let subrole: String
    let value_settable: Bool
}
struct Slice: Codable, Equatable {
    let qualification: String
    let window_title: String
    let group_identifier: String
    let boundary: [Int]
    let items: [Area]
    let access: String
}
func boundedSlice(_ object: [String: Any]) throws -> Slice {
    guard Set(object.keys) == Set(["qualification", "window_title", "group_identifier", "boundary", "items", "access"]),
          let items = object["items"] as? [[String: Any]],
          items.allSatisfy({ Set($0.keys) == Set(["path", "value", "description", "identifier", "subrole", "value_settable"]) })
    else { throw ProbeError.invalid }
    let slice = try JSONDecoder().decode(Slice.self, from: JSONSerialization.data(withJSONObject: object))
    guard slice.qualification == "unqualified", !slice.boundary.isEmpty, slice.boundary.count <= 5,
          slice.boundary.allSatisfy({ 0 <= $0 && $0 < 32 }),
          slice.window_title.utf8.count <= 200, slice.group_identifier.utf8.count <= 200,
          !slice.items.isEmpty, slice.items.count <= 8,
          slice.access == "read_only",
          Set(slice.items.map({ $0.path })).count == slice.items.count,
          slice.items.allSatisfy({ item in
              item.path.count <= 8 && item.path.count == slice.boundary.count + 3 && item.path.suffix(2) == [0, 0] &&
              Array(item.path.prefix(slice.boundary.count)) == slice.boundary &&
              item.path.allSatisfy({ 0 <= $0 && $0 < 32 }) &&
              item.value.utf8.count <= 4000 && item.description.utf8.count <= 1000 &&
              item.identifier.utf8.count <= 200 && item.subrole.utf8.count <= 200
          }), slice.items.reduce(0, { $0 + $1.value.utf8.count }) <= 16000
    else { throw ProbeError.invalid }
    return slice
}
func stableSlice(_ before: [String: Any], _ after: [String: Any]) throws -> [String: Any] {
    let first = try boundedSlice(before)
    guard first == (try boundedSlice(after)) else { throw ProbeError.stale }
    return try JSONSerialization.jsonObject(with: JSONEncoder().encode(first)) as! [String: Any]
}
extension Reader {
    func element(_ root: AXUIElement, _ path: [Int]) throws -> AXUIElement {
        var current = root
        for index in path {
            try ready(current)
            var values: CFArray?
            guard index >= 0, index < 32,
                  AXUIElementCopyAttributeValues(current, kAXChildrenAttribute as CFString, index, 1, &values) == .success,
                  let children = values as? [AXUIElement], children.count == 1
            else { throw ProbeError.unavailable }
            current = children[0]
        }
        return current
    }
    func text(_ element: AXUIElement, _ attributeName: String, _ maximum: Int) throws -> String {
        guard let raw = try attribute(element, attributeName as CFString) else { return "" }
        guard let value = raw as? String, value.utf8.count <= maximum else { throw ProbeError.unavailable }
        return value
    }
    func body(_ area: AXUIElement, _ length: Int) throws -> String {
        readStage = .bounded_range
        if length == 0 { return "" }
        try ready(area)
        var range = CFRange(location: 0, length: length)
        guard let parameter = AXValueCreate(.cfRange, &range) else { throw ProbeError.unavailable }
        var result: CFTypeRef?
        guard AXUIElementCopyParameterizedAttributeValue(area, kAXStringForRangeParameterizedAttribute as CFString, parameter, &result) == .success,
              let value = result as? String, value.utf8.count <= 4000,
              CFStringGetLength(value as CFString) == length else { throw ProbeError.unavailable }
        return value
    }
    func snapshot(_ window: AXUIElement, _ group: AXUIElement, _ areas: [([Int], AXUIElement, Bool)], _ boundary: [Int]) throws -> [String: Any] {
        readStage = .character_count
        var lengths: [Int] = []
        for (_, area, _) in areas {
            guard let raw = try attribute(area, kAXNumberOfCharactersAttribute as CFString) as? NSNumber,
                  CFGetTypeID(raw) != CFBooleanGetTypeID(), raw.doubleValue == Double(raw.intValue),
                  raw.intValue >= 0, raw.intValue <= 4000 else { throw ProbeError.unavailable }
            lengths.append(raw.intValue)
        }
        guard lengths.reduce(0, +) <= 16000 else { throw ProbeError.unavailable }
        readStage = .selection_metadata
        let title = try text(window, kAXTitleAttribute, 200)
        let groupID = try text(group, kAXIdentifierAttribute, 200)
        var values: [[String: Any]] = []
        for (index, entry) in areas.enumerated() {
            let (path, area, modifiable) = entry
            values.append(["path": path, "value": try body(area, lengths[index]),
                           "description": try text(area, kAXDescriptionAttribute, 1000),
                           "identifier": try text(area, kAXIdentifierAttribute, 200),
                           "subrole": try text(area, kAXSubroleAttribute, 200), "value_settable": modifiable])
        }
        return ["qualification": "unqualified", "window_title": title,
                "group_identifier": groupID,
                "boundary": boundary, "items": values, "access": "read_only"]
    }
    func candidate(_ process: NSRunningApplication, _ spec: BoundarySpec) throws -> [String: Any] {
        guard spec.nodes.count <= 160, spec.nodes.first?.path == [], spec.nodes.first?.role == "AXWindow",
              !spec.boundary.isEmpty, spec.boundary.count < 8, !spec.paths.isEmpty, spec.paths.count <= 8,
              spec.paths.allSatisfy({ $0.count <= 8 && $0.count > spec.boundary.count &&
                  Array($0.prefix(spec.boundary.count)) == spec.boundary && $0.allSatisfy({ 0 <= $0 && $0 < 32 }) }),
              Set(spec.paths).count == spec.paths.count else { throw ProbeError.invalid }
        let (shape, truncated) = try structure(process)
        guard !truncated, let paths = candidatePaths(shape, spec)
        else { throw ProbeError.stale }
        let application = AXUIElementCreateApplication(process.processIdentifier)
        let window = try focused(application)
        let group = try element(window, spec.boundary)
        var areas: [([Int], AXUIElement, Bool)] = []
        // Observe API modifiability as metadata. This program exposes no input operation.
        for path in paths {
            let area = try element(window, path)
            try ready(area)
            readStage = .modifiability
            var settable = DarwinBoolean(false)
            guard AXUIElementIsAttributeSettable(area, kAXValueAttribute as CFString, &settable) == .success
            else { throw ProbeError.unavailable }
            areas.append((path, area, settable.boolValue))
        }
        guard !areas.isEmpty else { throw ProbeError.unavailable }
        let before = try snapshot(window, group, areas, spec.boundary)
        let (shapeAfter, truncatedAfter) = try structure(process)
        guard !truncatedAfter, shapeAfter == shape, !process.isTerminated,
              CFEqual(window, try focused(application)), CFEqual(group, try element(window, spec.boundary))
        else { throw ProbeError.stale }
        for (path, area, modifiable) in areas {
            guard CFEqual(area, try element(window, path)) else { throw ProbeError.stale }
            try ready(area)
            readStage = .modifiability
            var settable = DarwinBoolean(false)
            guard AXUIElementIsAttributeSettable(area, kAXValueAttribute as CFString, &settable) == .success,
                  settable.boolValue == modifiable else { throw ProbeError.stale }
        }
        readStage = .stability
        let result = try stableSlice(before, snapshot(window, group, areas, spec.boundary))
        guard !process.isTerminated, CFEqual(window, try focused(application)) else { throw ProbeError.stale }
        return result
    }
}
func native(_ job: Job, _ directory: URL) async throws -> [String: Any] {
    try check(job, directory)
    guard AXIsProcessTrusted() else { return ["status": "permission_required", "trusted": false] }
    guard job.app == "messages", let key = job.app, let target = targets[key],
          let resource = Bundle.main.resourceURL?.appendingPathComponent("read-boundary.json"),
          let bytes = try? Data(contentsOf: resource), bytes.count <= 50000 else { throw ProbeError.invalid }
    let spec = try JSONDecoder().decode(BoundarySpec.self, from: bytes)
    let verified = try running(key)
    let result = try Reader(job, directory).candidate(verified, spec)
    return ["status": "ok", "trusted": true, "target_pid": Int(verified.processIdentifier),
            "bundle_id": target.0, "snapshot": result]
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
        if result["status"] as? String != "ok" { result["failure_stage"] = readStage.rawValue }
        result["protocol"] = 2; result["request_id"] = job.request_id
        result["operation"] = job.operation; result["app"] = (job.app as Any?) ?? NSNull()
        result["helper_identity"] = identity; result["helper_pid"] = Int(getpid())
        try writePrivate(result, directory.appendingPathComponent("response.json"))
        _exit(0)
    } catch { _exit(64) } // Never print raw errors, paths or source values.
}

let arguments = Array(CommandLine.arguments.dropFirst())
if arguments.isEmpty || arguments == ["--manifest"] {
    let result: [String: Any] = ["protocol": 2, "identity": identity,
        "operations": ["read_selected"], "access": "read_only",
        "text_reading": true, "qualified_conversation": false, "screenshots": false, "input_actions": false]
    print(String(data: try JSONSerialization.data(withJSONObject: result, options: [.sortedKeys]), encoding: .utf8)!)
} else if arguments == ["--boundary-fixture"] {
    do {
        let data = FileHandle.standardInput.readData(ofLength: 100001)
        guard data.count <= 100000, let object = try JSONSerialization.jsonObject(with: data) as? [String: Any],
              let expected = object["expected"], let current = object["current"] else { throw ProbeError.invalid }
        let spec = try JSONDecoder().decode(BoundarySpec.self, from: JSONSerialization.data(withJSONObject: expected))
        let nodes = try JSONDecoder().decode([Node].self, from: JSONSerialization.data(withJSONObject: current))
        guard shapeMatches(nodes, spec) else { throw ProbeError.invalid }
        print("{\"boundary_matches\":true,\"native_executed\":false}")
    } catch { _exit(64) }
} else if arguments == ["--read-fixture"] {
    do {
        let data = FileHandle.standardInput.readData(ofLength: 100001)
        guard data.count <= 100000,
              let object = try JSONSerialization.jsonObject(with: data) as? [String: Any],
              Set(object.keys) == Set(["before", "after"]),
              let before = object["before"] as? [String: Any], let after = object["after"] as? [String: Any]
        else { throw ProbeError.invalid }
        readStage = .stability
        let result = try stableSlice(before, after)
        print(String(data: try JSONSerialization.data(withJSONObject: result, options: [.sortedKeys]), encoding: .utf8)!)
    } catch { _exit(64) }
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
