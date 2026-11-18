import { afterEach, expect, it, vi } from "vitest";
import { api, setCsrf } from "./api";

afterEach(() => {
  vi.unstubAllGlobals();
  setCsrf("");
});
it("sends cookies and session-bound CSRF on writes", async () => {
  const fetchMock = vi.fn().mockResolvedValue({
    ok: true,
    status: 200,
    json: async () => ({ id: 1 }),
  });
  vi.stubGlobal("fetch", fetchMock);
  setCsrf("session-token");
  await api("/profile", {
    method: "PATCH",
    body: JSON.stringify({ name: "Анна" }),
  });
  expect(fetchMock).toHaveBeenCalledWith(
    "/api/profile",
    expect.objectContaining({
      credentials: "same-origin",
      headers: expect.objectContaining({ "X-CSRF-Token": "session-token" }),
    }),
  );
});
it("shows server errors instead of pretending a request succeeded", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok: false,
      status: 403,
      json: async () => ({ detail: "Нет доступа" }),
    }),
  );
  await expect(api("/projects")).rejects.toThrow("Нет доступа");
});
it("handles logout without parsing an empty body", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true, status: 204 }));
  await expect(
    api("/auth/logout", { method: "POST" }),
  ).resolves.toBeUndefined();
});
it("notifies the session when a protected request expires", async () => {
  const expired = vi.fn();
  window.addEventListener("session-expired", expired);
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok: false,
      status: 401,
      json: async () => ({ detail: "Войдите в аккаунт" }),
    }),
  );
  try {
    await expect(api("/profile")).rejects.toMatchObject({ status: 401 });
    expect(expired).toHaveBeenCalledOnce();
  } finally {
    window.removeEventListener("session-expired", expired);
  }
});
