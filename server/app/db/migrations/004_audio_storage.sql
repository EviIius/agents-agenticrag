ALTER TABLE attachments ADD COLUMN audio_available INTEGER NOT NULL DEFAULT 1 CHECK (audio_available IN (0,1));
