import { Outlet } from "react-router";
import { Toaster } from "sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { ThemeProvider } from "@/components/app/ThemeProvider";
import { useMediaQuery } from "@/hooks/useMediaQuery";
export default function App() {
  const phone = useMediaQuery("(max-width: 639px)");
  return (
    <ThemeProvider>
      <TooltipProvider>
        <Outlet />
        <Toaster
          position={phone ? "bottom-center" : "bottom-right"}
          toastOptions={{ className: "font-sans" }}
        />
      </TooltipProvider>
    </ThemeProvider>
  );
}
