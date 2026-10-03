"""Glossary of names that transcripts garble.

File format, one entry per line:

    CORRECT = wrong form, another wrong form
    CORRECT

Lines starting with # are comments. The correct forms are given to Whisper as
a vocabulary hint; the wrong forms are replaced after transcription.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Tuple

# Whisper accepts at most ~224 prompt tokens; stay well inside that.
MAX_PROMPT_CHARS = 600


class Glossary:
    def __init__(self, entries: List[Tuple[str, List[str]]]):
        self.entries = entries
        self._rules = self._compile(entries)

    @classmethod
    def load(cls, path: Path) -> "Glossary":
        entries: List[Tuple[str, List[str]]] = []
        if not path.exists():
            return cls(entries)
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            correct, _, wrong = line.partition("=")
            correct = correct.strip()
            if not correct:
                continue
            variants = [w.strip() for w in wrong.split(",") if w.strip()]
            entries.append((correct, variants))
        return cls(entries)

    @property
    def terms(self) -> List[str]:
        return [correct for correct, _ in self.entries]

    def prompt(self, template: str) -> str:
        """Vocabulary hint for Whisper, or "" when the glossary is empty."""
        terms: List[str] = []
        for term in self.terms:
            if len(", ".join(terms + [term])) > MAX_PROMPT_CHARS:
                break
            terms.append(term)
        if not terms:
            return ""
        if len(terms) == 1:
            joined = terms[0]
        else:
            joined = ", ".join(terms[:-1]) + " and " + terms[-1]
        return template.replace("{terms}", joined)

    @property
    def prompt_truncated(self) -> bool:
        return len(", ".join(self.terms)) > MAX_PROMPT_CHARS

    @staticmethod
    def _pattern(form: str) -> "re.Pattern[str]":
        # Words may be run together, spaced or hyphenated: "bus cart",
        # "bus-cart" and "buscart" all match the form "bus cart".
        words = [re.escape(w) for w in re.split(r"[\s\-]+", form) if w]
        return re.compile(r"(?<!\w)" + r"[\s\-]*".join(words) + r"(?!\w)",
                          re.IGNORECASE)

    @classmethod
    def _compile(cls, entries):
        rules = []
        for correct, variants in entries:
            # The correct form itself is included so its casing is normalised.
            for form in variants + [correct]:
                rules.append((form, correct, cls._pattern(form)))
        # Longest forms first, so "bus cart" wins over a shorter overlap.
        rules.sort(key=lambda r: len(r[0]), reverse=True)
        return rules

    def apply(self, text: str) -> Tuple[str, Dict[Tuple[str, str], int]]:
        """Return corrected text and a count of each (found, replacement)."""
        counts: Dict[Tuple[str, str], int] = {}
        for _form, correct, pattern in self._rules:
            def swap(match, correct=correct):
                found = match.group(0)
                if found != correct:
                    key = (found, correct)
                    counts[key] = counts.get(key, 0) + 1
                return correct
            text = pattern.sub(swap, text)
        return text, counts
