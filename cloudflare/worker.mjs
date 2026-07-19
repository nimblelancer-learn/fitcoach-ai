import { getLangfuseConfig, submitLangfuseTrace } from "./langfuse.mjs";

const FITNESS_GOALS = new Set([
  "fat_loss",
  "muscle_gain",
  "general_fitness",
  "endurance",
]);

const EXPERIENCE_LEVELS = new Set(["beginner", "intermediate"]);
const TRAINING_LOCATIONS = new Set(["home", "gym", "outdoors", "mixed"]);
const EQUIPMENT_OPTIONS = new Set([
  "bodyweight",
  "dumbbells",
  "resistance_bands",
  "kettlebell",
  "barbell",
  "machines",
  "full_gym",
]);
const DIFFICULTY_FEEDBACK = new Set(["too_easy", "about_right", "too_hard"]);
const MEDICAL_TRIGGER_PATTERNS = [
  "chest pain",
  "fainting",
  "near-fainting",
  "severe dizziness",
  "sudden severe shortness of breath",
  "rehab",
  "rehabilitation",
  "physical therapy",
  "post-surgery",
  "post surgery",
  "fracture",
  "dislocation",
  "diagnosed",
  "torn acl",
];
const TOKEN_PATTERN = /[a-z0-9]+/g;
const DEFAULT_TIMEOUT_MS = 20_000;

const WORKOUT_PLAN_JSON_SCHEMA = {
  type: "object",
  additionalProperties: false,
  required: [
    "title",
    "summary",
    "goal",
    "experience_level",
    "training_days_per_week",
    "duration_weeks",
    "weekly_schedule",
    "progression_suggestion",
    "safety_warnings",
  ],
  properties: {
    title: { type: "string", minLength: 1, maxLength: 120 },
    summary: { type: "string", minLength: 1, maxLength: 500 },
    goal: { type: "string", enum: [...FITNESS_GOALS] },
    experience_level: { type: "string", enum: [...EXPERIENCE_LEVELS] },
    training_days_per_week: { type: "integer", minimum: 1, maximum: 7 },
    duration_weeks: { type: "integer", minimum: 1, maximum: 12 },
    weekly_schedule: {
      type: "array",
      minItems: 1,
      maxItems: 7,
      items: {
        type: "object",
        additionalProperties: false,
        required: [
          "day_index",
          "title",
          "focus",
          "estimated_duration_minutes",
          "warm_up",
          "exercises",
          "cool_down",
          "intensity_note",
        ],
        properties: {
          day_index: { type: "integer", minimum: 1, maximum: 7 },
          title: { type: "string", minLength: 1, maxLength: 120 },
          focus: { type: "string", minLength: 1, maxLength: 200 },
          estimated_duration_minutes: {
            type: "integer",
            minimum: 15,
            maximum: 180,
          },
          warm_up: {
            type: "array",
            minItems: 1,
            maxItems: 5,
            items: { type: "string", minLength: 1, maxLength: 200 },
          },
          exercises: {
            type: "array",
            minItems: 1,
            maxItems: 12,
            items: {
              type: "object",
              additionalProperties: false,
              required: [
                "name",
                "category",
                "prescription_type",
                "sets",
                "reps_min",
                "reps_max",
                "duration_seconds",
                "rest_seconds",
                "intensity",
                "target_muscles",
                "instructions",
                "safety_notes",
                "alternatives",
              ],
              properties: {
                name: { type: "string", minLength: 1, maxLength: 120 },
                category: { type: "string", enum: ["strength", "cardio", "mobility"] },
                prescription_type: { type: "string", enum: ["repetitions", "duration"] },
                sets: { type: "integer", minimum: 1, maximum: 8 },
                reps_min: { type: ["integer", "null"], minimum: 1, maximum: 100 },
                reps_max: { type: ["integer", "null"], minimum: 1, maximum: 100 },
                duration_seconds: {
                  type: ["integer", "null"],
                  minimum: 15,
                  maximum: 3600,
                },
                rest_seconds: { type: ["integer", "null"], minimum: 0, maximum: 600 },
                intensity: { type: "string", enum: ["low", "moderate", "high"] },
                target_muscles: {
                  type: "array",
                  minItems: 1,
                  maxItems: 6,
                  items: { type: "string", minLength: 1, maxLength: 200 },
                },
                instructions: {
                  type: "array",
                  minItems: 1,
                  maxItems: 6,
                  items: { type: "string", minLength: 1, maxLength: 200 },
                },
                safety_notes: {
                  type: "array",
                  maxItems: 5,
                  items: { type: "string", minLength: 1, maxLength: 200 },
                },
                alternatives: {
                  type: "array",
                  maxItems: 3,
                  items: { type: "string", minLength: 1, maxLength: 200 },
                },
              },
            },
          },
          cool_down: {
            type: "array",
            minItems: 1,
            maxItems: 5,
            items: { type: "string", minLength: 1, maxLength: 200 },
          },
          intensity_note: { type: "string", minLength: 1, maxLength: 240 },
        },
      },
    },
    progression_suggestion: { type: "string", minLength: 1, maxLength: 400 },
    safety_warnings: {
      type: "array",
      maxItems: 10,
      items: {
        type: "object",
        additionalProperties: false,
        required: [
          "code",
          "severity",
          "message",
          "recommended_action",
          "applies_to_exercise",
          "requires_professional_clearance",
        ],
        properties: {
          code: {
            type: "string",
            enum: [
              "stop_if_pain",
              "form_priority",
              "injury_modification",
              "beginner_intensity",
              "medical_referral",
              "equipment_substitution",
            ],
          },
          severity: { type: "string", enum: ["info", "caution", "stop"] },
          message: { type: "string", minLength: 1, maxLength: 300 },
          recommended_action: { type: "string", minLength: 1, maxLength: 300 },
          applies_to_exercise: {
            type: ["string", "null"],
            minLength: 1,
            maxLength: 120,
          },
          requires_professional_clearance: { type: "boolean" },
        },
      },
    },
  },
};

const WORKOUT_PLAN_SYSTEM_INSTRUCTION = [
  "You generate structured workout plans for general fitness only.",
  "Do not diagnose, treat, or interpret medical conditions.",
  "Do not provide rehabilitation protocols, return-to-sport advice, or injury-treatment plans.",
  "Do not replace a doctor, physical therapist, or other licensed medical professional.",
  "If the user reports red-flag symptoms such as chest pain, fainting, severe dizziness, sudden severe shortness of breath, or sharp worsening pain, do not coach through the risk as if it were normal training.",
  "When medical risk or clearance needs are present, keep the output conservative and use structured safety warnings to recommend professional assessment instead of medical advice.",
  "If the user has limitations but no red-flag symptoms, prefer lower-risk substitutions, reduced complexity, and pain-free ranges of motion.",
  "Be conservative for beginner users.",
  "Respect the user's stated limitations, exercise preferences, equipment, and training location.",
  "Follow the WorkoutPlan schema exactly.",
  "All fields must be present.",
  "Use [] for empty lists.",
  "Use null for nullable fields that do not apply.",
  "For repetitions prescriptions, include reps_min and reps_max, set duration_seconds to null, and ensure reps_min <= reps_max.",
  "For duration prescriptions, include duration_seconds and set reps_min and reps_max to null.",
  "Use retrieved knowledge context when it is relevant to the user profile and safety constraints.",
  "Do not output prose outside the structured response.",
].join(" ");

class AppError extends Error {
  constructor(status, code, message, details = null) {
    super(message);
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

export default {
  async fetch(request, env, ctx) {
    return handleRequest(request, env, ctx);
  },
};

export async function handleRequest(request, env, ctx) {
  const url = new URL(request.url);
  const requestId = request.headers.get("X-Request-ID") || crypto.randomUUID();

  try {
    if (request.method === "GET" && url.pathname === "/health") {
      return jsonResponse(
        {
          status: "ok",
          runtime: "cloudflare-worker",
          d1_binding: Boolean(env.FITCOACH_DB),
        },
        200,
        requestId,
      );
    }

    if (request.method === "POST" && url.pathname === "/api/workout-plans") {
      return await handleWorkoutPlanRequest(request, env, requestId, ctx);
    }

    if (request.method === "POST" && url.pathname === "/api/feedback") {
      return await handleFeedbackRequest(request, env, requestId);
    }

    if (request.method === "GET") {
      return await serveAsset(request, env, ctx, requestId);
    }

    throw new AppError(404, "NOT_FOUND", "The requested route was not found.");
  } catch (error) {
    if (error instanceof AppError) {
      return errorResponse(error, requestId);
    }

    return errorResponse(
      new AppError(500, "INTERNAL_SERVER_ERROR", "An unexpected error occurred."),
      requestId,
    );
  }
}

async function handleWorkoutPlanRequest(request, env, requestId, ctx) {
  requireBinding(env, "FITCOACH_DB");
  const langfuseConfig = getLangfuseConfig(env);
  const profile = validateUserProfile(await parseJson(request));
  const retrievalQuery = buildRetrievalQuery(profile);
  const retrievalStartedAt = new Date().toISOString();
  const retrievalResult = await retrieveKnowledge(profile, retrievalQuery, env);
  const retrievalFinishedAt = new Date().toISOString();
  const retrievedChunks = retrievalResult.chunks;

  let usedFallback = false;
  const generationStartedAtEpoch = Date.now();
  const generationStartedAt = new Date(generationStartedAtEpoch).toISOString();
  let plan = null;
  let usage = null;
  let refusalDetected = false;
  let safetyTriggerCodes = [];
  let generationStatus = "success";
  let generationErrorCode = null;
  try {
    const generationResult = await generateWorkoutPlan(profile, retrievedChunks, env);
    plan = generationResult.plan;
    usage = generationResult.usage;
    refusalDetected = generationResult.refusalDetected;
    safetyTriggerCodes = generationResult.safetyTriggerCodes;
    validateWorkoutPlan(plan);
  } catch (error) {
    if (error instanceof AppError) {
      generationStatus = "error";
      generationErrorCode = error.code;
      refusalDetected = error.code === "OPENAI_REFUSAL";
      safetyTriggerCodes = error.code === "OPENAI_REFUSAL" ? ["model_refusal"] : [];
      plan = null;
      usage = null;
      await finalizeGenerationFailure({
        env,
        request,
        requestId,
        ctx,
        langfuseConfig,
        profile,
        retrievalQuery,
        retrievalResult,
        retrievalStartedAt,
        retrievalFinishedAt,
        generationStartedAt,
        generationFinishedAt: new Date().toISOString(),
        refusalDetected,
        safetyTriggerCodes,
        generationStatus,
        generationErrorCode,
      });
      throw error;
    }

    usedFallback = true;
    plan = buildFallbackWorkoutPlan(profile);
  }

  const generationFinishedAtEpoch = Date.now();
  const generationFinishedAt = new Date(generationFinishedAtEpoch).toISOString();
  const latencyMs = generationFinishedAtEpoch - generationStartedAtEpoch;
  const chunkIds = retrievedChunks.map((chunk) => chunk.chunk_id);
  const traceId = langfuseConfig.enabled ? requestId : null;
  await saveGenerationRun(env.FITCOACH_DB, {
    requestId,
    createdAt: new Date().toISOString(),
    appRuntime: "cloudflare-worker",
    appVersion: env.APP_VERSION || null,
    requestLocale: normalizeLocale(request.headers.get("Accept-Language")),
    provider: "openai",
    model: env.OPENAI_MODEL || "unconfigured",
    ragProvider: env.RAG_EMBEDDING_PROVIDER || null,
    ragCollection: env.QDRANT_COLLECTION || null,
    chunkIds,
    chunkCount: chunkIds.length,
    profile,
    workoutPlan: plan,
    generationStatus,
    errorCode: generationErrorCode,
    latencyMs,
    usedFallback,
    traceId,
    traceEnabled: langfuseConfig.enabled,
  });

  if (langfuseConfig.enabled) {
    const tracePromise = submitLangfuseTrace({
      config: langfuseConfig,
      traceId,
      requestId,
      profile,
      locale: normalizeLocale(request.headers.get("Accept-Language")),
      environment: env.APP_ENV || "production",
      version: env.APP_VERSION || null,
      retrieval: {
        startedAt: retrievalStartedAt,
        finishedAt: retrievalFinishedAt,
        query: retrievalQuery,
        chunkIds,
        chunkCount: chunkIds.length,
        ragProvider: env.RAG_EMBEDDING_PROVIDER || null,
        ragCollection: env.QDRANT_COLLECTION || null,
        failed: retrievalResult.failed,
      },
      generation: {
        startedAt: generationStartedAt,
        finishedAt: generationFinishedAt,
        completionStartTime: generationStartedAt,
        input: buildWorkoutPlanPrompt(profile, retrievedChunks),
        output: plan,
        model: env.OPENAI_MODEL || "unconfigured",
        usage,
        usedFallback,
        refusalDetected,
        safetyTriggerCodes,
        generationStatus,
        errorCode: generationErrorCode,
      },
    }).catch((error) => {
      console.warn("langfuse_trace_submission_failed", {
        request_id: requestId,
        error: error instanceof Error ? error.message : String(error),
      });
    });

    if (ctx && typeof ctx.waitUntil === "function") {
      ctx.waitUntil(tracePromise);
    }
  }

  return jsonResponse(plan, 200, requestId, {
    "X-RAG-Chunk-Count": String(chunkIds.length),
    "X-RAG-Chunk-Ids": chunkIds.slice(0, 3).join(","),
  });
}

async function finalizeGenerationFailure({
  env,
  request,
  requestId,
  ctx,
  langfuseConfig,
  profile,
  retrievalQuery,
  retrievalResult,
  retrievalStartedAt,
  retrievalFinishedAt,
  generationStartedAt,
  generationFinishedAt,
  refusalDetected,
  safetyTriggerCodes,
  generationStatus,
  generationErrorCode,
}) {
  const chunkIds = retrievalResult.chunks.map((chunk) => chunk.chunk_id);
  const traceId = langfuseConfig.enabled ? requestId : null;
  await saveGenerationRun(env.FITCOACH_DB, {
    requestId,
    createdAt: new Date().toISOString(),
    appRuntime: "cloudflare-worker",
    appVersion: env.APP_VERSION || null,
    requestLocale: normalizeLocale(request.headers.get("Accept-Language")),
    provider: "openai",
    model: env.OPENAI_MODEL || "unconfigured",
    ragProvider: env.RAG_EMBEDDING_PROVIDER || null,
    ragCollection: env.QDRANT_COLLECTION || null,
    chunkIds,
    chunkCount: chunkIds.length,
    profile,
    workoutPlan: null,
    generationStatus,
    errorCode: generationErrorCode,
    latencyMs: Date.parse(generationFinishedAt) - Date.parse(generationStartedAt),
    usedFallback: false,
    traceId,
    traceEnabled: langfuseConfig.enabled,
  });

  if (!langfuseConfig.enabled) {
    return;
  }

  const tracePromise = submitLangfuseTrace({
    config: langfuseConfig,
    traceId,
    requestId,
    profile,
    locale: normalizeLocale(request.headers.get("Accept-Language")),
    environment: env.APP_ENV || "production",
    version: env.APP_VERSION || null,
    retrieval: {
      startedAt: retrievalStartedAt,
      finishedAt: retrievalFinishedAt,
      query: retrievalQuery,
      chunkIds,
      chunkCount: chunkIds.length,
      ragProvider: env.RAG_EMBEDDING_PROVIDER || null,
      ragCollection: env.QDRANT_COLLECTION || null,
      failed: retrievalResult.failed,
    },
    generation: {
      startedAt: generationStartedAt,
      finishedAt: generationFinishedAt,
      completionStartTime: generationStartedAt,
      input: buildWorkoutPlanPrompt(profile, retrievalResult.chunks),
      output: { error_code: generationErrorCode },
      model: env.OPENAI_MODEL || "unconfigured",
      usage: null,
      usedFallback: false,
      refusalDetected,
      safetyTriggerCodes,
      generationStatus,
      errorCode: generationErrorCode,
    },
  }).catch((error) => {
    console.warn("langfuse_trace_submission_failed", {
      request_id: requestId,
      error: error instanceof Error ? error.message : String(error),
    });
  });

  if (ctx && typeof ctx.waitUntil === "function") {
    ctx.waitUntil(tracePromise);
  }
}

async function handleFeedbackRequest(request, env, requestId) {
  requireBinding(env, "FITCOACH_DB");
  const payload = await parseJson(request);
  const submission = validateFeedbackSubmission(payload);
  const generationRun = await loadGenerationRun(env.FITCOACH_DB, submission.request_id);
  if (!generationRun) {
    throw new AppError(
      404,
      "GENERATION_NOT_FOUND",
      "The associated generation run was not found. Generate a new plan and try again.",
    );
  }

  await saveFeedbackSubmission(env.FITCOACH_DB, {
    requestId: submission.request_id,
    feedback: submission.feedback,
    runtimeMetadata: {
      saved_request_id: requestId,
      profile_json: JSON.stringify(submission.profile),
      workout_plan_json: JSON.stringify(submission.generated_plan),
      chunk_ids_json: generationRun.rag_chunk_ids_json,
      chunk_count: generationRun.chunk_count,
      latency_ms: generationRun.latency_ms,
      used_fallback: Boolean(generationRun.used_fallback),
      model_name: generationRun.model,
      trace_id: generationRun.trace_id,
      trace_enabled: Boolean(generationRun.trace_enabled),
      langfuse_host: env.LANGFUSE_BASE_URL || null,
    },
  });

  return jsonResponse(
    {
      ok: true,
      request_id: submission.request_id,
      message: "Feedback saved.",
    },
    201,
    requestId,
  );
}

async function serveAsset(request, env, ctx, requestId) {
  if (!env.ASSETS || typeof env.ASSETS.fetch !== "function") {
    throw new AppError(404, "NOT_FOUND", "Static assets are not available.");
  }

  const response = await env.ASSETS.fetch(request);
  const headers = new Headers(response.headers);
  headers.set("X-Request-ID", requestId);
  headers.set("Cache-Control", "no-store");
  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers,
  });
}

async function parseJson(request) {
  try {
    return await request.json();
  } catch {
    throw new AppError(400, "INVALID_JSON", "The request body must be valid JSON.");
  }
}

function validateUserProfile(payload) {
  if (!isPlainObject(payload)) {
    throw new AppError(422, "REQUEST_VALIDATION_ERROR", "The request data is invalid.");
  }

  const normalized = {
    goal: validateEnum(payload.goal, FITNESS_GOALS, "goal"),
    experience_level: validateEnum(
      payload.experience_level,
      EXPERIENCE_LEVELS,
      "experience_level",
    ),
    training_days_per_week: validateInteger(
      payload.training_days_per_week,
      1,
      7,
      "training_days_per_week",
    ),
    session_duration_minutes: validateInteger(
      payload.session_duration_minutes,
      15,
      180,
      "session_duration_minutes",
    ),
    equipment: validateUniqueStringList(payload.equipment, {
      field: "equipment",
      minItems: 1,
      maxItems: 8,
      allowedValues: EQUIPMENT_OPTIONS,
    }),
    training_location: validateEnum(
      payload.training_location,
      TRAINING_LOCATIONS,
      "training_location",
    ),
    injuries_or_limitations: validateUniqueStringList(payload.injuries_or_limitations ?? [], {
      field: "injuries_or_limitations",
      minItems: 0,
      maxItems: 5,
      maxLength: 200,
    }),
    exercise_preferences: validateUniqueStringList(payload.exercise_preferences ?? [], {
      field: "exercise_preferences",
      minItems: 0,
      maxItems: 5,
      maxLength: 200,
    }),
  };

  return normalized;
}

function validateFeedbackSubmission(payload) {
  if (!isPlainObject(payload)) {
    throw new AppError(422, "REQUEST_VALIDATION_ERROR", "The request data is invalid.");
  }

  const requestId = validateString(payload.request_id, "request_id", 1, 120);
  const profile = validateUserProfile(payload.profile);
  const generatedPlan = validateWorkoutPlan(payload.generated_plan);
  const feedback = {
    usefulness_rating: validateInteger(payload.feedback?.usefulness_rating, 1, 5, "usefulness_rating"),
    difficulty_feedback: validateEnum(
      payload.feedback?.difficulty_feedback,
      DIFFICULTY_FEEDBACK,
      "difficulty_feedback",
    ),
    felt_safe: validateBoolean(payload.feedback?.felt_safe, "felt_safe"),
    would_follow_plan: validateBoolean(
      payload.feedback?.would_follow_plan,
      "would_follow_plan",
    ),
    feedback_text:
      payload.feedback?.feedback_text == null || payload.feedback?.feedback_text === ""
        ? null
        : validateString(payload.feedback.feedback_text, "feedback_text", 1, 1000),
  };

  return {
    request_id: requestId,
    profile,
    generated_plan: generatedPlan,
    feedback,
  };
}

function validateWorkoutPlan(payload) {
  if (!isPlainObject(payload)) {
    throw new AppError(422, "REQUEST_VALIDATION_ERROR", "The workout plan is invalid.");
  }

  const trainingDays = validateInteger(
    payload.training_days_per_week,
    1,
    7,
    "training_days_per_week",
  );
  const weeklySchedule = validateArray(
    payload.weekly_schedule,
    "weekly_schedule",
    1,
    7,
  ).map((day) => validateWorkoutDay(day));

  if (weeklySchedule.length !== trainingDays) {
    throw new AppError(
      422,
      "REQUEST_VALIDATION_ERROR",
      "The workout plan is invalid.",
      [{ field: "weekly_schedule", message: "weekly_schedule length must equal training_days_per_week" }],
    );
  }

  const dayIndexes = weeklySchedule.map((day) => day.day_index);
  if (new Set(dayIndexes).size !== dayIndexes.length) {
    throw new AppError(
      422,
      "REQUEST_VALIDATION_ERROR",
      "The workout plan is invalid.",
      [{ field: "weekly_schedule", message: "weekly_schedule must not contain duplicate day_index values" }],
    );
  }

  return {
    title: validateString(payload.title, "title", 1, 120),
    summary: validateString(payload.summary, "summary", 1, 500),
    goal: validateEnum(payload.goal, FITNESS_GOALS, "goal"),
    experience_level: validateEnum(
      payload.experience_level,
      EXPERIENCE_LEVELS,
      "experience_level",
    ),
    training_days_per_week: trainingDays,
    duration_weeks: validateInteger(payload.duration_weeks, 1, 12, "duration_weeks"),
    weekly_schedule: weeklySchedule,
    progression_suggestion: validateString(
      payload.progression_suggestion,
      "progression_suggestion",
      1,
      400,
    ),
    safety_warnings: validateArray(payload.safety_warnings, "safety_warnings", 0, 10).map((item) =>
      validateSafetyWarning(item),
    ),
  };
}

function validateWorkoutDay(payload) {
  if (!isPlainObject(payload)) {
    throw new AppError(422, "REQUEST_VALIDATION_ERROR", "The workout plan is invalid.");
  }

  return {
    day_index: validateInteger(payload.day_index, 1, 7, "day_index"),
    title: validateString(payload.title, "title", 1, 120),
    focus: validateString(payload.focus, "focus", 1, 200),
    estimated_duration_minutes: validateInteger(
      payload.estimated_duration_minutes,
      15,
      180,
      "estimated_duration_minutes",
    ),
    warm_up: validateStringList(payload.warm_up, "warm_up", 1, 5, 200),
    exercises: validateArray(payload.exercises, "exercises", 1, 12).map((item) =>
      validateExerciseItem(item),
    ),
    cool_down: validateStringList(payload.cool_down, "cool_down", 1, 5, 200),
    intensity_note: validateString(payload.intensity_note, "intensity_note", 1, 240),
  };
}

function validateExerciseItem(payload) {
  if (!isPlainObject(payload)) {
    throw new AppError(422, "REQUEST_VALIDATION_ERROR", "The workout plan is invalid.");
  }

  const prescriptionType = validateEnum(
    payload.prescription_type,
    new Set(["repetitions", "duration"]),
    "prescription_type",
  );
  const repsMin = validateNullableInteger(payload.reps_min, 1, 100, "reps_min");
  const repsMax = validateNullableInteger(payload.reps_max, 1, 100, "reps_max");
  const durationSeconds = validateNullableInteger(
    payload.duration_seconds,
    15,
    3600,
    "duration_seconds",
  );

  if (prescriptionType === "repetitions") {
    if (repsMin == null || repsMax == null || durationSeconds != null || repsMin > repsMax) {
      throw new AppError(422, "REQUEST_VALIDATION_ERROR", "The workout plan is invalid.");
    }
  }
  if (prescriptionType === "duration") {
    if (durationSeconds == null || repsMin != null || repsMax != null) {
      throw new AppError(422, "REQUEST_VALIDATION_ERROR", "The workout plan is invalid.");
    }
  }

  return {
    name: validateString(payload.name, "name", 1, 120),
    category: validateEnum(payload.category, new Set(["strength", "cardio", "mobility"]), "category"),
    prescription_type: prescriptionType,
    sets: validateInteger(payload.sets, 1, 8, "sets"),
    reps_min: repsMin,
    reps_max: repsMax,
    duration_seconds: durationSeconds,
    rest_seconds: validateNullableInteger(payload.rest_seconds, 0, 600, "rest_seconds"),
    intensity: validateEnum(payload.intensity, new Set(["low", "moderate", "high"]), "intensity"),
    target_muscles: validateStringList(payload.target_muscles, "target_muscles", 1, 6, 200),
    instructions: validateStringList(payload.instructions, "instructions", 1, 6, 200),
    safety_notes: validateStringList(payload.safety_notes ?? [], "safety_notes", 0, 5, 200),
    alternatives: validateStringList(payload.alternatives ?? [], "alternatives", 0, 3, 200),
  };
}

function validateSafetyWarning(payload) {
  if (!isPlainObject(payload)) {
    throw new AppError(422, "REQUEST_VALIDATION_ERROR", "The workout plan is invalid.");
  }

  const code = validateEnum(
    payload.code,
    new Set([
      "stop_if_pain",
      "form_priority",
      "injury_modification",
      "beginner_intensity",
      "medical_referral",
      "equipment_substitution",
    ]),
    "code",
  );
  const normalized = {
    code,
    severity: validateEnum(payload.severity, new Set(["info", "caution", "stop"]), "severity"),
    message: validateString(payload.message, "message", 1, 300),
    recommended_action: validateString(
      payload.recommended_action,
      "recommended_action",
      1,
      300,
    ),
    applies_to_exercise:
      payload.applies_to_exercise == null
        ? null
        : validateString(payload.applies_to_exercise, "applies_to_exercise", 1, 120),
    requires_professional_clearance: validateBoolean(
      payload.requires_professional_clearance,
      "requires_professional_clearance",
    ),
  };

  if (code === "medical_referral" && !normalized.requires_professional_clearance) {
    throw new AppError(422, "REQUEST_VALIDATION_ERROR", "The workout plan is invalid.");
  }

  return normalized;
}

function validateString(value, field, minLength, maxLength) {
  if (typeof value !== "string") {
    throw validationError(field, "must be a string");
  }

  const normalized = value.trim();
  if (normalized.length < minLength || normalized.length > maxLength) {
    throw validationError(field, `must be between ${minLength} and ${maxLength} characters`);
  }
  return normalized;
}

function validateEnum(value, allowed, field) {
  const normalized = validateString(value, field, 1, 200);
  if (!allowed.has(normalized)) {
    throw validationError(field, "contains an unsupported value");
  }
  return normalized;
}

function validateInteger(value, min, max, field) {
  if (!Number.isInteger(value)) {
    throw validationError(field, "must be an integer");
  }
  if (value < min || value > max) {
    throw validationError(field, `must be between ${min} and ${max}`);
  }
  return value;
}

function validateNullableInteger(value, min, max, field) {
  if (value == null) {
    return null;
  }
  return validateInteger(value, min, max, field);
}

function validateBoolean(value, field) {
  if (typeof value !== "boolean") {
    throw validationError(field, "must be a boolean");
  }
  return value;
}

function validateArray(value, field, minItems, maxItems) {
  if (!Array.isArray(value)) {
    throw validationError(field, "must be an array");
  }
  if (value.length < minItems || value.length > maxItems) {
    throw validationError(field, `must contain between ${minItems} and ${maxItems} items`);
  }
  return value;
}

function validateStringList(value, field, minItems, maxItems, maxLength) {
  return validateArray(value, field, minItems, maxItems).map((item) =>
    validateString(item, field, 1, maxLength),
  );
}

function validateUniqueStringList(
  value,
  { field, minItems, maxItems, maxLength = 200, allowedValues = null },
) {
  const normalized = validateStringList(value, field, minItems, maxItems, maxLength);
  const dedupeKey = normalized.map((item) => item.toLowerCase());
  if (new Set(dedupeKey).size !== dedupeKey.length) {
    throw validationError(field, "must not contain duplicates");
  }
  if (allowedValues) {
    for (const item of normalized) {
      if (!allowedValues.has(item)) {
        throw validationError(field, "contains an unsupported value");
      }
    }
  }
  return normalized;
}

function validationError(field, message) {
  return new AppError(422, "REQUEST_VALIDATION_ERROR", "The request data is invalid.", [
    { field, message },
  ]);
}

function buildRetrievalQuery(profile) {
  return [
    `goal: ${profile.goal}`,
    `experience_level: ${profile.experience_level}`,
    `training_days_per_week: ${profile.training_days_per_week}`,
    `session_duration_minutes: ${profile.session_duration_minutes}`,
    `equipment: ${profile.equipment.join(", ") || "none"}`,
    `training_location: ${profile.training_location}`,
    `injuries_or_limitations: ${profile.injuries_or_limitations.join(", ") || "none"}`,
    `exercise_preferences: ${profile.exercise_preferences.join(", ") || "none"}`,
  ].join("\n");
}

function buildWorkoutPlanPrompt(profile, retrievedChunks) {
  const promptLines = [
    "Create a workout plan from this user profile.",
    `goal: ${profile.goal}`,
    `experience_level: ${profile.experience_level}`,
    `training_days_per_week: ${profile.training_days_per_week}`,
    `session_duration_minutes: ${profile.session_duration_minutes}`,
    `equipment: ${profile.equipment.join(", ") || "none"}`,
    `training_location: ${profile.training_location}`,
    `injuries_or_limitations: ${profile.injuries_or_limitations.join(", ") || "none"}`,
    `exercise_preferences: ${profile.exercise_preferences.join(", ") || "none"}`,
  ];

  if (retrievedChunks.length > 0) {
    promptLines.push("", "Retrieved knowledge context:");
    retrievedChunks.forEach((chunk, index) => {
      let header = `[${index + 1}] chunk_id=${chunk.chunk_id}; title=${chunk.title}; topic=${chunk.topic}; document_id=${chunk.document_id}`;
      if (Array.isArray(chunk.section_path) && chunk.section_path.length > 0) {
        header += `; section_path=${chunk.section_path.join(" > ")}`;
      }
      promptLines.push(header, chunk.text);
    });
  }

  return [
    {
      role: "system",
      content: WORKOUT_PLAN_SYSTEM_INSTRUCTION,
    },
    {
      role: "user",
      content: promptLines.join("\n"),
    },
  ];
}

async function retrieveKnowledge(profile, retrievalQuery, env) {
  if (!env.QDRANT_URL || !env.QDRANT_COLLECTION) {
    return { chunks: [], failed: false };
  }

  const effectiveLimit = Number.parseInt(env.RAG_RETRIEVAL_LIMIT || "3", 10);
  if (!Number.isFinite(effectiveLimit) || effectiveLimit <= 0) {
    return { chunks: [], failed: false };
  }

  let queryVector;
  try {
    queryVector = await embedText(retrievalQuery, env);
  } catch {
    return { chunks: [], failed: true };
  }

  const headers = { "content-type": "application/json" };
  if (env.QDRANT_API_KEY) {
    headers["api-key"] = env.QDRANT_API_KEY;
  }

  const response = await fetch(
    `${env.QDRANT_URL.replace(/\/$/, "")}/collections/${env.QDRANT_COLLECTION}/points/query`,
    {
      method: "POST",
      headers,
      body: JSON.stringify({
        query: queryVector,
        limit: effectiveLimit,
        with_payload: true,
      }),
    },
  );

  if (!response.ok) {
    return { chunks: [], failed: true };
  }

  const body = await response.json();
  const result = Array.isArray(body?.result)
    ? body.result
    : Array.isArray(body?.result?.points)
      ? body.result.points
      : [];

  return {
    chunks: result
      .map((match) => normalizeRetrievedChunk(match))
      .filter((chunk) => chunk !== null),
    failed: false,
  };
}

async function embedText(text, env) {
  const provider = env.RAG_EMBEDDING_PROVIDER || "local-hash";
  const dimensions = Number.parseInt(env.RAG_EMBEDDING_DIMENSIONS || "256", 10);
  if (provider === "local-hash") {
    return hashEmbed(text, dimensions);
  }

  if (provider !== "openai") {
    throw new AppError(500, "UNSUPPORTED_EMBEDDING_PROVIDER", "The embedding provider is unsupported.");
  }

  if (!env.OPENAI_API_KEY || !env.RAG_EMBEDDING_MODEL) {
    throw new AppError(503, "OPENAI_CONFIG_MISSING", "The workout generation service is not configured.");
  }

  const response = await fetch("https://api.openai.com/v1/embeddings", {
    method: "POST",
    headers: {
      authorization: `Bearer ${env.OPENAI_API_KEY}`,
      "content-type": "application/json",
    },
    body: JSON.stringify({
      model: env.RAG_EMBEDDING_MODEL,
      input: text,
    }),
  });

  if (!response.ok) {
    throw new AppError(502, "OPENAI_REQUEST_FAILED", "The workout generation service request failed.");
  }

  const body = await response.json();
  return body?.data?.[0]?.embedding ?? [];
}

async function generateWorkoutPlan(profile, retrievedChunks, env) {
  if (!env.OPENAI_API_KEY || !env.OPENAI_MODEL) {
    throw new AppError(503, "OPENAI_CONFIG_MISSING", "The workout generation service is not configured.");
  }

  if (containsMedicalRisk(profile)) {
    return {
      plan: buildFallbackWorkoutPlan(profile, true),
      usage: null,
      refusalDetected: false,
      safetyTriggerCodes: ["medical_keyword"],
    };
  }

  const controller = new AbortController();
  const timeoutMs = Number.parseInt(env.OPENAI_TIMEOUT_MS || `${DEFAULT_TIMEOUT_MS}`, 10);
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch("https://api.openai.com/v1/responses", {
      method: "POST",
      signal: controller.signal,
      headers: {
        authorization: `Bearer ${env.OPENAI_API_KEY}`,
        "content-type": "application/json",
      },
      body: JSON.stringify({
        model: env.OPENAI_MODEL,
        input: buildWorkoutPlanPrompt(profile, retrievedChunks),
        text: {
          format: {
            type: "json_schema",
            name: "workout_plan",
            strict: true,
            schema: WORKOUT_PLAN_JSON_SCHEMA,
          },
        },
      }),
    });

    if (!response.ok) {
      throw new AppError(502, "OPENAI_REQUEST_FAILED", "The workout generation service request failed.");
    }

    const body = await response.json();
    if (extractRefusal(body)) {
      throw new AppError(
        502,
        "OPENAI_REFUSAL",
        "The workout generation service did not return a workout plan.",
      );
    }
    const outputText = extractOutputText(body);
    if (!outputText) {
      throw new AppError(
        502,
        "OPENAI_INVALID_OUTPUT",
        "The workout generation service did not return a valid workout plan.",
      );
    }
    return {
      plan: JSON.parse(outputText),
      usage: normalizeUsage(body?.usage),
      refusalDetected: false,
      safetyTriggerCodes: [],
    };
  } catch (error) {
    if (error instanceof AppError) {
      throw error;
    }
    if (error?.name === "AbortError") {
      throw new AppError(504, "OPENAI_TIMEOUT", "The workout generation service timed out.");
    }
    throw error;
  } finally {
    clearTimeout(timeoutId);
  }
}

function extractOutputText(body) {
  if (typeof body?.output_text === "string" && body.output_text.trim()) {
    return body.output_text;
  }

  for (const item of body?.output || []) {
    for (const content of item?.content || []) {
      if (typeof content?.text === "string" && content.text.trim()) {
        return content.text;
      }
    }
  }

  return null;
}

function extractRefusal(body) {
  for (const item of body?.output || []) {
    for (const content of item?.content || []) {
      if (typeof content?.refusal === "string" && content.refusal.trim()) {
        return content.refusal.trim();
      }
    }
  }

  return null;
}

function containsMedicalRisk(profile) {
  const haystack = [
    ...profile.injuries_or_limitations,
    ...profile.exercise_preferences,
  ]
    .join(" ")
    .toLowerCase();
  return MEDICAL_TRIGGER_PATTERNS.some((pattern) => haystack.includes(pattern));
}

function buildFallbackWorkoutPlan(profile, medicalFallback = false) {
  const schedule = [];
  for (let index = 0; index < profile.training_days_per_week; index += 1) {
    schedule.push({
      day_index: index + 1,
      title: `Day ${index + 1} - Low-risk full body session`,
      focus: "Technique-first strength and low-impact conditioning",
      estimated_duration_minutes: Math.min(profile.session_duration_minutes, 45),
      warm_up: [
        "Walk or march in place for 5 minutes",
        "Move through a comfortable range of motion before loading exercises",
      ],
      exercises: [
        {
          name: "Chair Squat",
          category: "strength",
          prescription_type: "repetitions",
          sets: 2,
          reps_min: 8,
          reps_max: 10,
          duration_seconds: null,
          rest_seconds: 75,
          intensity: "low",
          target_muscles: ["legs", "glutes"],
          instructions: [
            "Use a pain-free range of motion.",
            "Stand up with control and sit back down slowly.",
          ],
          safety_notes: ["Stop immediately if pain sharpens."],
          alternatives: ["Sit-to-stand from a taller surface"],
        },
        {
          name: "Incline Push-up",
          category: "strength",
          prescription_type: "repetitions",
          sets: 2,
          reps_min: 6,
          reps_max: 8,
          duration_seconds: null,
          rest_seconds: 75,
          intensity: "low",
          target_muscles: ["chest", "shoulders", "triceps"],
          instructions: [
            "Use a wall or counter to reduce load.",
            "Keep ribs down and move with control.",
          ],
          safety_notes: [],
          alternatives: ["Wall push-up"],
        },
        {
          name: "Brisk Walk",
          category: "cardio",
          prescription_type: "duration",
          sets: 1,
          reps_min: null,
          reps_max: null,
          duration_seconds: 600,
          rest_seconds: null,
          intensity: "low",
          target_muscles: ["cardiovascular system"],
          instructions: [
            "Choose a pace that allows easy conversation.",
          ],
          safety_notes: [],
          alternatives: ["Easy cycling"],
        },
      ],
      cool_down: [
        "Easy walking for 3 minutes",
        "Gentle breathing and light stretching",
      ],
      intensity_note: "Keep the session comfortable and leave several reps in reserve.",
    });
  }

  return {
    title: medicalFallback
      ? "Conservative plan pending medical clearance"
      : `${profile.training_days_per_week}-Day Beginner Conservative Plan`,
    summary: medicalFallback
      ? "The request included medical-risk language, so this fallback keeps activity low-risk and directs the user to seek professional clearance."
      : "A conservative fallback plan that keeps the public MVP usable when the model response is unavailable.",
    goal: profile.goal,
    experience_level: profile.experience_level,
    training_days_per_week: profile.training_days_per_week,
    duration_weeks: 2,
    weekly_schedule: schedule,
    progression_suggestion:
      "Repeat the same schedule for two weeks before increasing volume, and keep each session comfortably below all-out effort.",
    safety_warnings: [
      {
        code: medicalFallback ? "medical_referral" : "form_priority",
        severity: medicalFallback ? "stop" : "caution",
        message: medicalFallback
          ? "The profile mentions a condition or symptom that should be cleared by a licensed medical professional before training progresses."
          : "Use a pain-free range of motion and prioritize technique over intensity.",
        recommended_action: medicalFallback
          ? "Pause progression and seek professional assessment before following a more demanding program."
          : "Reduce range of motion, slow the tempo, or stop the exercise if discomfort increases.",
        applies_to_exercise: null,
        requires_professional_clearance: medicalFallback,
      },
    ],
  };
}

async function saveGenerationRun(db, record) {
  await db
    .prepare(
      `INSERT OR REPLACE INTO generation_runs (
        request_id,
        created_at,
        app_runtime,
        app_version,
        request_locale,
        provider,
        model,
        rag_provider,
        rag_collection,
        rag_chunk_ids_json,
        chunk_count,
        profile_json,
        workout_plan_json,
        generation_status,
        error_code,
        latency_ms,
        used_fallback,
        trace_id,
        trace_enabled
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
    )
    .bind(
      record.requestId,
      record.createdAt,
      record.appRuntime,
      record.appVersion,
      record.requestLocale,
      record.provider,
      record.model,
      record.ragProvider,
      record.ragCollection,
      JSON.stringify(record.chunkIds),
      record.chunkCount,
      JSON.stringify(record.profile),
      JSON.stringify(record.workoutPlan),
      record.generationStatus,
      record.errorCode,
      record.latencyMs,
      record.usedFallback ? 1 : 0,
      record.traceId,
      record.traceEnabled ? 1 : 0,
    )
    .run();
}

async function loadGenerationRun(db, requestId) {
  const result = await db
    .prepare(
      `SELECT request_id, rag_chunk_ids_json, chunk_count, latency_ms, used_fallback, model,
              trace_id, trace_enabled
       FROM generation_runs
       WHERE request_id = ?`
    )
    .bind(requestId)
    .first();
  return result ?? null;
}

async function saveFeedbackSubmission(db, record) {
  const createdAt = new Date().toISOString();
  await db
    .prepare(
      `INSERT INTO plan_feedback (
        request_id,
        created_at,
        usefulness_rating,
        difficulty_feedback,
        felt_safe,
        would_follow_plan,
        feedback_text,
        feedback_json,
        runtime_metadata_json
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`
    )
    .bind(
      record.requestId,
      createdAt,
      record.feedback.usefulness_rating,
      record.feedback.difficulty_feedback,
      record.feedback.felt_safe ? 1 : 0,
      record.feedback.would_follow_plan ? 1 : 0,
      record.feedback.feedback_text,
      JSON.stringify(record.feedback),
      JSON.stringify(record.runtimeMetadata),
    )
    .run();
}

function normalizeRetrievedChunk(match) {
  const payload = match?.payload;
  if (!isPlainObject(payload)) {
    return null;
  }

  if (
    typeof payload.chunk_id !== "string" ||
    typeof payload.document_id !== "string" ||
    typeof payload.title !== "string" ||
    typeof payload.topic !== "string" ||
    typeof payload.text !== "string"
  ) {
    return null;
  }

  return {
    chunk_id: payload.chunk_id,
    document_id: payload.document_id,
    title: payload.title,
    topic: payload.topic,
    text: payload.text,
    section_path: Array.isArray(payload.section_path)
      ? payload.section_path.filter((item) => typeof item === "string")
      : null,
  };
}

async function hashEmbed(text, dimensions) {
  if (!Number.isInteger(dimensions) || dimensions <= 0) {
    throw new AppError(500, "INVALID_EMBEDDING_DIMENSIONS", "Embedding dimensions must be positive.");
  }

  const vector = Array.from({ length: dimensions }, () => 0);
  const tokens = text.toLowerCase().match(TOKEN_PATTERN) || [];
  if (tokens.length === 0) {
    return vector;
  }

  for (const token of tokens) {
    const digest = new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(token)));
    const index =
      ((digest[0] << 24) | (digest[1] << 16) | (digest[2] << 8) | digest[3]) >>> 0;
    const bucket = index % dimensions;
    const sign = digest[4] % 2 === 0 ? 1 : -1;
    const weight = 1 + digest[5] / 255;
    vector[bucket] += sign * weight;
  }

  const norm = Math.sqrt(vector.reduce((sum, value) => sum + value * value, 0));
  if (norm === 0) {
    return vector;
  }
  return vector.map((value) => value / norm);
}

function jsonResponse(body, status, requestId, extraHeaders = {}) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
      "X-Request-ID": requestId,
      ...extraHeaders,
    },
  });
}

function errorResponse(error, requestId) {
  return jsonResponse(
    {
      error: {
        code: error.code,
        message: error.message,
        details: error.details,
      },
      request_id: requestId,
    },
    error.status,
    requestId,
  );
}

function requireBinding(env, binding) {
  if (!env[binding]) {
    throw new AppError(
      500,
      "MISSING_BINDING",
      `The required Cloudflare binding ${binding} is not configured.`,
    );
  }
}

function normalizeLocale(acceptLanguage) {
  if (typeof acceptLanguage !== "string" || !acceptLanguage.trim()) {
    return null;
  }
  return acceptLanguage.split(",")[0]?.trim() || null;
}

function isPlainObject(value) {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function normalizeUsage(usage) {
  if (!isPlainObject(usage)) {
    return null;
  }

  const input = Number.isInteger(usage.input_tokens) ? usage.input_tokens : null;
  const output = Number.isInteger(usage.output_tokens) ? usage.output_tokens : null;
  const total =
    Number.isInteger(usage.total_tokens)
      ? usage.total_tokens
      : input != null || output != null
        ? (input || 0) + (output || 0)
        : null;

  if (input == null && output == null && total == null) {
    return null;
  }

  return {
    input: input ?? undefined,
    output: output ?? undefined,
    total: total ?? undefined,
  };
}
