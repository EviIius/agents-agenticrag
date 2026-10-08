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
      { path: "/", element: <LiveAppShell /> },
      { path: "/c/:chatId", element: <LiveAppShell /> },
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
