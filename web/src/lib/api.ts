import type { components } from "./api-types";
export type Chat = components["schemas"]["Chat"];
export type Message = components["schemas"]["Message"];
export type Model = components["schemas"]["ModelInfo"];
export type Attachment = components["schemas"]["Attachment"];
export type Detail = components["schemas"]["ChatDetail"];
export type RunResponse = components["schemas"]["RunResponse"];
export type Bootstrap = components["schemas"]["Bootstrap"];
export type Source = components["schemas"]["Source"];
export type WebRead = components["schemas"]["WebRead"];
export type Params = components["schemas"]["Parameters"];
export class ApiError extends Error {
  constructor(
    public code: string,
    message: string,
  ) {
    super(message);
  }
}
export async function api<T>(
  url: string,
  body?: unknown,
  method?: string,
): Promise<T> {
  const response = await fetch("/api" + url, {
    method: method ?? (body === undefined ? "GET" : "POST"),
    headers:
      body instanceof FormData
        ? undefined
        : { "Content-Type": "application/json" },
    body:
      body === undefined
        ? undefined
        : body instanceof FormData
          ? body
          : JSON.stringify(body),
  });
  if (!response.ok) {
    const data = await response
      .json()
      .catch(() => ({ error: { message: "Connection unavailable" } }));
    throw new ApiError(
      data.error?.code ?? "http_error",
      data.error?.message ?? "Request failed",
    );
  }
  return response.status === 204
    ? (undefined as T)
    : (response.json() as Promise<T>);
}
export type Transcript = components["schemas"]["Transcript"];
export type TranscriptionStatus = components["schemas"]["TranscriptionStatus"];
export type TranscriptionEvent = components["schemas"]["TranscriptionEvent"];

export type Preset = components["schemas"]["Preset"];

export type Folder = components["schemas"]["Folder"];
export type BackupStatus = components["schemas"]["BackupStatus"];
