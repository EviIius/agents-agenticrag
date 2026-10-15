import { ApiError } from "./api";
export function isImageFile(file: File): boolean {
  return (
    file.type.startsWith("image/") ||
    /\.(png|jpe?g|webp|gif|heic|heif)$/i.test(file.name)
  );
}

export function isHeifHeader(bytes: Uint8Array): boolean {
  if (bytes.length < 16) return false;
  const text = (start: number) =>
    String.fromCharCode(...bytes.slice(start, start + 4));
  if (text(4) !== "ftyp") return false;
  const size = new DataView(
    bytes.buffer,
    bytes.byteOffset,
    bytes.byteLength,
  ).getUint32(0);
  if (size < 16) return false;
  const brands = [text(8)];
  for (let i = 16; i + 4 <= Math.min(size, bytes.length); i += 4)
    brands.push(text(i));
  return (
    !brands.some((brand) => ["avif", "avis"].includes(brand)) &&
    brands.some((brand) =>
      ["heic", "heix", "hevc", "hevx", "heim", "heis", "mif1", "msf1"].includes(
        brand,
      ),
    )
  );
}

export async function prepareImage(file: File): Promise<File> {
  // A renamed HEIC is still HEIC. Let the Mac's bounded codec normalize it.
  if (isHeifHeader(new Uint8Array(await file.slice(0, 256).arrayBuffer()))) {
    const name = /\.(png|jpe?g|webp|gif|heic|heif)$/i.test(file.name)
      ? file.name
      : file.name + ".heic";
    return new File([file], name, { type: "image/heic" });
  }
  let image: ImageBitmap;
  try {
    image = await createImageBitmap(file);
  } catch {
    throw new ApiError(
      "image_unreadable",
      "Couldn't open this image. Export it as a JPEG or PNG and try again.",
    );
  }
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
