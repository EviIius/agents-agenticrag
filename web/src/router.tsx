import config from "../../shared/config.json";
import { createBrowserRouter } from "react-router";
import { LiveAppShell } from "@/components/app/LiveAppShell";
import App from "./App";
import { AppShell } from "@/components/app/AppShell";
export const router = createBrowserRouter([
  {
    element: <App />,
    HydrateFallback: () => (
      <p role="status" className="p-6 text-fg-2">
        Loading {config.APP_NAME}…
      </p>
    ),
    children: [
      {
        element: <LiveAppShell />,
        children: [
          { index: true, element: null },
          { path: "/c/:chatId", element: null },
          ...[
            "/workflows",
            "/workflows/new",
            "/workflows/runs",
            "/workflows/runs/:runId",
            "/workflows/:workflowId/runs/:runId",
          ].map((path) => ({
            path,
            lazy: async () => {
              const { WorkflowsPage } =
                await import("@/components/workflows/WorkflowsPage");
              return { Component: WorkflowsPage };
            },
          })),
          {
            path: "/workflows/:workflowId",
            lazy: async () => {
              const { Studio } =
                await import("@/components/workflows/studio/Studio");
              return { Component: Studio };
            },
          },
          {
            path: "/images",
            lazy: async () => {
              const { ImagesPage } =
                await import("@/components/images/ImagesPage");
              return { Component: ImagesPage };
            },
          },
        ],
      },
      { path: "/design/chat/:chatId?", element: <AppShell /> },
      {
        path: "/design",
        lazy: async () => {
          const { DesignPage } = await import("@/design/DesignPage");
          return {
            Component: () => (
              <AppShell>
                <DesignPage />
              </AppShell>
            ),
          };
        },
      },
    ],
  },
]);
