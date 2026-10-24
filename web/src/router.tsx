import config from "../../shared/config.json";
import { createBrowserRouter } from "react-router";
import { LiveAppShell } from "@/components/app/LiveAppShell";
import App from "./App";
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
      {
        path: "/design/chat/:chatId?",
        lazy: async () => {
          const { AppShell } = await import("@/components/app/AppShell");
          return { Component: AppShell };
        },
      },
      {
        path: "/design",
        lazy: async () => {
          const [{ AppShell }, { DesignPage }] = await Promise.all([
            import("@/components/app/AppShell"),
            import("@/design/DesignPage"),
          ]);
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
