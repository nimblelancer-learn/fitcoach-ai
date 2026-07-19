import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const publicHtml = readFileSync(new URL("../public/index.html", import.meta.url), "utf8");

test("public homepage keeps preset helper functions inside the module script", () => {
  const scriptMatch = publicHtml.match(/<script type="module">([\s\S]*?)<\/script>/);
  assert.ok(scriptMatch, "expected a module script in public/index.html");

  const scriptBody = scriptMatch[1];
  assert.match(scriptBody, /function renderProfileFieldOptions\(\)/);
  assert.match(scriptBody, /function renderPresetCard\(fieldName, preset, checked\)/);
  assert.match(scriptBody, /function syncOtherVisibility\(fieldName\)/);
  assert.match(scriptBody, /applyStaticCopy\(\);/);
});

test("public homepage does not contain stray executable code after </html>", () => {
  const htmlCloseIndex = publicHtml.lastIndexOf("</html>");
  assert.notEqual(htmlCloseIndex, -1, "expected closing </html> tag");

  const trailing = publicHtml.slice(htmlCloseIndex + "</html>".length);
  assert.equal(trailing.trim(), "");
});
