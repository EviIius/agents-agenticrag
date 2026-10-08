import { Check, Copy } from "lucide-react";
import { useEffect, useRef } from "react";
import { useReducedMotion } from "@/hooks/useReducedMotion";
import { Streamdown } from "streamdown";
import { createCodePlugin } from "@streamdown/code";
import { math } from "@streamdown/math";
import "katex/dist/katex.min.css";
import "streamdown/styles.css";
import { useCopyFeedback } from "@/hooks/useCopyFeedback";
import type { Source } from "@/lib/api";
import { renderCitations } from "@/lib/citations";
import { CitationPill } from "./CitationPill";
const code = createCodePlugin({
  themes: ["github-light-default", "github-dark-default"],
});
export default function Markdown({
  text,
  streaming = false,
  sources,
}: {
  text: string;
  streaming?: boolean;
  sources?: Source[];
}) {
  const feedback = useCopyFeedback();
  const reduceMotion = useReducedMotion();
  const container = useRef<HTMLDivElement>(null);
  const rendered = sources ? renderCitations(text, sources.length) : text;
  useEffect(() => {
    const root = container.current;
    if (!root) return;
    const makeScrollableFocusable = () => {
      root
        .querySelectorAll<HTMLElement>(
          '[data-streamdown="code-block-body"], [data-streamdown="table-wrapper"], [data-streamdown="table-wrapper"] > div:has(> table)',
        )
        .forEach((element) => {
          element.tabIndex = 0;
          element.setAttribute("role", "region");
          element.setAttribute(
            "aria-label",
            element.dataset.streamdown === "code-block-body"
              ? "Code example"
              : "Answer table",
          );
        });
    };
    makeScrollableFocusable();
    const observer = new MutationObserver(makeScrollableFocusable);
    observer.observe(root, { childList: true, subtree: true });
    return () => observer.disconnect();
  }, []);
  return (
    <div
      ref={container}
      data-streaming={streaming || undefined}
      data-code-copied={feedback.copied || undefined}
      className="min-w-0"
    >
      <span role="status" aria-live="polite" className="sr-only">
        {feedback.failed ? "Couldn't copy. Try again." : ""}
      </span>
      <Streamdown
        className="prose-answer"
        skipHtml
        remarkRehypeOptions={{ allowDangerousHtml: false }}
        plugins={{ code, math }}
        shikiTheme={["github-light-default", "github-dark-default"]}
        parseIncompleteMarkdown={streaming}
        isAnimating={streaming}
        animated={
          streaming && !reduceMotion
            ? {
                animation: "fadeIn",
                duration: 200,
                easing: "ease-out",
                sep: "word",
              }
            : false
        }
        caret={streaming ? "block" : undefined}
        icons={{
          CheckIcon: () =>
            feedback.copied ? (
              <Check
                data-slot="copy-check"
                aria-hidden="true"
                className="size-3.5"
              />
            ) : (
              <Copy aria-hidden="true" className="size-3.5" />
            ),
        }}
        codeBlockMaxHeight={480}
        controls={{
          code: { copy: { onCopy: feedback.confirm }, download: false },
          table: false,
        }}
        components={{
          a: ({ href, children, node }) => {
            if (href?.startsWith("#cite-") && sources) {
              const selected = href
                .slice(6)
                .split("-")
                .map(Number)
                .map((n) => sources.find((s) => s.n === n))
                .filter((s): s is Source => !!s);
              const before = rendered.slice(
                0,
                node?.position?.start.offset ?? text.length,
              );
              const sentence = before.split(/[.!?\n]/).pop() ?? text;
              return <CitationPill sources={selected} sentence={sentence} />;
            }
            return (
              <a href={href} target="_blank" rel="noopener noreferrer">
                {children}
              </a>
            );
          },
          img: ({ src, alt }) => (
            <a
              href={typeof src === "string" ? src : undefined}
              target="_blank"
              rel="noopener noreferrer"
            >
              {alt || "View image"} ↗
            </a>
          ),
        }}
      >
        {rendered}
      </Streamdown>
    </div>
  );
}
