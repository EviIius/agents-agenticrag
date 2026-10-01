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
