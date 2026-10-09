"""Literal link fragments do not require all evidence facts to become code."""

from evals.reliability.evidence_contract_v10 import safe_text


def test_url_and_email_fragments_are_code_but_exact_values_stay_prose() -> None:
    text = safe_text("Offset -24.5. See https://example.invalid and person@example.invalid")
    assert text.startswith("Offset -24.5. See ")
    assert "`https://example.invalid`" in text
    assert "`person@example.invalid`" in text


def test_source_reference_inside_a_link_fragment_stays_inside_code() -> None:
    text = safe_text("www.example.invalid/[900]")
    assert text == "`www.example.invalid/[900]`"


def test_pipe_in_url_fragment_is_escaped_for_the_table_parser() -> None:
    assert (
        safe_text("https://example.invalid/A|B", in_table=True) == r"`https://example.invalid/A\|B`"
    )
