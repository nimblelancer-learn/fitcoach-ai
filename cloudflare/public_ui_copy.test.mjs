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
  assert.match(publicHtml, /Use short English text in both free-text fields\./);
  assert.match(publicHtml, /Occasional knee discomfort/);
  assert.match(publicHtml, /Strength training/);
});

test("public homepage no longer exposes project-process messaging", () => {
  assert.doesNotMatch(publicHtml, /MVP Cloudflare/);
  assert.doesNotMatch(publicHtml, /Phiên bản công khai này chạy trên Cloudflare Worker/);
  assert.doesNotMatch(publicHtml, /Phản hồi gắn với đúng request tạo kế hoạch/);
  assert.doesNotMatch(publicHtml, /learning/i);
  assert.doesNotMatch(publicHtml, /interview/i);
});
