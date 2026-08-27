import assert from "node:assert/strict";
import test from "node:test";

import { resolveLanguage } from "../assets/site.js";


test("explicit supported language wins over browser preference", () => {
  assert.equal(
    resolveLanguage({ search: "?lang=ru", languages: ["en-US"] }),
    "ru",
  );
  assert.equal(
    resolveLanguage({ search: "?lang=en", languages: ["ru-RU"] }),
    "en",
  );
});

test("browser Russian maps to Russian and every other language falls back to English", () => {
  assert.equal(resolveLanguage({ search: "", languages: ["ru-RU"] }), "ru");
  assert.equal(resolveLanguage({ search: "", languages: ["uk-UA", "en-GB"] }), "en");
  assert.equal(resolveLanguage({ search: "", languages: ["de-DE"] }), "en");
});

test("unsupported or malformed query values cannot hide both languages", () => {
  assert.equal(resolveLanguage({ search: "?lang=de", languages: ["ru"] }), "ru");
  assert.equal(resolveLanguage({ search: "?lang=RU", languages: ["en"] }), "en");
  assert.equal(resolveLanguage({ search: "?lang=", languages: [] }), "en");
});
