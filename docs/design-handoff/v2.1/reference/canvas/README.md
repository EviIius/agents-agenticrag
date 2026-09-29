# Mockup sources

These are the design canvas's artboard files, copied as they are. They need the canvas runtime (`support.js`) to run, so read them as HTML and CSS rather than opening them:

- **Markup:** inside `<x-dc>`. `{{name}}` holes are values from the script block. `<sc-if>` and `<sc-for>` are conditionals and loops.
- **Styles:** inside `<helmet><style>`. The same shared block is repeated in every file; the mockup variable names map to `tokens.css` as shown in `../../README.md`.
- **State logic and timings:** the `<script type="text/x-dc">` block at the end of each file. For example, `Launch.dc.html` holds the intro timeline, and `Offline.dc.html` holds the retry backoff.

Inline `style="…"` attributes are fine in the mockups but not in the app, because the app's CSP forbids them. Use classes from `../../components-v21.reference.css`.
