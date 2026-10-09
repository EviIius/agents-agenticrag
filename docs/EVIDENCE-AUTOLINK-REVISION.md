# Evidence contract v9: neutralize bare source links

The installed GFM parser creates an active link from v8's escaped bracket-link
text because its bare `https://…` URL remains detectable. The synthetic AST
failure is retained at `evidence-v8/autolink-failure.json`.

Version 9 encodes colons, email at signs and the dot in a `www.` prefix as HTML
entities before Markdown parsing. Visible text remains unchanged; the parser
cannot recognize URL/email autolink syntax. Genuine host citation/source controls
retain their original source URLs. Source text cannot manufacture those controls.

Keep all earlier replays, the selection prompt, source units, metadata, context,
caps and gates unchanged. Freeze v9 before the same 62-selection host-only replay;
verify rendering and inert links in the actual chat component on Chromium/WebKit.
This is a renderer correction, not another model trial or qualification.
