# Prompts to paste into Codex

One prompt at a time. Each assumes this folder is at `docs/next/attachments/` in the repository, including `prototype.html` and `reference/`.

**Everything is built on its own branch, `codex/attachments-redesign`.** Nothing reaches `main` or the installed app until you paste the last prompt ("Merge and publish").

Give Codex your decisions from `ATTACHMENTS-SPEC.md` §12 first. AT-A needs J-U1, J-U3, J-U4 and J-U5. AT-B needs J-U2.

---

## AT-A: one way in, the tray and the composer

```text
Read AGENTS.md, docs/next/QA-REQUIREMENTS.md, docs/next/PHASE-4-POLISH-AND-MOTION.md (C1–C4),
docs/next/chat-images/CHAT-IMAGES-SPEC.md A2 (image mode), then
docs/next/attachments/ATTACHMENTS-SPEC.md (all of it). Open docs/next/attachments/prototype.html
in a browser at 1440 px and at 390 px: press "Add sample files", open Tools, switch Library and
Thinking on, switch the model between Text and Vision. Look at every image in
docs/next/attachments/reference/. Match that look, spacing and motion. Where the prototype and
the spec differ, the spec wins.

Branch first (spec §9):
- git switch main && git pull --ff-only (only if a remote is configured), then
  git switch -c codex/attachments-redesign. Record the base commit in the report.
- Every commit for this work goes on codex/attachments-redesign. Never commit to main.
- Add the AGENTS.md amendment from §12 on the branch, with today's date and only the parts I
  approved.

Build checkpoint AT-A only (§2, §3, §6). Stop with docs/ATTACHMENTS-AT-A-REPORT.md using the SPEC
§H4 template plus QA §8, with evidence for AT-AC1 to AT-AC9, AT-AC16 and every gate. Then push
the branch (git push -u origin codex/attachments-redesign) and, if gh is available, open a DRAFT
pull request against main titled "Attachments and composer redesign (AT-A, AT-B)". Do not merge.

My decisions: J-U1 = <yes / no>. J-U3 = <yes / no>. J-U4 = <yes / no>. J-U5 = yes.

Rules that matter most here:
- Web only. No server file, schema, prompt, model call or dependency changes. G-6, G-7, G-8 and
  G-9 must show no change. G-10: the request body for each tool combination is identical to
  before.
- Do not run the publisher, change the installed app, restart the service or touch main.
  Verify with make check, make e2e (Chromium and WebKit, including the iPhone 390 px profile)
  and the fake runtime only.
- On touch, the file input is laid transparently over the + button (§2.1). Never call .click()
  on a hidden input on touch devices. The in-app "Add image / text file / document / recording"
  menu goes away.
- One accept string from file-kinds.ts; classification reuses the existing useUploads rules.
- Every upload, images and text included, goes through uploadWithProgress. Photo thumbnails come
  from a local object URL at pick time; revoke it on removal and after the server copy loads.
- Problems become tile states and the status line (§3.4), never toast.error. Images on a model
  without vision are kept with a warning and Switch model, not refused.
- The composer (§6): 24 px box, 16 px text box, + and Tools on the left, chips for tools that
  are on, Send on the right. Search, Library, Create image and Thinking move into the Tools
  menu; the four pills go away. Reuse the existing state for search, library scope, thinking
  level and image mode; only the controls move. Image mode itself stays as chat images A2 built
  it, with Create image as its new entry point.
- Do not copy any other product's logo, icons, colors or wording. Use Atelier's tokens and the
  existing icon set.
- Motion in web/src/styles/motion.css with transform, opacity, width and stroke-dasharray only.
  Everything stops under both reduced-motion triggers. performance.spec.ts thresholds unchanged.
- Every new state on /design. Test files and screenshots are synthetic with "fake" in the file
  name. Never capture the iOS document picker or a real file name.
```

## AT-B: drop, paste and the thread

```text
Read docs/next/attachments/ATTACHMENTS-SPEC.md §4, §5, §7 and §11, and look at
reference/drop-*, paste-*, thread-*, viewer-*, sheet-* and phone-thread-*. In the prototype,
drag files onto the window, paste a screenshot, paste a long block of text, then send.

Stay on codex/attachments-redesign. Build checkpoint AT-B only. Stop with
docs/ATTACHMENTS-AT-B-REPORT.md (§H4 plus QA §8), evidence for AT-AC10 to AT-AC15 and every gate,
and push the branch so the draft pull request updates. Do not merge.

My decisions: J-U2 = <yes / no>.

Rules that matter most here:
- DropOverlay replaces the dashed box in LiveAppShell.tsx. During a drag the composer sits above
  the scrim. Other routes keep their own drop behavior.
- Pasted images become photo tiles named "Pasted image N.png". If J-U2 is yes, pastes longer than
  4,000 characters become "Pasted text N.txt" with a working Keep as text; shorter pastes behave
  as today.
- MessageAttachments renders above the user bubble: the photo grid (1, 2, 3+ with "+N" after 6)
  and read-only file cards that wrap two to a row on desktop and stack on phones. Fixed boxes,
  loading="lazy", decoding="async": no layout shift (AT-AC12).
- Photos open the existing image viewer with that message's photos; files open DocumentSheet,
  TranscriptSheet or the text preview.
- The optimistic row shows the same tiles as the confirmed row.
- Rows loaded from history never animate.
- Same branch, web-only, synthetic-data and no-publish rules as AT-A.
```

## Merge and publish (only after you have reviewed both reports)

```text
I approve docs/ATTACHMENTS-AT-A-REPORT.md and docs/ATTACHMENTS-AT-B-REPORT.md. Merge
codex/attachments-redesign into main with git merge --no-ff, run make check and make e2e on main,
then publish with the existing static-only publisher (web assets only; server hashes must be
unchanged) and keep the private rollback. Report the merge commit, the published asset hashes
and the rollback path, then ask me for the five-minute phone check in QA §7. If anything fails,
stop before publishing and tell me.
```
