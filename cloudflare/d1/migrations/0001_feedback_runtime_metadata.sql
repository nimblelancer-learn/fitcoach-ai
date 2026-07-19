CREATE TABLE IF NOT EXISTS generation_runs (
    request_id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    app_runtime TEXT NOT NULL,
    app_version TEXT,
    request_locale TEXT,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    rag_provider TEXT,
    rag_collection TEXT,
    rag_chunk_ids_json TEXT NOT NULL,
    chunk_count INTEGER NOT NULL DEFAULT 0,
    profile_json TEXT NOT NULL,
    workout_plan_json TEXT NOT NULL,
    generation_status TEXT NOT NULL,
    error_code TEXT,
    latency_ms INTEGER,
    used_fallback INTEGER NOT NULL DEFAULT 0,
    trace_id TEXT,
    trace_enabled INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_generation_runs_created_at
    ON generation_runs(created_at DESC);

CREATE TABLE IF NOT EXISTS plan_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    usefulness_rating INTEGER NOT NULL,
    difficulty_feedback TEXT NOT NULL,
    felt_safe INTEGER NOT NULL,
    would_follow_plan INTEGER NOT NULL,
    feedback_text TEXT,
    feedback_channel TEXT NOT NULL DEFAULT 'public_mvp',
    feedback_json TEXT NOT NULL,
    runtime_metadata_json TEXT NOT NULL DEFAULT '{}',
    FOREIGN KEY (request_id) REFERENCES generation_runs(request_id)
);

CREATE INDEX IF NOT EXISTS idx_plan_feedback_request_id
    ON plan_feedback(request_id);

CREATE INDEX IF NOT EXISTS idx_plan_feedback_created_at
    ON plan_feedback(created_at DESC);
