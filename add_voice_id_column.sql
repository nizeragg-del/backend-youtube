-- SQL script to add the voice_id column to the user_configs table in Supabase.
ALTER TABLE user_configs ADD COLUMN IF NOT EXISTS voice_id TEXT DEFAULT 'tc_5f8d7b0de146f10007b8042f';
