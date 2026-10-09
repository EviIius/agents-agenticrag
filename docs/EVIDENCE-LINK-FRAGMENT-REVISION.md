# Evidence contract v10: literal link fragments

The installed GFM parser decodes v9's entities before it autolinks text. Retain
the failed diagnostic at `evidence-v9/autolink-failure.json`; entity encoding
alone does not neutralize bare URLs or emails.

Version 10 wraps only source URL and email fragments in inline code, leaving
ordinary fact sentences in escaped prose. It preserves original source values,
including decimals and signs, without making every factual sentence a code span.
Backticks in selected source text remain rejected. Table pipes remain escaped
for the table parser. Host source/citation controls keep their own validated URLs.

Freeze the revised renderer, same-selection replay, diagnostic, tests and browser
fixture test before evaluation. Verify the installed GFM AST and actual chat
rendering with public/synthetic text. No new inference, evidence, prompt, source
unit or gate change; all earlier failed trials remain available.
