import { useEffect, useRef, useState } from "react";
export function useCopyFeedback() {
  const [copied, setCopied] = useState(false),
    [failed, setFailed] = useState(false);
  const timer = useRef<ReturnType<typeof setTimeout>>(undefined);
  useEffect(() => () => clearTimeout(timer.current), []);
  const confirm = () => {
    clearTimeout(timer.current);
    setFailed(false);
    setCopied(true);
    timer.current = setTimeout(() => setCopied(false), 1500);
  };
  const copy = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      confirm();
    } catch {
      clearTimeout(timer.current);
      setCopied(false);
      setFailed(true);
    }
  };
  return { copied, failed, confirm, copy };
}
