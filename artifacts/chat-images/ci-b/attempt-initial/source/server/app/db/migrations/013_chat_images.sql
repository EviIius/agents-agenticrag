ALTER TABLE messages ADD COLUMN kind TEXT NOT NULL DEFAULT 'text'
 CHECK(kind IN ('text','image'));
CREATE TABLE message_images (
 message_id TEXT NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
 position INTEGER NOT NULL CHECK(position BETWEEN 0 AND 2),
 job_id TEXT NOT NULL REFERENCES image_jobs(id),
 PRIMARY KEY(message_id,position)
);
CREATE INDEX message_images_job ON message_images(job_id);
-- Origins deliberately outlive deleted chats/messages; outputs belong to Gallery.
CREATE TABLE chat_image_requests (
 request_key TEXT PRIMARY KEY, chat_id TEXT NOT NULL,
 user_id TEXT NOT NULL, assistant_id TEXT NOT NULL, input_json TEXT NOT NULL
);
CREATE TABLE chat_image_origins (
 job_id TEXT PRIMARY KEY REFERENCES image_jobs(id),
 request_key TEXT NOT NULL REFERENCES chat_image_requests(request_key)
);
