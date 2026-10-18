import hashlib
from pathlib import Path

from app.library.prompt import PROMPT as LIBRARY
from app.runs.agent_prompt import PREAMBLE, prompt
from app.search.prompt import PROMPT as WEB


def test_agent_v1_prompt_hashes_and_verbatim_existing_rules() -> None:
    assert prompt("web").endswith(WEB[WEB.index("- ") :])
    assert prompt("library").endswith(LIBRARY[LIBRARY.index("- ") :])
    assert hashlib.sha256(prompt("web").encode()).hexdigest() == (
        "d973c913f70a422ddeaf193eb6738121bd16c18917a2b75e5a024cd3df942b92"
    )
    assert hashlib.sha256(prompt("library").encode()).hexdigest() == (
        "0edb998196d7a6116c8f6f50d8f0ecf6c471f9cd9da3f73e60ebdf2aedd743e5"
    )
    plan = Path(__file__).resolve().parents[2] / "docs/next/agent-loop/NATIVE-AGENT-LOOP-PLAN.md"
    # The Markdown block indents continuation lines by two more spaces.
    assert PREAMBLE in plan.read_text().replace("\n  ", "\n")
