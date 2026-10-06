import assert from "node:assert/strict";
import test from "node:test";
import { loadTs } from "./load-ts.mjs";
const { backendUrl, isBrowserApiPath } = await loadTs("../lib/backend.ts");
const { internalHeaders } = await loadTs("../lib/internal-auth.ts");

test("one server API origin is required", () => {
  const before = process.env.INTERNAL_API_URL;
  try {
    delete process.env.INTERNAL_API_URL;
    assert.throws(backendUrl, /required/);
    process.env.INTERNAL_API_URL = "http://backend:8000/";
    assert.equal(backendUrl(), "http://backend:8000");
    process.env.INTERNAL_API_URL = "file:///private";
    assert.throws(backendUrl, /Invalid/);
  } finally {
    if (before === undefined) delete process.env.INTERNAL_API_URL;
    else process.env.INTERNAL_API_URL = before;
  }
});

test("BFF identity comes from the resolved session", () => {
  const before = process.env.INTERNAL_API_KEY;
  try {
    process.env.INTERNAL_API_KEY = "test-only-internal-value";
    assert.deepEqual(internalHeaders("session@example.com"), {
      "x-user-email": "session@example.com", "x-internal-token": "test-only-internal-value",
    });
    delete process.env.INTERNAL_API_KEY;
    assert.throws(() => internalHeaders("session@example.com"), /not set/);
  } finally {
    if (before === undefined) delete process.env.INTERNAL_API_KEY;
    else process.env.INTERNAL_API_KEY = before;
  }
});

test("browser proxy cannot invoke server identity sync or legacy tools", () => {
  for (const path of [["auth", "sync"], ["chat", "message"], ["profile", "update"], ["content", "articles"], ["assessment", "quiz"], ["courses", "..", "auth"], ["courses/auth"], []]) {
    assert.equal(isBrowserApiPath(path), false);
  }
  assert.equal(isBrowserApiPath(["courses", "course-id", "tutor"]), true);
  assert.equal(isBrowserApiPath(["me"]), true);
});
