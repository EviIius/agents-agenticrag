import { useMediaQuery } from "./useMediaQuery";
import { useUI } from "@/stores/ui";

/** OS preference and the user's Always preference both disable JS-driven motion. */
export function useReducedMotion() {
  const system = useMediaQuery("(prefers-reduced-motion: reduce)");
  const always = useUI((state) => state.reduceMotion === "always");
  return system || always;
}
