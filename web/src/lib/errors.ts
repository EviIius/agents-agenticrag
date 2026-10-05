import type { Message, Model, Bootstrap } from "./api";
export function errorCopy(
  code: string,
  detail: string,
  model?: Model | null,
  connection?: Bootstrap["connections"][number],
  context?: number,
) {
  const name = connection?.name ?? "Ollama",
    host = connection?.base_url ?? "the configured address",
    title = model?.display_name ?? "This model",
    n = context ?? model?.context_length ?? 8192;
  const copy: Record<string, string> = {
    preset_name_taken:
      "A preset with this name already exists. Choose another name.",
    document_no_text:
      "This PDF has no selectable text. Scanned documents aren't supported yet.",
    document_encrypted:
      "This PDF is password-protected. Remove the password and try again.",
    document_unreadable: "Couldn't read this file. It may be damaged.",
    document_too_large: "Documents can be up to 50 MB and 1,500 pages.",
    document_timeout: "This document took too long to read.",
    runtime_unreachable: `Can't reach ${name} at ${host}. Is it running?`,
    model_not_found: `${title} isn't available on ${name} anymore.`,
    model_load_failed: `${name} couldn't load ${title}, most likely not enough memory. Eject other models or pick a smaller one.`,
    context_overflow: `This chat is longer than ${title}'s context window (${n} tokens).`,
    idle_timeout: "The model stopped responding. The partial answer is kept.",
    interrupted: "Interrupted because the server restarted.",
    provider_error: `${name} returned an error: ${detail}`,
  };
  return copy[code] ?? "Something went wrong. Try again.";
}
export function messageError(
  message: Message,
  models: Model[],
  connections: Bootstrap["connections"],
) {
  const model =
    models.find(
      (m) =>
        m.model_id === message.model?.model_id &&
        m.connection_id === message.model?.connection_id,
    ) ??
    (message.model
      ? ({ display_name: message.model.display_name } as Model)
      : undefined);
  return errorCopy(
    message.error?.code ?? "provider_error",
    message.error?.message ?? "",
    model,
    connections.find((c) => c.id === message.model?.connection_id),
    message.stats?.context_length,
  );
}

export function failureCopy(error: unknown) {
  return errorCopy(
    error && typeof error === "object" && "code" in error
      ? String(error.code)
      : "unknown",
    "",
  );
}
export function failureDetail(error: unknown) {
  return error instanceof Error ? error.message : String(error);
}
