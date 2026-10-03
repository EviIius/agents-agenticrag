import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1, refetchOnWindowFocus: true } },
});
import { Outlet } from "react-router";
import { Toaster } from "sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { ThemeProvider } from "@/components/app/ThemeProvider";
import { useMediaQuery } from "@/hooks/useMediaQuery";
export default function App() {
  const phone = useMediaQuery("(max-width: 639px)");
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <TooltipProvider>
          <Outlet />
          <Toaster
            position={phone ? "top-center" : "bottom-right"}
            closeButton
            visibleToasts={1}
            duration={4500}
            toastOptions={{ className: "font-sans" }}
          />
        </TooltipProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}
