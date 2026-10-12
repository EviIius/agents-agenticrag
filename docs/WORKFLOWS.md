# Ordered workflows

Open **Workflows** in Atelier's sidebar. Each accepted run saves its selected
models, settings, attempts and outputs on your Mac. Closing the browser does not
stop it. After an uncertain server interruption, use **Retry unfinished steps**;
completed drafts and images are reused.

## Image brief → variants

1. Choose **Brief to images**, enter a brief, and select a prompt-draft model.
   A model marked **tested with images** has the measured compatible digest and
   context. Other loaded combinations may stop at the image memory check.
2. Enter one to three seeds, separated by commas. Keep prompt review enabled to
   inspect or edit the draft before generation.
3. Approve the prompt. The pinned FLUX.2 klein 4B worker generates each variant
   in order. Open **Images** to compare, save/share, create a new seeded version
   or remove outputs. Selection is yours; there is no model judge.

## Recording → meeting-pack draft

1. Choose **Recording to meeting pack** and upload audio or select a saved
   recording. A saved transcript also works after its audio was removed.
2. Select the drafting model. Optional guarded clean-up has its own explicit
   model selection and preserves the original transcript.
3. Check the resulting summary, decisions and action items against **View
   original transcript**. Missing owners and deadlines should remain unstated.
   Timestamps are included when the original source provides them.
4. Use **Save outputs** to choose Markdown or JSON, then save/share. The export retains
   the original source for review. A rejected clean-up can be retried or skipped
   explicitly to continue with the original transcript.

Meeting packs are drafts. These templates do not establish general factual
reliability or revive Research. Large inputs are rejected with a context message
instead of being silently shortened.

The native checks retained two model limitations: a missing action timestamp and
a quoted instruction misrepresented as an attendee's claim. Check quoted speech
against the source as well as decisions/owners/dates. **Original source timestamps**
in the source dialog and Markdown export are copied directly from the saved
transcript; they remain available when the model omits a draft reference.

## Controls and storage

- Optional output-limit/temperature fields override only the values you enter.
  Empty fields inherit your saved model defaults, then runtime defaults.
- Cancel stops the current owned text/image/clean-up job before releasing its
  native capacity. A transcription already accepted for a shared attachment may
  continue, so its original output remains available to chats.
- Images, transcription and text share the existing native resource queue.
  Foreground chat gets preference; a running native invocation finishes or is
  explicitly cancelled. No model is silently ejected.
- Workflow text, sources and attempts live in the existing database backups.
  Images use the image output backup manifest. Model weights are shared and are
  not duplicated per run. Successful audio still follows your audio retention
  setting; it is removed by default after durable transcription.
- The page shows the latest 50 runs. Earlier runs remain saved in the database.
