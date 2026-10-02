"""Declared regex assertions, including alternative equivalent answer formats."""

import re
from typing import Any


def required_facts(answer: str, expect: dict[str, Any]) -> bool:
    patterns = expect.get("must_include_last", expect.get("must_include", []))
    mandatory = all(re.search(pattern, answer, re.I) for pattern in patterns)
    alternatives = expect.get("must_include_one_of", [])
    return mandatory and (
        not alternatives
        or any(all(re.search(pattern, answer, re.I) for pattern in group) for group in alternatives)
    )
