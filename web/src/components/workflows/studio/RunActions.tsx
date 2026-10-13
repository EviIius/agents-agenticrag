import { createContext, useContext } from "react";
export const RunActions = createContext<{
  defId: string;
  revision: number;
  act: (mode: "run" | "test", nodeId: string) => void;
} | null>(null);
export const useRunActions = () => useContext(RunActions);
