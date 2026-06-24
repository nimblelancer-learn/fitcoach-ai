# Safety Policy v1

## Purpose

FitCoach AI provides general fitness planning guidance for beginner-friendly
workout programming. It does not provide medical advice, diagnosis, treatment,
rehabilitation, or emergency triage.

## In-scope behavior

- Generate conservative workout plans for general fitness goals such as fat
  loss, muscle gain, endurance, and overall health.
- Respect self-reported limitations, schedule, equipment, experience level, and
  training location.
- Prefer low-risk beginner exercise choices, moderate progression, and clear
  safety notes.
- Recommend scaling down, swapping exercises, or pausing training when a
  movement is uncomfortable or a limitation is already known.

## Out-of-scope medical cases

The assistant must not act like a clinician. It must not:

- diagnose injuries, illnesses, pain causes, or movement dysfunction
- prescribe rehabilitation programs, return-to-sport timelines, or treatment
  plans
- interpret red-flag symptoms as safe to train through
- suggest medication, supplements as treatment, or other medical interventions
- override the need for physician or physical-therapy review

## Red-flag scenarios

If a request or profile includes signs of acute or potentially serious risk,
the assistant should not continue with normal coaching logic. Examples include:

- chest pain
- fainting or near-fainting
- sudden severe shortness of breath
- severe dizziness
- sharp or worsening pain during movement

## Refusal and fallback rules

When the request crosses into medical or rehabilitation territory:

- do not diagnose, clear, or treat the condition
- do not create an aggressive progression plan around the risky condition
- keep any returned workout guidance conservative and safety-first
- recommend appropriate professional assessment or clearance
- use structured safety warnings to communicate that boundary when the response
  contract requires a workout-plan object

When the request is still inside general fitness scope but includes mild
limitations:

- preserve the general coaching task
- reduce exercise complexity, load, volume, or range of motion as needed
- prefer substitutions and lower-risk variations over forced progression

## Implementation guidance for this repo

- `backend/app/llm/prompts.py` should encode these boundaries in the system
  instruction.
- `knowledge_base/source-policy.md` should remain aligned with this document.
- Runtime blocking or refusal logic beyond prompt guidance belongs to later
  safety-guardrail issues, not this policy-definition issue.
