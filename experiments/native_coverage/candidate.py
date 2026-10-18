"""Unexecuted v2 candidate. It is never imported by the app or stopped N1 worker."""

from app.runs.agent_prompt import prompt as v1

REMINDER = """Write each factual list item with its own inline citation at the end of that item.
Citations in a heading or introductory sentence do not cite later items.
Apply the same rule to each factual table row."""


def prompt(kind):
    return v1(kind) + "\n" + REMINDER
