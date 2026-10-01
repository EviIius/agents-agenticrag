import type { RefObject } from "react";
import { UserMessage } from "./UserMessage";
import { AssistantMessage } from "./AssistantMessage";
export function Thread({
  message,
  scrollRef,
  onAboveBottomChange,
}: {
  message?: string;
  scrollRef: RefObject<HTMLDivElement | null>;
  onAboveBottomChange: (above: boolean) => void;
}) {
  return (
    <div
      ref={scrollRef}
      className="thread-scroll"
      data-testid="thread"
      role="log"
      aria-live="off"
      aria-label="Conversation"
      onScroll={() => {
        const element = scrollRef.current;
        if (element)
          onAboveBottomChange(
            element.scrollHeight - element.clientHeight - element.scrollTop >
              120,
          );
      }}
    >
      <div className="thread-column">
        <UserMessage text={message} />
        <AssistantMessage />
      </div>
    </div>
  );
}
