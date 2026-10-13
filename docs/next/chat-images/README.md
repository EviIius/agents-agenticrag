# Images in chat, and the working indicator

**Written:** 13 October 2026, against commit `dce4c49` · **By:** Claude (validator) · **For:** Jake to approve, Codex to build

Two changes. First, the three grey waiting dots become a status line: your Atelier "A" draws itself next to a word that changes every couple of seconds (*Spelunking… Mixing pigments…*), real stages always win, and a thinking model shows a one-line live ticker of its reasoning. Second, images become turns in the conversation: Image is a mode of the same composer, and each reply is an image card that develops in place with real step progress, then reveals the picture, with a full-screen viewer, Refine, More like this and Try again.

Place this folder at `docs/next/chat-images/` in the repository.

| File | What it is | For |
|---|---|---|
| `CHAT-IMAGES-SPEC.md` | The spec: findings, the working indicator, images as chat turns, frame states and animation, viewer, data model, API, checkpoints, QA, decisions | Jake, Codex |
| `prototype.html` | Interactive prototype with fake data. Press send (try Search and Think), then switch on Image, pick 2 images and send. Hover an image for actions, click it for the viewer, try Refine and Try again. Theme, status words and reduced motion are at the bottom of the sidebar. | Jake, Codex |
| `reference/*-fake.png` | Screenshots of the prototype at 1440 and 390 px with the real fonts | Codex |
| `CODEX-PROMPT.md` | One prompt per checkpoint, ready to paste | Jake |

## Decisions needed (spec §E)

| ID | Decision | Before | Recommendation |
|---|---|---|---|
| J-I1 | Status words default: Playful or Plain | CI-A | Playful, with Plain in Appearance |
| J-I2 | Live reasoning as a one-line ticker instead of the auto-opened panel | CI-A | Yes |
| J-I3 | Images become chat turns; the composer's image panel goes away | CI-B | Yes |
| J-I4 | Image turns are left out of the text model's context | CI-B | Yes |
| J-I5 | Image-first chats are titled from the prompt, without a model call | CI-B | Yes |

## Order

```text
CI-A working indicator (web only) ■  CI-B image turns ■  CI-C viewer and iteration ■
■ = stop for Jake's review
```
