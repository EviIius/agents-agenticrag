import { useEffect, useRef } from "react";
import { Streamdown } from "streamdown";
import { createCodePlugin } from "@streamdown/code";
import { math } from "@streamdown/math";
import "katex/dist/katex.min.css";
const code = createCodePlugin({
  themes: ["github-light-default", "github-dark-default"],
});
export default function Markdown({
  text,
  streaming = false,
}: {
  text: string;
  streaming?: boolean;
}) {
  const container = useRef<HTMLDivElement>(null);
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
          a: ({ href, children }) => (
            <a href={href} target="_blank" rel="noopener noreferrer">
              {children}
            </a>
          ),
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
        {text}
      </Streamdown>
    </div>
  );
}
