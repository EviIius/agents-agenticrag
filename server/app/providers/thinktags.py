from .base import ProviderEvent, ReasoningDelta, TextDelta


class ThinkSplitter:
    def __init__(self) -> None:
        self.state = "start"
        self.pending = ""
        self.text_emitted = False

    def feed(self, chunk: str) -> list[ProviderEvent]:
        self.pending += chunk
        out: list[ProviderEvent] = []
        if self.state == "start":
            candidate = self.pending.lstrip()
            if not candidate or "<think>".startswith(candidate):
                return out
            if candidate.startswith("<think>"):
                self.pending = candidate[7:]
                self.state = "think"
            else:
                self.state = "answer"
        if self.state == "think":
            index = self.pending.find("</think>")
            if index >= 0:
                if index:
                    out.append(ReasoningDelta(self.pending[:index]))
                self.pending = self.pending[index + 8 :]
                self.state = "answer"
            else:
                hold = max(
                    (n for n in range(1, 8) if "</think>".startswith(self.pending[-n:])), default=0
                )
                emit = self.pending[:-hold] if hold else self.pending
                self.pending = self.pending[-hold:] if hold else ""
                if emit:
                    out.append(ReasoningDelta(emit))
        if self.state == "answer":
            text = self.pending if self.text_emitted else self.pending.lstrip("\n")
            self.pending = ""
            if text:
                self.text_emitted = True
                out.append(TextDelta(text))
        return out

    def end(self) -> list[ProviderEvent]:
        text, self.pending = self.pending, ""
        if not text:
            return []
        return [ReasoningDelta(text)] if self.state == "think" else [TextDelta(text)]
