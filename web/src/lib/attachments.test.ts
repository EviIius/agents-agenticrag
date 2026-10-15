import { afterEach, describe, expect, it, vi } from "vitest";
import { isHeifHeader, isImageFile, prepareImage } from "./attachments";

const heic = new Uint8Array([
  0, 0, 0, 24, 102, 116, 121, 112, 104, 101, 105, 99, 0, 0, 0, 0, 104, 101, 105,
  99, 109, 105, 102, 49,
]);
afterEach(() => vi.unstubAllGlobals());
describe("image upload preparation", () => {
  it("recognizes empty browser MIME from the image extension", () => {
    expect(isImageFile(new File(["fake"], "fake.PNG"))).toBe(true);
    expect(isImageFile(new File([heic], "fake.HEIC"))).toBe(true);
    expect(isImageFile(new File(["text"], "fake.txt"))).toBe(false);
  });
  it("passes actual HEIC bytes to the Mac codec even when named PNG", async () => {
    const decode = vi.fn();
    vi.stubGlobal("createImageBitmap", decode);
    const result = await prepareImage(
      new File([heic], "fake.png", { type: "image/png" }),
    );
    expect(result.type).toBe("image/heic");
    expect(isHeifHeader(new Uint8Array(await result.arrayBuffer()))).toBe(true);
    expect(result.name).toBe("fake.png");
    expect(decode).not.toHaveBeenCalled();
  });
  it("gives otherwise unnamed HEIC data a supported extension", async () => {
    const result = await prepareImage(
      new File([heic], "fake-photo", { type: "image/heic" }),
    );
    expect(result.name).toBe("fake-photo.heic");
  });
  it("reports unreadable ordinary images with useful copy", async () => {
    vi.stubGlobal(
      "createImageBitmap",
      vi.fn().mockRejectedValue(new Error("decode")),
    );
    await expect(
      prepareImage(new File(["invalid"], "fake.png")),
    ).rejects.toThrow("JPEG or PNG");
  });
  it("does not treat PNG, random bytes or AVIF as HEIC", () => {
    expect(isHeifHeader(new Uint8Array([137, 80, 78, 71]))).toBe(false);
    const avif = heic.slice();
    avif.set([97, 118, 105, 102], 8);
    expect(isHeifHeader(avif)).toBe(false);
  });
});
