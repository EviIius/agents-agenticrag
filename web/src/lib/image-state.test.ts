import { describe, expect, it } from "vitest";
import { imageTurnStatus } from "./image-state";
import {
  claimImageReveal,
  receiveImages,
  useImageJobs,
  type ImageJob,
} from "./image-events";

const job = (changes: Partial<ImageJob> = {}): ImageJob => ({
  id: "fake-status",
  prompt: "Synthetic circle",
  seed: 1,
  mode: "generate",
  width: 1024,
  height: 1024,
  export_bytes: 0,
  state: "running",
  stage: "Generating image",
  completed_steps: 2,
  steps: 4,
  created_at: "2026-10-13T15:00:00Z",
  updated_at: "2026-10-13T15:00:10Z",
  elapsed_seconds: 10,
  image_bytes: 0,
  metadata_bytes: 0,
  ...changes,
});
describe("Image turn truth", () => {
  it("uses actual state, steps and queue position rather than elapsed time", () => {
    expect(imageTurnStatus([job()])).toBe("Creating · step 3 of 4");
    expect(imageTurnStatus([job({ completed_steps: 4 })])).toBe(
      "Creating · step 4 of 4",
    );
    expect(imageTurnStatus([job({ stage: "Decoding image" })])).toBe(
      "Finishing",
    );
    expect(imageTurnStatus([job({ state: "preparing" })])).toBe(
      "Loading the image model",
    );
    expect(
      imageTurnStatus([
        job({ state: "preparing", stage: "Making room for images" }),
      ]),
    ).toBe("Making room for images");
    expect(
      imageTurnStatus(
        [job({ state: "queued" })],
        [job({ id: "older", created_at: "2026-10-13T14:59:00Z" })],
      ),
    ).toBe("Waiting for your Mac · after 1 image");
    expect(
      imageTurnStatus([job({ state: "complete", image_bytes: 100 })]),
    ).toBe("1 image · 10 s");
    expect(imageTurnStatus([job({ state: "complete" })])).toBe("Image removed");
  });
  it("describes terminal failure, interruption and cancellation explicitly", () => {
    expect(imageTurnStatus([job({ state: "failed" })])).toBe(
      "Couldn't create this image",
    );
    expect(imageTurnStatus([job({ state: "interrupted" })])).toBe(
      "Interrupted — retry available",
    );
    expect(imageTurnStatus([job({ state: "cancelled" })])).toBe("Cancelled");
    expect(imageTurnStatus([job({ state: "cancelling" })])).toBe("Cancelling…");
  });
  it("only reveals a session completion once; history and stale events cannot reveal", () => {
    useImageJobs.setState({ jobs: {} });
    receiveImages([job({ id: "history", state: "complete" })]);
    expect(claimImageReveal("history")).toBe(false);
    receiveImages([job({ id: "session" })]);
    receiveImages([
      job({
        id: "session",
        state: "complete",
        updated_at: "2026-10-13T15:00:11Z",
      }),
    ]);
    expect(claimImageReveal("session")).toBe(true);
    expect(claimImageReveal("session")).toBe(false);
    receiveImages([job({ id: "session", state: "queued" })]);
    expect(useImageJobs.getState().jobs.session.state).toBe("complete");
  });
});
