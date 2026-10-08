"""Reproduce the synthetic Phase 3 migration fixture, without reading app data."""

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "server/tests/fixtures/db/phase3.db"


def generate(destination: Path = DESTINATION) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        destination.unlink()
    with sqlite3.connect(destination) as db:
        db.execute("PRAGMA foreign_keys=ON")
        for migration in sorted((ROOT / "server/app/db/migrations").glob("*.sql")):
            number = int(migration.name.split("_")[0])
            if number > 4:
                break
            db.executescript(migration.read_text())
            db.execute(f"PRAGMA user_version={number}")
        db.execute(
            "INSERT INTO connections(id,kind,name,base_url,created_at,updated_at) VALUES('fake-connection','ollama','Synthetic runtime','http://127.0.0.1:18080','2026-10-03','2026-10-03')"
        )
        db.execute(
            "INSERT INTO model_prefs(connection_id,model_id,context_length) VALUES('fake-connection','fake-chat',16384)"
        )
        for chat in ("fake-branches", "fake-web", "fake-recording", "fake-import"):
            db.execute(
                "INSERT INTO chats(id,title,connection_id,model_id,created_at,updated_at) VALUES(?,?,'fake-connection','fake-chat','2026-10-03','2026-10-03')",
                (chat, "Synthetic " + chat),
            )
        rows = [
            ("fake-user", "fake-branches", None, "user", "Synthetic question"),
            ("fake-answer", "fake-branches", "fake-user", "assistant", "Synthetic answer"),
            (
                "fake-sibling",
                "fake-branches",
                "fake-user",
                "assistant",
                "Synthetic alternate answer",
            ),
            ("fake-web-answer", "fake-web", None, "assistant", "Synthetic cited answer [1]."),
            (
                "fake-audio-user",
                "fake-recording",
                None,
                "user",
                "Summarize the synthetic recording.",
            ),
            ("fake-import-user", "fake-import", None, "user", "Synthetic imported message"),
        ]
        for id, chat, parent, role, content in rows:
            db.execute(
                "INSERT INTO messages(id,chat_id,parent_id,role,content,created_at,updated_at) VALUES(?,?,?,?,?,'2026-10-03','2026-10-03')",
                (id, chat, parent, role, content),
            )
            db.execute("UPDATE chats SET current_leaf_id=? WHERE id=?", (id, chat))
            db.execute(
                "INSERT INTO chat_search(chat_id,message_id,title,content) VALUES(?,?,?,?)",
                (chat, id, "Synthetic " + chat, content),
            )
        db.execute(
            "INSERT INTO message_sources(message_id,n,url,title,site_name,passages_json,cited) VALUES('fake-web-answer',1,'https://example.org/fake','Synthetic source','Example','[{\"text\":\"Synthetic evidence\"}]',1)"
        )
        db.execute(
            "INSERT INTO web_reads(message_id,url,title,status) VALUES('fake-web-answer','https://example.org/fake','Synthetic source','used')"
        )
        db.execute(
            "INSERT INTO attachments(id,message_id,kind,filename,mime_type,bytes,path,created_at,audio_available) VALUES('fake-audio','fake-audio-user','audio','fake-recording.wav','audio/wav',64,'attachments/fake-audio.wav','2026-10-03',0)"
        )
        db.execute(
            "INSERT INTO transcripts(attachment_id,status,text,raw_text,segments_json,meta_json,created_at,updated_at) VALUES('fake-audio','ready','Synthetic transcript.','Synthetic transcript.','[{\"start\":0,\"end\":1,\"text\":\"Synthetic transcript.\"}]','{}','2026-10-03','2026-10-03')"
        )
        db.execute(
            "INSERT INTO legacy_imports(legacy_id,chat_id) VALUES('fake-legacy','fake-import')"
        )
        db.execute("INSERT INTO settings(key,value_json) VALUES('auto_title','false')")
        db.commit()
    destination.chmod(0o600)


if __name__ == "__main__":
    generate()
    print("Synthetic Phase 3 database generated.")
