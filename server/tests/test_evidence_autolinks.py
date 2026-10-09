"""Source link syntax is encoded before the browser's GFM parser sees it."""

from evals.reliability.evidence_contract_v9 import safe_text


def test_bare_urls_emails_and_www_prefixes_are_not_active_markdown() -> None:
    result = safe_text("https://example.invalid www.example.invalid person@example.invalid")
    assert "https:" not in result and "www." not in result and "@" not in result
    assert "https&#58;//example.invalid" in result
    assert "www&#46;example.invalid" in result
    assert "person&#64;example.invalid" in result


def test_url_neutralization_does_not_change_decimals_signs_or_identifiers() -> None:
    assert safe_text("Offset -24.5; code CEDAR-42") == "Offset -24.5; code CEDAR-42"
