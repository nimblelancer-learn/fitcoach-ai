import test from "node:test";
import assert from "node:assert/strict";

import { handleRequest } from "./worker.mjs";

class FakeD1Database {
  constructor() {
    this.generationRuns = new Map();
    this.feedbackRows = [];
  }

  prepare(sql) {
    return {
      bind: (...params) => ({
        run: async () => this.#run(sql, params),
        first: async () => this.#first(sql, params),
      }),
    };
  }

  async #run(sql, params) {
    if (sql.includes("INSERT OR REPLACE INTO generation_runs")) {
      this.generationRuns.set(params[0], {
        request_id: params[0],
        created_at: params[1],
        app_runtime: params[2],
        app_version: params[3],
        request_locale: params[4],
        provider: params[5],
        model: params[6],
        rag_provider: params[7],
        rag_collection: params[8],
        rag_chunk_ids_json: params[9],
        chunk_count: params[10],
        profile_json: params[11],
        workout_plan_json: params[12],
        generation_status: params[13],
        error_code: params[14],
        latency_ms: params[15],
        used_fallback: params[16],
        trace_id: params[17],
        trace_enabled: params[18],
      });
      return { success: true };
    }

    if (sql.includes("INSERT INTO plan_feedback")) {
      this.feedbackRows.push({
        request_id: params[0],
        created_at: params[1],
        usefulness_rating: params[2],
        difficulty_feedback: params[3],
        felt_safe: params[4],
        would_follow_plan: params[5],
        feedback_text: params[6],
        feedback_json: params[7],
        runtime_metadata_json: params[8],
      });
      return { success: true };
    }

    throw new Error(`Unhandled SQL in test stub: ${sql}`);
  }

  async #first(sql, params) {
    if (sql.includes("FROM generation_runs")) {
      return this.generationRuns.get(params[0]) ?? null;
    }

    throw new Error(`Unhandled SQL in test stub: ${sql}`);
  }
}

function createEnv(db) {
  return {
    FITCOACH_DB: db,
    APP_VERSION: "test-worker",
    APP_ENV: "test",
    OPENAI_API_KEY: "test-key",
    OPENAI_MODEL: "gpt-4.1-mini",
    OPENAI_TIMEOUT_MS: "5000",
    LANGFUSE_BASE_URL: "https://cloud.langfuse.com",
    QDRANT_URL: "https://qdrant.example.com",
    QDRANT_COLLECTION: "fitcoach_knowledge",
    RAG_EMBEDDING_PROVIDER: "local-hash",
    RAG_EMBEDDING_DIMENSIONS: "16",
    RAG_RETRIEVAL_LIMIT: "3",
  };
}

function validProfile() {
  return {
    goal: "fat_loss",
    experience_level: "beginner",
    training_days_per_week: 3,
    session_duration_minutes: 45,
    equipment: ["bodyweight", "dumbbells"],
    training_location: "home",
    injuries_or_limitations: ["Occasional knee discomfort"],
    exercise_preferences: ["Strength training", "Low-impact cardio"],
  };
}

function validPlan() {
  return {
    title: "3-Day Beginner Home Strength Plan",
    summary: "A low-impact three-day plan for general fitness and fat loss.",
    goal: "fat_loss",
    experience_level: "beginner",
    training_days_per_week: 3,
    duration_weeks: 4,
    weekly_schedule: [
      {
        day_index: 1,
        title: "Day 1 - Full Body A",
        focus: "Full-body strength",
        estimated_duration_minutes: 45,
        warm_up: ["Walk in place for 5 minutes"],
        exercises: [
          {
            name: "Goblet Squat",
            category: "strength",
            prescription_type: "repetitions",
            sets: 3,
            reps_min: 8,
            reps_max: 10,
            duration_seconds: null,
            rest_seconds: 90,
            intensity: "moderate",
            target_muscles: ["quadriceps", "glutes"],
            instructions: ["Keep your chest tall."],
            safety_notes: ["Use a pain-free range of motion."],
            alternatives: ["Box squat"],
          },
        ],
        cool_down: ["Easy stretching for 5 minutes"],
        intensity_note: "Choose a load that leaves about two reps in reserve.",
      },
      {
        day_index: 3,
        title: "Day 2 - Upper Body",
        focus: "Upper-body strength",
        estimated_duration_minutes: 45,
        warm_up: ["Arm circles for 2 minutes"],
        exercises: [
          {
            name: "Dumbbell Row",
            category: "strength",
            prescription_type: "repetitions",
            sets: 3,
            reps_min: 10,
            reps_max: 12,
            duration_seconds: null,
            rest_seconds: 75,
            intensity: "moderate",
            target_muscles: ["back", "biceps"],
            instructions: ["Keep the spine neutral."],
            safety_notes: [],
            alternatives: ["Resistance band row"],
          },
        ],
        cool_down: ["Gentle shoulder stretches"],
        intensity_note: "Use a controlled tempo.",
      },
      {
        day_index: 5,
        title: "Day 3 - Conditioning",
        focus: "Low-impact conditioning",
        estimated_duration_minutes: 40,
        warm_up: ["March in place for 3 minutes"],
        exercises: [
          {
            name: "Brisk Walk",
            category: "cardio",
            prescription_type: "duration",
            sets: 1,
            reps_min: null,
            reps_max: null,
            duration_seconds: 1200,
            rest_seconds: null,
            intensity: "low",
            target_muscles: ["cardiovascular system"],
            instructions: ["Maintain a pace that allows conversation."],
            safety_notes: [],
            alternatives: [],
          },
        ],
        cool_down: ["Easy walking for 5 minutes"],
        intensity_note: "Stay below breathless effort.",
      },
    ],
    progression_suggestion:
      "When all sets feel comfortable with good form, add one repetition per set before increasing load.",
    safety_warnings: [
      {
        code: "form_priority",
        severity: "caution",
        message: "Keep controlled form; stop if sharp pain occurs.",
        recommended_action: "Reduce range of motion or choose the listed alternative.",
        applies_to_exercise: null,
        requires_professional_clearance: false,
      },
    ],
  };
}

test("POST /api/workout-plans returns a plan, preserves request ID, and writes generation metadata", async () => {
  const db = new FakeD1Database();
  const env = createEnv(db);
  env.LANGFUSE_PUBLIC_KEY = "pk-test";
  env.LANGFUSE_SECRET_KEY = "sk-test";
  const originalFetch = globalThis.fetch;
  const waitUntilPromises = [];
  globalThis.fetch = async (url) => {
    if (String(url).includes("/points/query")) {
      return Response.json({
        result: [
          {
            payload: {
              chunk_id: "doc-1::chunk-000",
              document_id: "doc-1",
              title: "Warm-up basics",
              topic: "warmup",
              text: "Start with 5 minutes of easy movement.",
            },
          },
        ],
      });
    }

    if (String(url) === "https://api.openai.com/v1/responses") {
      return Response.json({
        usage: {
          input_tokens: 123,
          output_tokens: 456,
          total_tokens: 579,
        },
        output_text: JSON.stringify(validPlan()),
      });
    }

    if (String(url) === "https://cloud.langfuse.com/api/public/ingestion") {
      return Response.json({ success: true });
    }

    throw new Error(`Unexpected fetch URL: ${url}`);
  };

  try {
    const response = await handleRequest(
      new Request("https://example.com/api/workout-plans", {
        method: "POST",
        headers: {
          "content-type": "application/json",
          "X-Request-ID": "req-test-123",
          "Accept-Language": "en-US,en;q=0.9",
        },
        body: JSON.stringify(validProfile()),
      }),
      env,
      {
        waitUntil(promise) {
          waitUntilPromises.push(promise);
        },
      },
    );

    assert.equal(response.status, 200);
    assert.equal(response.headers.get("X-Request-ID"), "req-test-123");
    assert.equal(response.headers.get("X-RAG-Chunk-Count"), "1");
    assert.equal(response.headers.get("X-RAG-Chunk-Ids"), "doc-1::chunk-000");

    const body = await response.json();
    assert.equal(body.title, "3-Day Beginner Home Strength Plan");

    const storedRun = db.generationRuns.get("req-test-123");
    assert.ok(storedRun);
    assert.equal(storedRun.request_locale, "en-US");
    assert.equal(storedRun.chunk_count, 1);
    assert.equal(storedRun.used_fallback, 0);
    assert.equal(storedRun.trace_id, "req-test-123");
    assert.equal(storedRun.trace_enabled, 1);
    await Promise.all(waitUntilPromises);
  } finally {
    globalThis.fetch = originalFetch;
  }
});

test("POST /api/feedback persists feedback against the stored generation run", async () => {
  const db = new FakeD1Database();
  const env = createEnv(db);
  db.generationRuns.set("req-test-123", {
    request_id: "req-test-123",
    rag_chunk_ids_json: JSON.stringify(["doc-1::chunk-000"]),
    chunk_count: 1,
    latency_ms: 231,
    used_fallback: 0,
    model: "gpt-4.1-mini",
    trace_id: "req-test-123",
    trace_enabled: 1,
  });

  const response = await handleRequest(
    new Request("https://example.com/api/feedback", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "X-Request-ID": "feedback-save-1",
      },
      body: JSON.stringify({
        request_id: "req-test-123",
        profile: validProfile(),
        generated_plan: validPlan(),
        feedback: {
          usefulness_rating: 5,
          difficulty_feedback: "about_right",
          felt_safe: true,
          would_follow_plan: true,
          feedback_text: "The plan felt realistic and easy to follow.",
        },
      }),
    }),
    env,
    {},
  );

  assert.equal(response.status, 201);
  const body = await response.json();
  assert.equal(body.request_id, "req-test-123");
  assert.equal(db.feedbackRows.length, 1);
  assert.equal(db.feedbackRows[0].request_id, "req-test-123");

  const metadata = JSON.parse(db.feedbackRows[0].runtime_metadata_json);
  assert.equal(metadata.saved_request_id, "feedback-save-1");
  assert.equal(metadata.chunk_count, 1);
  assert.equal(metadata.model_name, "gpt-4.1-mini");
  assert.equal(metadata.trace_id, "req-test-123");
  assert.equal(metadata.trace_enabled, true);
  assert.equal(metadata.langfuse_host, "https://cloud.langfuse.com");
});

test("POST /api/workout-plans still succeeds when Langfuse is not configured", async () => {
  const db = new FakeD1Database();
  const env = createEnv(db);
  const originalFetch = globalThis.fetch;
  globalThis.fetch = async (url) => {
    if (String(url).includes("/points/query")) {
      return Response.json({ result: [] });
    }
    if (String(url) === "https://api.openai.com/v1/responses") {
      return Response.json({
        output_text: JSON.stringify(validPlan()),
      });
    }
    throw new Error(`Unexpected fetch URL: ${url}`);
  };

  try {
    const response = await handleRequest(
      new Request("https://example.com/api/workout-plans", {
        method: "POST",
        headers: {
          "content-type": "application/json",
          "X-Request-ID": "req-no-langfuse",
        },
        body: JSON.stringify(validProfile()),
      }),
      env,
      {},
    );

    assert.equal(response.status, 200);
    const storedRun = db.generationRuns.get("req-no-langfuse");
    assert.ok(storedRun);
    assert.equal(storedRun.trace_id, null);
    assert.equal(storedRun.trace_enabled, 0);
  } finally {
    globalThis.fetch = originalFetch;
  }
});

test("POST /api/workout-plans rejects duplicate equipment values", async () => {
  const db = new FakeD1Database();
  const env = createEnv(db);

  const response = await handleRequest(
    new Request("https://example.com/api/workout-plans", {
      method: "POST",
      headers: {
        "content-type": "application/json",
      },
      body: JSON.stringify({
        ...validProfile(),
        equipment: ["bodyweight", "Bodyweight"],
      }),
    }),
    env,
    {},
  );

  assert.equal(response.status, 422);
  const body = await response.json();
  assert.equal(body.error.code, "REQUEST_VALIDATION_ERROR");
  assert.deepEqual(body.error.details, [
    {
      field: "equipment",
      message: "must not contain duplicates",
    },
  ]);
});

test("POST /api/feedback rejects invalid boolean fields", async () => {
  const db = new FakeD1Database();
  const env = createEnv(db);
  db.generationRuns.set("req-test-123", {
    request_id: "req-test-123",
    rag_chunk_ids_json: JSON.stringify(["doc-1::chunk-000"]),
    chunk_count: 1,
    latency_ms: 231,
    used_fallback: 0,
    model: "gpt-4.1-mini",
    trace_id: "req-test-123",
    trace_enabled: 1,
  });

  const response = await handleRequest(
    new Request("https://example.com/api/feedback", {
      method: "POST",
      headers: {
        "content-type": "application/json",
      },
      body: JSON.stringify({
        request_id: "req-test-123",
        profile: validProfile(),
        generated_plan: validPlan(),
        feedback: {
          usefulness_rating: 5,
          difficulty_feedback: "about_right",
          felt_safe: "true",
          would_follow_plan: true,
          feedback_text: "Looks good",
        },
      }),
    }),
    env,
    {},
  );

  assert.equal(response.status, 422);
  const body = await response.json();
  assert.equal(body.error.code, "REQUEST_VALIDATION_ERROR");
  assert.deepEqual(body.error.details, [
    {
      field: "felt_safe",
      message: "must be a boolean",
    },
  ]);
});

test("POST /api/workout-plans fails open when Langfuse ingestion errors", async () => {
  const db = new FakeD1Database();
  const env = createEnv(db);
  env.LANGFUSE_PUBLIC_KEY = "pk-test";
  env.LANGFUSE_SECRET_KEY = "sk-test";
  const originalFetch = globalThis.fetch;
  const waitUntilPromises = [];
  globalThis.fetch = async (url) => {
    if (String(url).includes("/points/query")) {
      return Response.json({ result: [] });
    }
    if (String(url) === "https://api.openai.com/v1/responses") {
      return Response.json({
        output_text: JSON.stringify(validPlan()),
      });
    }
    if (String(url) === "https://cloud.langfuse.com/api/public/ingestion") {
      throw new Error("langfuse outage");
    }
    throw new Error(`Unexpected fetch URL: ${url}`);
  };

  try {
    const response = await handleRequest(
      new Request("https://example.com/api/workout-plans", {
        method: "POST",
        headers: {
          "content-type": "application/json",
          "X-Request-ID": "req-langfuse-outage",
        },
        body: JSON.stringify(validProfile()),
      }),
      env,
      {
        waitUntil(promise) {
          waitUntilPromises.push(promise);
        },
      },
    );

    assert.equal(response.status, 200);
    await Promise.all(waitUntilPromises);
    const storedRun = db.generationRuns.get("req-langfuse-outage");
    assert.ok(storedRun);
    assert.equal(storedRun.trace_id, "req-langfuse-outage");
    assert.equal(storedRun.trace_enabled, 1);
  } finally {
    globalThis.fetch = originalFetch;
  }
});
