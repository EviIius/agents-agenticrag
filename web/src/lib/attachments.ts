import { ApiError } from "./api";
export async function prepareImage(file: File): Promise<File> {
  const image = await createImageBitmap(file);
  const scale = Math.min(1, 2048 / Math.max(image.width, image.height));
  const canvas = document.createElement("canvas");
  canvas.width = Math.round(image.width * scale);
  canvas.height = Math.round(image.height * scale);
  const context = canvas.getContext("2d")!;
  context.drawImage(image, 0, 0, canvas.width, canvas.height);
  image.close();
  const hasAlpha = context
    .getImageData(0, 0, canvas.width, canvas.height)
    .data.some((v, i) => i % 4 === 3 && v < 255);
  const mime = hasAlpha ? "image/png" : "image/jpeg";
  const blob = await new Promise<Blob>((resolve, reject) =>
    canvas.toBlob(
      (b) => (b ? resolve(b) : reject(new Error("Cannot resize image"))),
      mime,
      0.9,
    ),
  );
  return new File(
    [blob],
    file.name.replace(/\.[^.]+$/, "") + (hasAlpha ? ".png" : ".jpg"),
    { type: mime },
  );
}

/** Browser transport progress; audio bytes are never read into JS memory. */
export function uploadWithProgress(
  file: File,
  onProgress: (percent: number) => void,
  signal: AbortSignal,
): Promise<import("./api").Attachment> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    const abort = () => xhr.abort();
    const done = () => signal.removeEventListener("abort", abort);
    xhr.open("POST", "/api/attachments");
    xhr.upload.onprogress = (event) => {
      if (event.lengthComputable)
        onProgress(Math.round((event.loaded / event.total) * 100));
    };
    xhr.onload = () => {
      done();
      try {
        const data = JSON.parse(xhr.responseText);
        if (xhr.status >= 200 && xhr.status < 300) resolve(data);
        else
          reject(
            new ApiError(
              data.error?.code ?? "http_error",
              data.error?.message ?? "Upload didn't finish",
            ),
          );
      } catch {
        reject(new Error("Upload didn't finish"));
      }
    };
    xhr.onerror = () => {
      done();
      reject(new Error("Upload didn't finish"));
    };
    xhr.onabort = () => {
      done();
      reject(new DOMException("Upload cancelled", "AbortError"));
    };
    signal.addEventListener("abort", abort, { once: true });
    if (signal.aborted) {
      done();
      reject(new DOMException("Upload cancelled", "AbortError"));
      return;
    }
    const form = new FormData();
    form.append("file", file);
    xhr.send(form);
  });
}
