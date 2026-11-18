let csrf = "";
export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message);
  }
}
export function setCsrf(value: string) {
  csrf = value;
}
export function api<T = void>(path: string, options?: RequestInit): Promise<T>;
export async function api(
  path: string,
  options: RequestInit = {},
): Promise<unknown> {
  const response = await fetch(`/api${path}`, {
    ...options,
    credentials: "same-origin",
    headers: {
      "Content-Type": "application/json",
      "X-CSRF-Token": csrf,
      ...options.headers,
    },
  });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    const message =
      typeof data.detail === "string"
        ? data.detail
        : "Проверьте заполнение полей и повторите попытку";
    if (response.status === 401 && path !== "/auth/login")
      window.dispatchEvent(new Event("session-expired"));
    throw new ApiError(message, response.status);
  }
  return response.status === 204 ? undefined : response.json();
}
export function errorMessage(error: unknown) {
  return error instanceof Error ? error.message : "Не удалось выполнить запрос";
}
