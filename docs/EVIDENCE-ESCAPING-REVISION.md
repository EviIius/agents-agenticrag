# Evidence contract v8: citation-compatible escaping replay

Version 7's inline code spans preserve visible values but break the existing
Library fact/citation binding check: its separate diagnostic scored 0/28.
Retain that replay and its failed compatibility diagnostic. No inference took
place, and the original v5 answers and reports remain unchanged.

Version 8 uses ordinary escaped Markdown. It retains decimal points, negative
signs and identifiers verbatim; encodes source brackets as HTML entities before
citation parsing; escapes HTML and active Markdown; and escapes pipes inside
tables. Source brackets can no longer create citations or links. Backticks remain
unsupported pending compatible scanners. Existing graders are unchanged.

The selection prompt, IDs, source context, quotation cap and unidentified-speaker
guard are unchanged. Freeze this renderer, replay driver, diagnostic script and
tests before replaying the same 62 retained streams. Keep any score difference
separate from model qualification: this replay cannot improve original evidence
coverage, relevance, omissions or latency.
