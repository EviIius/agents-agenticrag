import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { RouterProvider } from "react-router";
import { router } from "./router";
import { registerPWA } from "./lib/pwa";
import "./styles/fonts.css";
import "./styles/globals.css";
import "./styles/prose.css";
createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
);

void registerPWA();
