import { useEffect, useRef } from "react";
import { Streamdown } from "streamdown";
import { createCodePlugin } from "@streamdown/code";
import { math } from "@streamdown/math";
import "katex/dist/katex.min.css";
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
  const container = useRef<HTMLDivElement>(null);
  const rendered = sources ? renderCitations(text, sources.length) : text;
  useEffect(() => {
    const root = container.current;
    if (!root) return;
    const makeScrollableFocusable = () => {
      root
        .querySelectorAll<HTMLElement>(
          '[data-streamdown="code-block-body"], [data-streamdown="table-wrapper"]',
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
    <div ref={container} className="min-w-0">
      <Streamdown
        className="prose-answer"
        skipHtml
        remarkRehypeOptions={{ allowDangerousHtml: false }}
        plugins={{ code, math }}
        shikiTheme={["github-light-default", "github-dark-default"]}
        parseIncompleteMarkdown={streaming}
        isAnimating={streaming}
        codeBlockMaxHeight={480}
        controls={{ code: { copy: true, download: false }, table: false }}
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
