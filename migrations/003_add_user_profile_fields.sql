-- Migration: 003 Add User Profile Fields
-- Feature: 003-personal-settings-i
-- Date: 2025-10-06
-- Description: Extend user table with profile fields (bio, profile picture, updated_at)

-- Add new columns to user table
ALTER TABLE user ADD COLUMN bio TEXT;
ALTER TABLE user ADD COLUMN profile_picture_data TEXT;
ALTER TABLE user ADD COLUMN profile_picture_mime_type VARCHAR(50);
ALTER TABLE user ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL;

-- Create index on updated_at for efficient concurrent edit detection
CREATE INDEX idx_user_updated_at ON user(updated_at);

-- Create trigger to auto-update updated_at timestamp on any UPDATE
CREATE TRIGGER update_user_timestamp 
AFTER UPDATE ON user
FOR EACH ROW
BEGIN
    UPDATE user SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- ROLLBACK (for manual rollback if needed)
-- DROP TRIGGER IF EXISTS update_user_timestamp;
-- DROP INDEX IF EXISTS idx_user_updated_at;
-- ALTER TABLE user DROP COLUMN updated_at;
-- ALTER TABLE user DROP COLUMN profile_picture_mime_type;
-- ALTER TABLE user DROP COLUMN profile_picture_data;
-- ALTER TABLE user DROP COLUMN bio;
