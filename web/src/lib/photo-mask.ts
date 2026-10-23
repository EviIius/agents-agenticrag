import type { PhotoSelection } from "@/hooks/usePhotoEdit";

export type PhotoStroke = PhotoSelection["strokes"][number];

/** Browser edge antialiasing is approximate; the CPU mask is authoritative. */
export function photoMask(
  width: number,
  height: number,
  strokes: PhotoStroke[],
) {
  const mask = document.createElement("canvas");
  mask.width = width;
  mask.height = height;
  const context = mask.getContext("2d", { willReadFrequently: true })!;
  context.lineCap = context.lineJoin = "round";
  context.fillStyle = context.strokeStyle = "white";
  for (const stroke of strokes) {
    context.globalCompositeOperation =
      stroke.operation === "erase" ? "destination-out" : "source-over";
    const radius = Math.max(
      1,
      Math.round(stroke.radius * Math.min(width, height)),
    );
    context.lineWidth = 2 * radius + 1;
    context.beginPath();
    stroke.points.forEach(([x, y], index) => {
      const px = Math.round(x * (width - 1));
      const py = Math.round(y * (height - 1));
      if (index) context.lineTo(px, py);
      else context.moveTo(px, py);
    });
    context.stroke();
    for (const [x, y] of stroke.points) {
      context.beginPath();
      context.arc(
        Math.round(x * (width - 1)),
        Math.round(y * (height - 1)),
        radius,
        0,
        2 * Math.PI,
      );
      context.fill();
    }
  }
  return mask;
}

export function maskCoverage(mask: HTMLCanvasElement) {
  const data = mask
    .getContext("2d")!
    .getImageData(0, 0, mask.width, mask.height).data;
  let selected = 0;
  for (let i = 3; i < data.length; i += 4) if (data[i] > 127) selected++;
  return { selected, percent: (100 * selected) / (mask.width * mask.height) };
}
