function buildBasicAuthHeader(publicKey, secretKey) {
  const credentials = `${publicKey}:${secretKey}`;
  const encoded = btoa(credentials);
  return `Basic ${encoded}`;
}

function normalizeBaseUrl(baseUrl) {
  return (baseUrl || "https://cloud.langfuse.com").replace(/\/$/, "");
}

export function getLangfuseConfig(env) {
  const publicKey = env.LANGFUSE_PUBLIC_KEY;
  const secretKey = env.LANGFUSE_SECRET_KEY;
  if (!publicKey || !secretKey) {
    return {
      enabled: false,
      baseUrl: normalizeBaseUrl(env.LANGFUSE_BASE_URL),
    };
  }

  return {
    enabled: true,
    publicKey,
    secretKey,
    baseUrl: normalizeBaseUrl(env.LANGFUSE_BASE_URL),
  };
}

function buildIngestionHeaders(config) {
  return {
    authorization: buildBasicAuthHeader(config.publicKey, config.secretKey),
    "content-type": "application/json",
  };
}

function buildTraceEvent({
  traceId,
  requestId,
  startedAt,
  finishedAt,
  environment,
  version,
  locale,
  profile,
  metadata,
}) {
  return {
    id: crypto.randomUUID(),
    timestamp: finishedAt,
    type: "trace-create",
    body: {
      id: traceId,
      timestamp: startedAt,
      name: "public-workout-plan-request",
      userId: requestId,
      sessionId: requestId,
      input: profile,
      output: {
        request_id: requestId,
        used_fallback: metadata.usedFallback,
        chunk_count: metadata.chunkCount,
        safety_trigger_codes: metadata.safetyTriggerCodes,
      },
      metadata: {
        request_id: requestId,
        request_locale: locale,
        app_runtime: "cloudflare-worker",
        app_version: version,
        environment,
      },
      tags: ["public-mvp", "workout-plan"],
    },
  };
}

function buildSpanEvent({
  traceId,
  observationId,
  name,
  startedAt,
  finishedAt,
  input,
  output,
  metadata,
  parentObservationId = null,
  level = "DEFAULT",
  statusMessage = null,
}) {
  return {
    id: crypto.randomUUID(),
    timestamp: finishedAt,
    type: "span-create",
    body: {
      id: observationId,
      traceId,
      parentObservationId,
      name,
      startTime: startedAt,
      endTime: finishedAt,
      level,
      statusMessage,
      input,
      output,
      metadata,
    },
  };
}

function buildGenerationEvent({
  traceId,
  observationId,
  parentObservationId,
  startedAt,
  finishedAt,
  input,
  output,
  model,
  usage,
  metadata,
  completionStartTime = null,
}) {
  return {
    id: crypto.randomUUID(),
    timestamp: finishedAt,
    type: "generation-create",
    body: {
      id: observationId,
      traceId,
      parentObservationId,
      name: "openai-workout-plan",
      startTime: startedAt,
      endTime: finishedAt,
      completionStartTime,
      model,
      input,
      output,
      usage,
      metadata,
    },
  };
}

export async function submitLangfuseTrace({
  config,
  traceId,
  requestId,
  profile,
  locale,
  environment,
  version,
  retrieval,
  generation,
}) {
  if (!config.enabled) {
    return { skipped: true };
  }

  const requestStartedAt = retrieval.startedAt || generation.startedAt;
  const requestFinishedAt = generation.finishedAt || retrieval.finishedAt || requestStartedAt;
  const retrievalObservationId = `${traceId}:retrieval`;
  const generationObservationId = `${traceId}:generation`;

  const batch = [
    buildTraceEvent({
      traceId,
      requestId,
      startedAt: requestStartedAt,
      finishedAt: requestFinishedAt,
      environment,
      version,
      locale,
      profile,
      metadata: {
        chunkCount: retrieval.chunkCount,
        usedFallback: generation.usedFallback,
        safetyTriggerCodes: generation.safetyTriggerCodes,
      },
    }),
    buildSpanEvent({
      traceId,
      observationId: retrievalObservationId,
      name: "retrieve-knowledge",
      startedAt: retrieval.startedAt,
      finishedAt: retrieval.finishedAt,
      input: { query: retrieval.query },
      output: {
        chunk_ids: retrieval.chunkIds,
        chunk_count: retrieval.chunkCount,
      },
      metadata: {
        rag_provider: retrieval.ragProvider,
        rag_collection: retrieval.ragCollection,
        retrieval_failed: retrieval.failed,
      },
      level: retrieval.failed ? "WARNING" : "DEFAULT",
      statusMessage: retrieval.failed ? "Retrieval degraded to empty context." : null,
    }),
    buildGenerationEvent({
      traceId,
      observationId: generationObservationId,
      parentObservationId: retrievalObservationId,
      startedAt: generation.startedAt,
      finishedAt: generation.finishedAt,
      completionStartTime: generation.completionStartTime,
      input: generation.input,
      output: generation.output,
      model: generation.model,
      usage: generation.usage,
      metadata: {
        request_id: requestId,
        used_fallback: generation.usedFallback,
        refusal_detected: generation.refusalDetected,
        safety_trigger_codes: generation.safetyTriggerCodes,
      },
    }),
  ];

  const response = await fetch(`${config.baseUrl}/api/public/ingestion`, {
    method: "POST",
    headers: buildIngestionHeaders(config),
    body: JSON.stringify({ batch }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Langfuse ingestion failed (${response.status}): ${errorText}`);
  }

  return { skipped: false };
}
