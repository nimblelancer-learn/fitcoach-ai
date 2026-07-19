SELECT
    pf.id AS feedback_id,
    pf.request_id,
    pf.created_at AS feedback_created_at,
    pf.feedback_channel,
    pf.usefulness_rating,
    pf.difficulty_feedback,
    pf.felt_safe,
    pf.would_follow_plan,
    pf.feedback_text,
    gr.created_at AS generated_at,
    gr.model AS model_name,
    gr.latency_ms,
    gr.used_fallback,
    gr.chunk_count AS retrieved_chunk_count,
    gr.rag_chunk_ids_json AS retrieved_chunk_ids_json,
    json_extract(pf.runtime_metadata_json, '$.safety_trigger_codes') AS safety_trigger_codes_json,
    gr.trace_id,
    gr.trace_enabled
FROM plan_feedback pf
LEFT JOIN generation_runs gr ON gr.request_id = pf.request_id
WHERE pf.feedback_channel = 'public_mvp'
ORDER BY pf.created_at DESC;
