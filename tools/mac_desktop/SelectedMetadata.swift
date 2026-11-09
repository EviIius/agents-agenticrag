// Compiled after the unchanged ReadOnlySnapshot reader definitions, before its entry point.
// Fixed selected-container metadata only. No body, scripting, database or input operation.
let metadataCaps = ["AXIdentifier": 200, "AXDescription": 1000, "AXHelp": 1000,
                    "AXTitle": 200, "AXRoleDescription": 200, "AXSubrole": 200,
                    "AXDOMIdentifier": 200]
struct MetadataItem: Codable, Equatable {
    let path: [Int]
    let role: String
    let fields: [String: String]
    let custom_content_available: Bool
    let attributed_range_available: Bool
    let url_available: Bool
    let linked_elements_available: Bool
    let selected_available: Bool
}
struct MetadataSlice: Codable, Equatable {
    let access: String
    let qualification: String
    let boundary: [Int]
    let items: [MetadataItem]
}
func metadataPaths(_ paths: [[Int]], _ boundary: [Int]) -> [[Int]] {
    [boundary] + paths.flatMap({ [Array($0.dropLast(2)), Array($0.dropLast()), $0] })
}
func metadataIndices(_ value: Any?) -> Bool {
    guard let values = value as? [NSNumber] else { return false }
    return values.allSatisfy({ number in
        CFGetTypeID(number) != CFBooleanGetTypeID() &&
        !["f", "d"].contains(String(cString: number.objCType)) &&
        number.doubleValue == Double(number.intValue) && (0..<32).contains(number.intValue)
    })
}
func boundedMetadata(_ object: [String: Any]) throws -> MetadataSlice {
    let keys: Set<String> = ["path", "role", "fields", "custom_content_available",
                            "attributed_range_available", "url_available",
                            "linked_elements_available", "selected_available"]
    guard Set(object.keys) == Set(["access", "qualification", "boundary", "items"]),
          metadataIndices(object["boundary"]),
          let items = object["items"] as? [[String: Any]],
          items.allSatisfy({ Set($0.keys) == keys && metadataIndices($0["path"]) &&
              Set(($0["fields"] as? [String: String] ?? [:]).keys) == Set(metadataCaps.keys) })
    else { throw ProbeError.invalid }
    let slice = try JSONDecoder().decode(MetadataSlice.self, from: JSONSerialization.data(withJSONObject: object))
    let boundary = slice.boundary
    let areas = slice.items.filter({ $0.role == "AXTextArea" }).map({ $0.path })
    guard slice.access == "read_only", slice.qualification == "unqualified",
          (1...5).contains(boundary.count), boundary.allSatisfy({ 0 <= $0 && $0 < 32 }),
          (1...8).contains(areas.count), slice.items.count <= 25,
          slice.items.map({ $0.path }) == metadataPaths(areas, boundary),
          Set(slice.items.map({ $0.path })).count == slice.items.count,
          areas.allSatisfy({ $0.count == boundary.count + 3 && $0.starts(with: boundary) && $0.suffix(2) == [0, 0] }),
          slice.items.allSatisfy({ item in
              item.path.allSatisfy({ 0 <= $0 && $0 < 32 }) &&
              (item.role == "AXTextArea" ? item.path.count == boundary.count + 3 :
                item.role == "AXGroup" && (boundary.count...boundary.count + 2).contains(item.path.count)) &&
              item.fields.allSatisfy({ key, value in value.utf8.count <= (metadataCaps[key] ?? -1) })
          }), slice.items.reduce(0, { $0 + $1.fields.values.reduce(0, { $0 + $1.utf8.count }) }) <= 16000
    else { throw ProbeError.invalid }
    return slice
}
extension Reader {
    func knownNames(_ element: AXUIElement, _ parameterized: Bool) throws -> [String] {
        try ready(element)
        var names: CFArray?
        let status = parameterized ? AXUIElementCopyParameterizedAttributeNames(element, &names) :
            AXUIElementCopyAttributeNames(element, &names)
        if status == .attributeUnsupported || status == .noValue { return [] }
        guard status == .success, let values = names as? [String], values.count <= 128 else { throw ProbeError.unavailable }
        return values
    }
    func metadata(_ elements: [([Int], AXUIElement)], _ boundary: [Int]) throws -> [String: Any] {
        readStage = .selection_metadata
        var items: [[String: Any]] = []
        for (path, element) in elements {
            var fields: [String: String] = [:]
            for name in metadataCaps.keys.sorted() {
                fields[name] = try text(element, name, metadataCaps[name]!)
            }
            let attributes = try knownNames(element, false)
            let parameterNames = try knownNames(element, true)
            items.append(["path": path, "role": path.count == boundary.count + 3 ? "AXTextArea" : "AXGroup",
                          "fields": fields,
                          "custom_content_available": attributes.contains("AXCustomContent"),
                          "attributed_range_available": parameterNames.contains("AXAttributedStringForRange"),
                          "url_available": attributes.contains("AXURL"),
                          "linked_elements_available": attributes.contains("AXLinkedUIElements"),
                          "selected_available": attributes.contains("AXSelected")])
        }
        let object: [String: Any] = ["access": "read_only", "qualification": "unqualified",
                                    "boundary": boundary, "items": items]
        _ = try boundedMetadata(object)
        return object
    }
    func selectedMetadata(_ process: NSRunningApplication, _ spec: BoundarySpec) throws -> [String: Any] {
        readStage = .structure
        let (shape, truncated) = try structure(process)
        guard !truncated, let paths = candidatePaths(shape, spec) else { throw ProbeError.stale }
        let application = AXUIElementCreateApplication(process.processIdentifier)
        let window = try focused(application)
        let elements = try metadataPaths(paths, spec.boundary).map({ ($0, try element(window, $0)) })
        let before = try metadata(elements, spec.boundary)
        let (afterShape, afterTruncated) = try structure(process)
        readStage = .stability
        guard !afterTruncated, samePane(shape, afterShape, spec), !process.isTerminated,
              CFEqual(window, try focused(application)) else { throw ProbeError.stale }
        for (path, original) in elements {
            guard CFEqual(original, try element(window, path)) else { throw ProbeError.stale }
        }
        let after = try metadata(elements, spec.boundary)
        readStage = .stability
        guard try boundedMetadata(before) == boundedMetadata(after), !process.isTerminated,
              CFEqual(window, try focused(application)) else { throw ProbeError.stale }
        return before
    }
}
func metadataJob(_ directory: URL) throws -> Job {
    let attributes = try FileManager.default.attributesOfItem(atPath: directory.path)
    guard attributes[.type] as? FileAttributeType == .typeDirectory,
          (attributes[.posixPermissions] as? NSNumber)?.intValue == 0o700,
          (attributes[.ownerAccountID] as? NSNumber)?.uint32Value == getuid(),
          directory.resolvingSymlinksInPath().path == directory.standardizedFileURL.path else { throw ProbeError.invalid }
    let descriptor = Darwin.open(directory.appendingPathComponent("request.json").path, O_RDONLY | O_NOFOLLOW)
    guard descriptor >= 0 else { throw ProbeError.invalid }
    let handle = FileHandle(fileDescriptor: descriptor, closeOnDealloc: true)
    var info = stat()
    guard fstat(descriptor, &info) == 0, info.st_mode & S_IFMT == S_IFREG,
          info.st_mode & 0o777 == 0o600, info.st_uid == getuid(), info.st_size <= 4096 else { throw ProbeError.invalid }
    let bytes = handle.readData(ofLength: 4097)
    guard bytes.count <= 4096,
          let object = try JSONSerialization.jsonObject(with: bytes) as? [String: Any],
          Set(object.keys) == Set(["protocol", "request_id", "operation", "app", "expires_at"]),
          let version = object["protocol"] as? NSNumber, CFGetTypeID(version) != CFBooleanGetTypeID(), version.intValue == 3,
          !["f", "d"].contains(String(cString: version.objCType)),
          version.doubleValue == 3 else { throw ProbeError.invalid }
    let job = try JSONDecoder().decode(Job.self, from: bytes)
    guard job.protocol == 3, job.operation == "inspect_metadata", job.app == "messages",
          job.request_id.range(of: "^[a-f0-9]{32}$", options: .regularExpression) != nil,
          job.expires_at.isFinite, job.expires_at <= Date().timeIntervalSince1970 + 15 else { throw ProbeError.invalid }
    try check(job, directory)
    return job
}
func executeMetadata(_ directory: URL) {
    do {
        let job = try metadataJob(directory)
        try writePrivate(["request_id": job.request_id, "pid": Int(getpid())], directory.appendingPathComponent("helper.json"))
        DispatchQueue.global().asyncAfter(deadline: .now() + min(12, max(0, job.expires_at - Date().timeIntervalSince1970))) { _exit(75) }
        var result: [String: Any]
        do {
            try check(job, directory)
            if !AXIsProcessTrusted() { result = ["status": "permission_required", "trusted": false] }
            else {
                guard let file = Bundle.main.resourceURL?.appendingPathComponent("read-boundary.json") else { throw ProbeError.invalid }
                let bytes = try Data(contentsOf: file)
                guard bytes.count <= 50000 else { throw ProbeError.invalid }
                let spec = try JSONDecoder().decode(BoundarySpec.self, from: bytes)
                let process = try running("messages")
                let snapshot = try Reader(job, directory).selectedMetadata(process, spec)
                result = ["status": "ok", "trusted": true, "target_pid": Int(process.processIdentifier),
                          "bundle_id": "com.apple.MobileSMS", "snapshot": snapshot]
            }
        } catch ProbeError.cancelled { result = ["status": "cancelled"] }
        catch ProbeError.deadline { result = ["status": "deadline"] }
        catch ProbeError.stale { result = ["status": "stale_window"] }
        catch ProbeError.identity { result = ["status": "identity_mismatch"] }
        catch { result = ["status": "unavailable"] }
        if result["status"] as? String != "ok" { result["failure_stage"] = readStage.rawValue }
        result["protocol"] = 3; result["request_id"] = job.request_id
        result["operation"] = job.operation; result["app"] = job.app!
        result["helper_identity"] = identity; result["helper_pid"] = Int(getpid())
        try writePrivate(result, directory.appendingPathComponent("response.json"))
        _exit(0)
    } catch { _exit(64) }
}
let arguments = Array(CommandLine.arguments.dropFirst())
if arguments == ["--manifest"] {
    print("{\"protocol\":3,\"access\":\"read_only\",\"operations\":[\"inspect_metadata\"],\"body_reading\":false,\"qualified_conversation\":false,\"input_actions\":false,\"screenshots\":false}")
} else if arguments == ["--metadata-fixture"] {
    do {
        let data = FileHandle.standardInput.readData(ofLength: 100001)
        guard data.count <= 100000, let object = try JSONSerialization.jsonObject(with: data) as? [String: Any],
              Set(object.keys) == Set(["before", "after"]),
              let first = object["before"] as? [String: Any], let last = object["after"] as? [String: Any],
              try boundedMetadata(first) == boundedMetadata(last) else { throw ProbeError.invalid }
        print("{\"valid\":true,\"native_executed\":false}")
    } catch { _exit(64) }
} else if arguments.count == 2 && arguments[0] == "--validate-job" {
    do { _ = try metadataJob(URL(fileURLWithPath: arguments[1], isDirectory: true)); print("{\"valid\":true,\"native_executed\":false}") }
    catch { _exit(64) }
} else if arguments.count == 2 && arguments[0] == "--native-job" {
    guard Bundle.main.bundleIdentifier == identity else { _exit(64) }
    let directory = URL(fileURLWithPath: arguments[1], isDirectory: true)
    let app = NSApplication.shared
    app.setActivationPolicy(.accessory)
    Task { executeMetadata(directory) }
    app.run()
} else { _exit(64) }
