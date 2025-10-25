CREATE TABLE IF NOT EXISTS results_api_keys (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  key_sha256 TEXT NOT NULL,      -- hex lowercase
  is_active INTEGER NOT NULL DEFAULT 1,
  last_used_at TIMESTAMP NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
