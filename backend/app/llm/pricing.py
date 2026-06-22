from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ModelPricing:
    input_per_million_tokens_usd: float
    output_per_million_tokens_usd: float


# Best-effort local pricing table for text generation requests.
# Unknown models should report "unavailable" rather than guessing.
MODEL_PRICING_USD_PER_MILLION_TOKENS: dict[str, ModelPricing] = {}


def estimate_request_cost_usd(
    model: str,
    *,
    input_tokens: int | None,
    output_tokens: int | None,
) -> float | None:
    pricing = MODEL_PRICING_USD_PER_MILLION_TOKENS.get(model)
    if pricing is None:
        return None

    return estimate_request_cost_from_pricing_usd(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        input_per_million_tokens_usd=pricing.input_per_million_tokens_usd,
        output_per_million_tokens_usd=pricing.output_per_million_tokens_usd,
    )


def estimate_request_cost_from_pricing_usd(
    *,
    input_tokens: int | None,
    output_tokens: int | None,
    input_per_million_tokens_usd: float,
    output_per_million_tokens_usd: float,
) -> float:
    prompt_tokens = max(input_tokens or 0, 0)
    completion_tokens = max(output_tokens or 0, 0)

    input_cost = (prompt_tokens / 1_000_000) * input_per_million_tokens_usd
    output_cost = (completion_tokens / 1_000_000) * output_per_million_tokens_usd
    return input_cost + output_cost
