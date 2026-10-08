import { settle } from "./helpers";
import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { mkdir } from "node:fs/promises";
for (const width of [390, 1440])
  for (const theme of ["light", "dark"]) {
    test(`clear audio preserves outputs ${width} ${theme}`, async ({
      page,
      request,
    }) => {
      await page.setViewportSize({ width, height: 900 });
      for (const item of await (
        await request.get("/api/attachments/pending")
      ).json())
        await request.delete(`/api/attachments/${item.id}`);
      await request.patch("/api/settings", {
        data: {
          "transcription.keep_audio": true,
          "appearance.theme": theme,
          default_model_id: "fake-chat",
        },
      });
      const response = await request.post("/api/attachments", {
        multipart: {
          file: {
            name: "Synthetic storage.wav",
            mimeType: "audio/wav",
            buffer: Buffer.from("fake"),
          },
        },
      });
      const item = await response.json();
      try {
        await expect
          .poll(
            async () =>
              (
                await (
                  await request.get(`/api/attachments/${item.id}/info`)
                ).json()
              ).transcript.status,
          )
          .toBe("ready");
        await page.goto("/");
        await expect(page.getByTestId("audio-chip")).toContainText(
          "Synthetic storage.wav",
        );
        await page.keyboard.press("Control+,");
        await page
          .getByRole("button", { name: "Transcription", exact: true })
          .click();
        await expect(
          page.getByRole("switch", {
            name: "Keep original audio after transcription",
          }),
        ).toBeChecked();
        await page
          .getByRole("button", { name: "Clear stored audio", exact: true })
          .click();
        const confirmation = page.getByRole("alertdialog", {
          name: "Clear stored audio?",
        });
        await expect(
          confirmation.getByRole("button", { name: "Cancel", exact: true }),
        ).toBeVisible();
        await confirmation
          .getByRole("button", { name: "Cancel", exact: true })
          .click();
        expect(
          (await (await request.get(`/api/attachments/${item.id}/info`)).json())
            .audio_available,
        ).toBe(true);
        await page
          .getByRole("button", { name: "Clear stored audio", exact: true })
          .click();
        await mkdir("../artifacts/phase-3", { recursive: true });
        await settle(page);
        await page.screenshot({
          animations: "disabled",
          path: `../artifacts/phase-3/audio-clear-${width}-${theme}-fake.png`,
        });
        await settle(page);
        expect(
          (await new AxeBuilder({ page }).analyze()).violations.filter((v) =>
            ["serious", "critical"].includes(v.impact ?? ""),
          ),
        ).toEqual([]);
        await confirmation
          .getByRole("button", { name: "Remove audio copies", exact: true })
          .click();
        await expect(confirmation).not.toBeVisible();
        await page.keyboard.press("Escape");
        await expect(page.getByTestId("audio-chip")).toContainText(
          "Transcript saved · audio removed",
        );
        await page
          .getByRole("button", {
            name: "Recording actions for Synthetic storage.wav",
          })
          .click();
        await expect(
          page.getByRole("menuitem", { name: "Download audio", exact: true }),
        ).toHaveCount(0);
        await expect(
          page.getByRole("menuitem", { name: "Transcribe again", exact: true }),
        ).toBeDisabled();
        for (const format of ["txt", "srt", "json"])
          expect(
            (
              await request.get(
                `/api/attachments/${item.id}/transcript/download?format=${format}`,
              )
            ).status(),
          ).toBe(200);
      } finally {
        await request.delete(`/api/attachments/${item.id}`);
        await request.patch("/api/settings", {
          data: { "transcription.keep_audio": false },
        });
      }
    });
  }
