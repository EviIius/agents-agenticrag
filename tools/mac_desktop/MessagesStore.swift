// Host-authored read-only store core. Native and invented-database fixtures share this code.
import Foundation
import SQLite3
import Darwin

enum StoreFailure: String, Error {
    case invalid, permission_required, unavailable, unsupported_schema, unsupported_message
    case ambiguous_recipient, no_conversation, stale_selection, deadline, cancelled
}
struct StoreTarget: Codable, Equatable {
    let chat_guid: String
    let address: String
    let service: String
    let handle_row_id: Int64
}
struct StoreMessage: Codable, Equatable {
    let guid: String
    let row_id: Int64
    let from_me: Bool
    let sender_handle: String
    let date: Int64
    let text: String
}
struct StoreSlice: Codable, Equatable {
    let access: String
    let qualification: String
    let target: StoreTarget
    let messages: [StoreMessage] // native order: newest first, date then native row ID
    let latest_incoming_guid: String?
    enum CodingKeys: String, CodingKey { case access, qualification, target, messages, latest_incoming_guid }
    func encode(to encoder: Encoder) throws {
        var result = encoder.container(keyedBy: CodingKeys.self)
        try result.encode(access, forKey: .access)
        try result.encode(qualification, forKey: .qualification)
        try result.encode(target, forKey: .target)
        try result.encode(messages, forKey: .messages)
        if let latest_incoming_guid { try result.encode(latest_incoming_guid, forKey: .latest_incoming_guid) }
        else { try result.encodeNil(forKey: .latest_incoming_guid) }
    }
}
func exactAddress(_ text: String) -> Bool {
    guard text.utf8.count <= 200 else { return false }
    let patterns = ["^\\+[1-9][0-9]{6,14}$", "^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?\\.[A-Za-z]{2,63}$"]
    return patterns.contains(where: { text.range(of: $0, options: .regularExpression) == text.startIndex..<text.endIndex })
}
final class StoreBudget {
    let deadline: TimeInterval
    let cancel: URL?
    init(_ seconds: Double = 3, cancel: URL? = nil) {
        deadline = ProcessInfo.processInfo.systemUptime + seconds
        self.cancel = cancel
    }
    func check() throws {
        if let cancel, FileManager.default.fileExists(atPath: cancel.path) { throw StoreFailure.cancelled }
        if ProcessInfo.processInfo.systemUptime >= deadline { throw StoreFailure.deadline }
    }
}
let storeTables: Set<String> = ["chat", "handle", "chat_handle_join", "chat_message_join", "message",
                                "message_attachment_join", "chat_recoverable_message_join", "sqlite_master", "sqlite_schema"]
func storeAuthorize(_ context: UnsafeMutableRawPointer?, _ action: Int32, _ first: UnsafePointer<CChar>?, _ second: UnsafePointer<CChar>?, _ database: UnsafePointer<CChar>?, _ trigger: UnsafePointer<CChar>?) -> Int32 {
    if trigger != nil { return SQLITE_DENY }
    switch action {
    case SQLITE_SELECT, SQLITE_TRANSACTION: return SQLITE_OK
    case SQLITE_READ:
        guard let first, let database, String(cString: database) == "main",
              storeTables.contains(String(cString: first)) else { return SQLITE_DENY }
        return SQLITE_OK
    case SQLITE_FUNCTION:
        guard let second, ["count", "coalesce"].contains(String(cString: second).lowercased()) else { return SQLITE_DENY }
        return SQLITE_OK
    case SQLITE_PRAGMA:
        guard let first, let second, String(cString: first).lowercased() == "table_info",
              storeTables.contains(String(cString: second)) else { return SQLITE_DENY }
        return SQLITE_OK
    default: return SQLITE_DENY
    }
}
final class MessagesStore {
    let db: OpaquePointer
    let budget: StoreBudget
    init(path: String, budget: StoreBudget) throws {
        self.budget = budget
        try budget.check()
        var database: OpaquePointer?
        let flags = SQLITE_OPEN_READONLY | SQLITE_OPEN_NOFOLLOW | SQLITE_OPEN_PRIVATECACHE
        let status = sqlite3_open_v2(path, &database, flags, nil)
        guard status == SQLITE_OK, let database else {
            if let database { sqlite3_close(database) }
            // This status is deliberately generic: no path/system error enters output.
            throw StoreFailure.permission_required
        }
        var owned = true
        defer { if owned { sqlite3_close(database) } }
        guard sqlite3_db_readonly(database, "main") == 1 else { throw StoreFailure.unavailable }
        // Apple's SDK omits the extension-enabling API; never enable it.
        // The authorizer below also rejects SQL extension loading.
        sqlite3_limit(database, SQLITE_LIMIT_LENGTH, 100_000)
        sqlite3_limit(database, SQLITE_LIMIT_SQL_LENGTH, 16_000)
        sqlite3_limit(database, SQLITE_LIMIT_ATTACHED, 0)
        sqlite3_busy_timeout(database, 250)
        guard sqlite3_exec(database, "PRAGMA query_only=ON; PRAGMA trusted_schema=OFF;", nil, nil, nil) == SQLITE_OK else {
            throw StoreFailure.unavailable
        }
        sqlite3_set_authorizer(database, storeAuthorize, nil)
        sqlite3_progress_handler(database, 1000, { pointer in
            guard let pointer else { return 1 }
            let budget = Unmanaged<StoreBudget>.fromOpaque(pointer).takeUnretainedValue()
            do { try budget.check(); return 0 } catch { return 1 }
        }, Unmanaged.passUnretained(budget).toOpaque())
        db = database
        owned = false
    }
    deinit { sqlite3_progress_handler(db, 0, nil, nil); sqlite3_close(db) }
    func statement<T>(_ sql: String, _ arguments: [String] = [], _ body: (OpaquePointer) throws -> T) throws -> T {
        try budget.check()
        var raw: OpaquePointer?
        guard sqlite3_prepare_v2(db, sql, -1, &raw, nil) == SQLITE_OK, let raw else {
            try budget.check(); throw StoreFailure.unsupported_schema
        }
        defer { sqlite3_finalize(raw) }
        guard sqlite3_bind_parameter_count(raw) == Int32(arguments.count) else { throw StoreFailure.invalid }
        for (offset, value) in arguments.enumerated() {
            guard value.withCString({ sqlite3_bind_text(raw, Int32(offset + 1), $0, -1, unsafeBitCast(-1, to: sqlite3_destructor_type.self)) }) == SQLITE_OK else { throw StoreFailure.unavailable }
        }
        return try body(raw)
    }
    func step(_ statement: OpaquePointer) throws -> Bool {
        try budget.check()
        switch sqlite3_step(statement) {
        case SQLITE_ROW: return true
        case SQLITE_DONE: return false
        default: try budget.check(); throw StoreFailure.unavailable
        }
    }
    func text(_ statement: OpaquePointer, _ column: Int32, _ maximum: Int, optional: Bool = false) throws -> String {
        if optional && sqlite3_column_type(statement, column) == SQLITE_NULL { return "" }
        guard sqlite3_column_type(statement, column) == SQLITE_TEXT else { throw StoreFailure.unsupported_message }
        let count = Int(sqlite3_column_bytes(statement, column))
        guard count >= 0, count <= maximum, let bytes = sqlite3_column_text(statement, column),
              let text = String(bytes: UnsafeBufferPointer(start: bytes, count: count), encoding: .utf8),
              !text.contains("\0") else { throw StoreFailure.unsupported_message }
        return text
    }
    func integer(_ statement: OpaquePointer, _ column: Int32) throws -> Int64 {
        guard sqlite3_column_type(statement, column) == SQLITE_INTEGER else { throw StoreFailure.unsupported_message }
        return sqlite3_column_int64(statement, column)
    }
    func schema(_ required: [String: Set<String>]) throws {
        for (table, columns) in required {
            guard storeTables.contains(table) else { throw StoreFailure.invalid }
            let realTable = try statement("SELECT type FROM sqlite_schema WHERE name=? LIMIT 2", [table]) { raw in
                guard try step(raw), try text(raw, 0, 20) == "table", try !step(raw) else { throw StoreFailure.unsupported_schema }
                return true
            }
            guard realTable else { throw StoreFailure.unsupported_schema }
            var found = Set<String>()
            try statement("PRAGMA table_info(\(table))") { raw in
                var count = 0
                while try step(raw) {
                    count += 1
                    guard count <= 256 else { throw StoreFailure.unsupported_schema }
                    found.insert(try text(raw, 1, 200))
                }
            }
            guard columns.isSubset(of: found) else { throw StoreFailure.unsupported_schema }
        }
    }
    func transaction<T>(_ body: () throws -> T) throws -> T {
        guard sqlite3_exec(db, "BEGIN", nil, nil, nil) == SQLITE_OK else { throw StoreFailure.unavailable }
        defer { sqlite3_exec(db, "ROLLBACK", nil, nil, nil) }
        let value = try body()
        guard sqlite3_exec(db, "COMMIT", nil, nil, nil) == SQLITE_OK else { throw StoreFailure.unavailable }
        return value
    }
    func resolve(_ address: String) throws -> StoreTarget {
        guard exactAddress(address) else { throw StoreFailure.invalid }
        try schema(["chat": ["guid", "chat_identifier", "style", "service_name"],
                    "handle": ["id", "service"], "chat_handle_join": ["chat_id", "handle_id"]])
        var targets: [StoreTarget] = []
        try statement("""
            SELECT DISTINCT c.guid, c.chat_identifier, c.style, c.service_name, h.ROWID, h.id, h.service,
              (SELECT COUNT(*) FROM chat_handle_join x WHERE x.chat_id=c.ROWID)
            FROM chat c JOIN chat_handle_join j ON j.chat_id=c.ROWID JOIN handle h ON h.ROWID=j.handle_id
            WHERE h.id=? COLLATE BINARY AND c.chat_identifier=h.id COLLATE BINARY
              AND c.style=45 AND (SELECT COUNT(*) FROM chat_handle_join x WHERE x.chat_id=c.ROWID)=1
            LIMIT 2
            """, [address]) { raw in
            while try step(raw) {
                let guid = try text(raw, 0, 200)
                let identifier = try text(raw, 1, 200)
                let style = try integer(raw, 2)
                let service = try text(raw, 3, 30)
                let handle = try integer(raw, 4)
                guard !guid.isEmpty, identifier == address, style == 45,
                      ["iMessage", "SMS", "RCS"].contains(service), handle > 0,
                      try text(raw, 5, 200) == address, try text(raw, 6, 30) == service,
                      try integer(raw, 7) == 1 else { throw StoreFailure.ambiguous_recipient }
                targets.append(StoreTarget(chat_guid: guid, address: address, service: service, handle_row_id: handle))
            }
        }
        guard targets.count == 1 else { throw targets.isEmpty ? StoreFailure.no_conversation : StoreFailure.ambiguous_recipient }
        return targets[0]
    }
    func read(_ target: StoreTarget) throws -> StoreSlice {
        try transaction {
            guard try resolve(target.address) == target else { throw StoreFailure.stale_selection }
            try schema([
                "message": ["guid", "text", "handle_id", "is_from_me", "date", "service", "item_type", "group_action_type", "associated_message_guid", "associated_message_type", "cache_has_attachments", "message_summary_info", "date_edited"],
                "chat_message_join": ["chat_id", "message_id"],
                "message_attachment_join": ["message_id", "attachment_id"],
                "chat_recoverable_message_join": ["chat_id", "message_id"]
            ])
            var messages: [StoreMessage] = []
            try statement("""
                SELECT m.guid, m.ROWID, m.is_from_me, h.id, m.date, m.text, m.service,
                  m.item_type, m.group_action_type, m.associated_message_guid, m.associated_message_type,
                  m.cache_has_attachments, m.message_summary_info IS NOT NULL, m.date_edited,
                  (SELECT COUNT(*) FROM message_attachment_join a WHERE a.message_id=m.ROWID),
                  (SELECT COUNT(*) FROM chat_recoverable_message_join d WHERE d.message_id=m.ROWID)
                FROM chat c JOIN chat_message_join j ON j.chat_id=c.ROWID JOIN message m ON m.ROWID=j.message_id
                  LEFT JOIN handle h ON h.ROWID=m.handle_id
                WHERE c.guid=? COLLATE BINARY ORDER BY m.date DESC, m.ROWID DESC LIMIT 8
                """, [target.chat_guid]) { raw in
                while try step(raw) {
                    let guid = try text(raw, 0, 200)
                    let row = try integer(raw, 1)
                    let from = try integer(raw, 2)
                    let sender = try text(raw, 3, 200, optional: true)
                    let date = try integer(raw, 4)
                    let body = try text(raw, 5, 4000)
                    guard !guid.isEmpty, row > 0, [0, 1].contains(from), date > 0,
                          !body.isEmpty, !body.contains("\u{FFFC}"),
                          from == 1 || sender == target.address,
                          try text(raw, 6, 30) == target.service,
                          try integer(raw, 7) == 0, try integer(raw, 8) == 0,
                          try text(raw, 9, 200, optional: true).isEmpty else { throw StoreFailure.unsupported_message }
                    for column: Int32 in [10, 11, 12, 13, 14, 15] {
                        guard try integer(raw, column) == 0 else { throw StoreFailure.unsupported_message }
                    }
                    messages.append(StoreMessage(guid: guid, row_id: row, from_me: from == 1, sender_handle: sender, date: date, text: body))
                }
            }
            guard !messages.isEmpty, Set(messages.map({ $0.guid })).count == messages.count,
                  Set(messages.map({ $0.row_id })).count == messages.count,
                  messages.reduce(0, { $0 + $1.text.utf8.count }) <= 16000 else { throw StoreFailure.unsupported_message }
            return StoreSlice(access: "read_only", qualification: "unqualified", target: target,
                              messages: messages, latest_incoming_guid: messages.first(where: { !$0.from_me })?.guid)
        }
    }
}
