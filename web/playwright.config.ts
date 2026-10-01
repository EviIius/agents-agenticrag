import { defineConfig, devices } from "@playwright/test";
export default defineConfig({
  testDir: "./tests",
  fullyParallel: false,
  workers: 2,
  timeout: 45000,
  use: { baseURL: "http://127.0.0.1:5173", trace: "retain-on-failure" },
  reporter: [["list"]],
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
    {
      name: "webkit",
      use: { ...devices["iPhone 13"], viewport: { width: 390, height: 844 } },
    },
  ],
  webServer: [
    {
      command: "npm run dev -- --port 5173 --strictPort",
      url: "http://127.0.0.1:5173",
      reuseExistingServer: !process.env.CI,
    },
    {
      command:
        "cd .. && . scripts/tool-env.sh && uv run --directory server uvicorn tests.fake_runtime:app --host 127.0.0.1 --port 18080 --workers 1",
      url: "http://127.0.0.1:18080/api/tags",
      reuseExistingServer: !process.env.CI,
    },
  ],
});
