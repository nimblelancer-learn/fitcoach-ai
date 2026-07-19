import test from "node:test";
import assert from "node:assert/strict";

import {
  OTHER_OPTION_VALUE,
  PROFILE_FIELD_PRESETS,
  containsVietnameseCharacters,
  normalizeProfileFieldSelection,
} from "../public/profile-fields.mjs";

test("preset definitions expose richer bilingual coverage for both profile fields", () => {
  assert.ok(PROFILE_FIELD_PRESETS.injuries_or_limitations.length >= 8);
  assert.ok(PROFILE_FIELD_PRESETS.exercise_preferences.length >= 9);
  assert.ok(
    PROFILE_FIELD_PRESETS.injuries_or_limitations.some((preset) => preset.value === OTHER_OPTION_VALUE),
  );
  assert.ok(
    PROFILE_FIELD_PRESETS.exercise_preferences.some((preset) => preset.value === OTHER_OPTION_VALUE),
  );
});

test("preset selections normalize to canonical English payload values", () => {
  const normalized = normalizeProfileFieldSelection(
    "exercise_preferences",
    ["Strength training", "Low-impact cardio"],
    "",
  );

  assert.deepEqual(normalized, ["Strength training", "Low-impact cardio"]);
});

test("other selections append English-safe custom entries", () => {
  const normalized = normalizeProfileFieldSelection(
    "injuries_or_limitations",
    ["Avoid jumping", OTHER_OPTION_VALUE],
    "Sensitive elbows\nAvoid kneeling",
  );

  assert.deepEqual(normalized, [
    "Avoid jumping",
    "Sensitive elbows",
    "Avoid kneeling",
  ]);
});

test("Vietnamese custom text is rejected for other selections", () => {
  assert.throws(
    () =>
      normalizeProfileFieldSelection(
        "exercise_preferences",
        [OTHER_OPTION_VALUE],
        "tap suc manh\nTập sức mạnh",
      ),
    { message: "exercise_preferences_english_only" },
  );
});

test("other selection requires at least one custom English entry", () => {
  assert.throws(
    () => normalizeProfileFieldSelection("injuries_or_limitations", [OTHER_OPTION_VALUE], ""),
    { message: "injuries_or_limitations_custom_required" },
  );
});

test("Vietnamese character detection stays available for final frontend guardrails", () => {
  assert.equal(containsVietnameseCharacters("Tập sức mạnh"), true);
  assert.equal(containsVietnameseCharacters("Strength training"), false);
});
