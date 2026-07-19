import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const publicHtml = readFileSync(new URL("../public/index.html", import.meta.url), "utf8");

test("public homepage keeps a simplified bilingual workout-plan flow", () => {
  assert.match(publicHtml, /Tạo một kế hoạch tập luyện gọn, rõ và dễ bắt đầu\./);
  assert.match(publicHtml, /Build a clear workout plan you can start right away\./);
  assert.match(publicHtml, /Thông tin tập luyện/);
  assert.match(publicHtml, /Training profile/);
  assert.match(publicHtml, /data-lang-choice="vi"/);
  assert.match(publicHtml, /data-lang-choice="en"/);
  assert.match(publicHtml, /Preset suggestions are recommended\./);
  assert.match(publicHtml, /Nên chọn từ các gợi ý có sẵn trước\./);
  assert.match(publicHtml, /Use the bilingual suggestions below first\./);
  assert.match(publicHtml, /Các gợi ý bên dưới đã kèm nghĩa tiếng Việt\./);
  assert.match(publicHtml, /id="injuries_or_limitations_presets"/);
  assert.match(publicHtml, /id="exercise_preferences_presets"/);
  assert.match(publicHtml, /profile-fields\.mjs/);
  assert.match(publicHtml, /Other/);
  assert.match(publicHtml, /Occasional knee discomfort/);
  assert.match(publicHtml, /Strength training/);
  assert.match(publicHtml, /Low-impact cardio/);
});

test("public homepage no longer exposes project-process messaging", () => {
  assert.doesNotMatch(publicHtml, /MVP Cloudflare/);
  assert.doesNotMatch(publicHtml, /Phiên bản công khai này chạy trên Cloudflare Worker/);
  assert.doesNotMatch(publicHtml, /Phản hồi gắn với đúng request tạo kế hoạch/);
  assert.doesNotMatch(publicHtml, /learning/i);
  assert.doesNotMatch(publicHtml, /interview/i);
});
