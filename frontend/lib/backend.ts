/** Server-to-server configuration only. Browsers use same-origin /api routes. */
export function backendUrl(): string {
  const value = process.env.INTERNAL_API_URL;
  if (!value) throw new Error("INTERNAL_API_URL is required on the Next.js server");
  let parsed: URL;
  try { parsed = new URL(value); } catch { throw new Error("Invalid INTERNAL_API_URL"); }
  if (!["http:", "https:"].includes(parsed.protocol)) throw new Error("Invalid INTERNAL_API_URL");
  return value.replace(/\/$/, "");
}

/** Browser proxy cannot mint identities or access retired product APIs. */
export function isBrowserApiPath(path: string[]): boolean {
  if (!path.length || path.some(segment => segment === "." || segment === ".." || segment.includes("/") || segment.includes("\\"))) return false;
  return !["auth", "chat", "profile", "content", "assessment"].includes(path[0]);
}
