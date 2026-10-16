# AT-B existing-test changes

Compared with AT-A `3e3ae755`. No existing test, skip, timeout or performance threshold is removed or relaxed.

| File / test | Change | Preserved checks |
|---|---|---|
| `web/tests/documents.spec.ts` / 5B paste and drop | Expect the approved “Drop to attach” heading instead of the old overlay sentence | Same file bytes, real drag/paste events, upload path and document chip |
| `web/tests/image-uploads.spec.ts` / HEIC paste and drop | Pasted photos use the approved “Pasted image 1.png” name; dropped files retain their name | Same actual chooser-normalization path, response and image-mode assertions |

Two new browser files add 22 engine-specific tests. AT-A’s ledger remains unchanged. New harness corrections are retained separately; they change no existing gate.
