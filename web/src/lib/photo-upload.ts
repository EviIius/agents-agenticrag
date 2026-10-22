import { ApiError } from "./api";

/** Safari can render some camera photos that the Mac codec cannot decode. */
async function browserPreview(file: File, signal: AbortSignal) {
  const image = new Image();
  const url = URL.createObjectURL(file);
  const abort = () => {
    image.src = "";
  };
  signal.addEventListener("abort", abort, { once: true });
  try {
    signal.throwIfAborted();
    image.src = url;
    await image.decode();
    signal.throwIfAborted();
    const width = image.naturalWidth,
      height = image.naturalHeight;
    if (!width || !height || width * height > 100_000_000)
      throw new Error("Choose a photo up to 100 megapixels.");
    const scale = Math.min(1, 2048 / Math.max(width, height));
    const canvas = document.createElement("canvas");
    canvas.width = Math.max(1, Math.round(width * scale));
    canvas.height = Math.max(1, Math.round(height * scale));
    const context = canvas.getContext("2d");
    if (!context) throw new Error("Couldn't convert this photo.");
    context.drawImage(image, 0, 0, canvas.width, canvas.height);
    const preview = await new Promise<Blob>((resolve, reject) =>
      canvas.toBlob((blob) => {
        if (blob) resolve(blob);
        else reject(new Error("Couldn't convert this photo."));
      }, "image/png"),
    );
    signal.throwIfAborted();
    return { preview, width, height };
  } finally {
    signal.removeEventListener("abort", abort);
    image.src = "";
    URL.revokeObjectURL(url);
  }
}

export async function uploadPhoto(
  chat: string,
  file: File,
  signal: AbortSignal,
): Promise<Response> {
  const form = new FormData();
  // The original is always uploaded unchanged, including on the fallback path.
  form.append("file", file, "photo");
  const send = () =>
    fetch(`/api/chats/${chat}/image-references`, {
      method: "POST",
      body: form,
      signal,
    });
  const first = await send();
  if (first.status !== 422) return first;
  const body = await first
    .clone()
    .json()
    .catch(() => ({}));
  if (body.error?.code !== "image_unreadable") return first;
  try {
    const converted = await browserPreview(file, signal);
    form.append("browser_preview", converted.preview, "preview.png");
    form.append("original_width", String(converted.width));
    form.append("original_height", String(converted.height));
    signal.throwIfAborted();
    return await send();
  } catch (error) {
    signal.throwIfAborted();
    if (error instanceof TypeError) throw error;
    throw new ApiError(
      "image_unreadable",
      "Couldn't open this photo. Try choosing it from Photo Library again.",
    );
  }
}
