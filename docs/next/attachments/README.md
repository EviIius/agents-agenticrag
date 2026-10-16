# Attachments and the composer

**Written:** 15 October 2026, against commit `55477ff1` · **By:** Claude (validator) · **For:** Jake to approve, Codex to build on branch `codex/attachments-redesign`

Adding a file becomes one tap. On iPhone, + opens the native Photo Library / Take Photo / Choose Files menu right at the button, with no in-app menu first. Picked files appear in a tray inside the composer: photos as thumbnails straight away, documents and recordings as small cards with real details. Each tile shows its own progress, and any problem shows on the file itself with a fix. Desktop gets a proper drop card and pasting. Sent messages show photos and file cards instead of file names.

The composer also takes the shape you know from Claude and ChatGPT. It is one rounded box with your files at the top and a quiet row underneath: + and Tools on the left, Send on the right. Search, Library, Create image and Thinking move into the Tools menu, and whatever is on shows as a small chip you can ✕ off. It uses Atelier's own colors and mark, not theirs.

Place this folder at `docs/next/attachments/` in the repository.

| File | What it is | For |
|---|---|---|
| `ATTACHMENTS-SPEC.md` | The spec: findings, one-tap +, the tray and tile states, drop and paste, files in the thread, the composer and Tools menu, motion, build notes, branch rule, checkpoints, QA, decisions | Jake, Codex |
| `prototype.html` | Interactive prototype with fake uploads. Pick real files (they stay in your browser), drag files onto the window, paste a screenshot, or use **Add sample files**. Open **Tools** and switch things on. Switch the model between Text and Vision to see the photo warning. Theme and reduced motion are in the sidebar (in the ☰ drawer on the phone). | Jake, Codex |
| `reference/*-fake.png` | Screenshots of the prototype at 1440 px and 390 px with the real fonts | Codex |
| `CODEX-PROMPT.md` | One prompt per checkpoint, ready to paste, plus the merge-and-publish prompt for after you approve | Jake |

## Decisions needed (spec §12)

| ID | Decision | Before | Recommendation |
|---|---|---|---|
| J-U1 | One-tap + with the system picker; the in-app type menu goes away | AT-A | Yes |
| J-U2 | Pastes longer than 4,000 characters become a text file, with Keep as text to undo | AT-B | Yes |
| J-U3 | Images on a model that can't see them are kept with a warning and Switch model, instead of refused | AT-A | Yes |
| J-U4 | The composer takes the familiar shape: Tools menu plus chips; the four always-visible pills go away | AT-A | Yes |
| J-U5 | Build on `codex/attachments-redesign`; merge and publish only after you approve | AT-A | Yes (your request) |

## Order

```text
AT-A one-tap +, tray, composer ■  AT-B drop, paste, thread ■  merge and publish (after your OK)
■ = stop for Jake's review
```

Web only: no server, schema, prompt, model-call or dependency change.
