import { createBrowserRouter } from "react-router";
import App from "./App";
import { AppShell } from "@/components/app/AppShell";
export const router = createBrowserRouter([
  {
    element: <App />,
    HydrateFallback: () => (
      <p role="status" className="p-6 text-fg-2">
        Loading Workbench…
      </p>
    ),
    children: [
      { path: "/", element: <AppShell /> },
      { path: "/c/:chatId", element: <AppShell /> },
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
