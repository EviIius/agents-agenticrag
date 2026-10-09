# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: conversation-motion.spec.ts >> code and transcript copy show a local check and clear it after 1.5 seconds
- Location: tests/conversation-motion.spec.ts:623:1

# Error details

```
Test timeout of 45000ms exceeded.
```

```
Error: locator.click: Test timeout of 45000ms exceeded.
Call log:
  - waiting for getByRole('region', { name: 'Conversation motion', exact: true }).locator('[data-streamdown="code-block-copy-button"]').first()
    - locator resolved to <button type="button" title="Copy Code" aria-label="Copy Code" data-streamdown="code-block-copy-button" class="cursor-pointer p-1 text-muted-foreground transition-all hover:text-foreground disabled:cursor-not-allowed disabled:opacity-50">…</button>
  - attempting click action
    2 × waiting for element to be visible, enabled and stable
      - element is not stable
    - retrying click action
    - waiting 20ms
    - waiting for element to be visible, enabled and stable
    - element is not stable
  2 × retrying click action
      - waiting 100ms
      - waiting for element to be visible, enabled and stable
      - element is visible, enabled and stable
      - scrolling into view if needed
      - done scrolling
      - element is outside of the viewport
  82 × retrying click action
       - waiting 500ms
       - waiting for element to be visible, enabled and stable
       - element is visible, enabled and stable
       - scrolling into view if needed
       - done scrolling
       - element is outside of the viewport
  - retrying click action
    - waiting 500ms

```

# Page snapshot

```yaml
- generic [ref=e2]:
  - main [ref=e4]:
    - generic [ref=e5]:
      - generic [ref=e6]:
        - button "Open sidebar" [ref=e7] [cursor=pointer]
        - button "Choose model" [ref=e9] [cursor=pointer]:
          - generic [aria-hidden] [ref=e10]: ●
          - generic [ref=e11]: fake-chat
      - generic [ref=e12]:
        - button "Chat controls" [ref=e13] [cursor=pointer]
        - button "Chat actions" [ref=e14] [cursor=pointer]
    - generic [ref=e16]:
      - generic [ref=e17]:
        - paragraph [ref=e18]: ATELIER / FOUNDATION
        - heading "A quieter place to think." [level=1] [ref=e19]
        - paragraph [ref=e20]: The living component guide. Every answer and statistic here is a Fake runtime fixture. Switch themes to review the same states.
        - generic [ref=e21]:
          - button "Light" [ref=e22] [cursor=pointer]
          - button "Dark" [ref=e23] [cursor=pointer]
          - button "System" [ref=e24] [cursor=pointer]
          - link "Everyday chat states" [ref=e25]:
            - /url: /design?everyday
          - link "Fixture chat" [ref=e26]:
            - /url: /design/chat/fixture
          - button "Appearance" [ref=e27] [cursor=pointer]
      - region "First run states" [ref=e28]:
        - heading "First run · synthetic runtime detection" [level=2] [ref=e29]
        - generic [ref=e30]:
          - heading "Welcome to Atelier" [level=1] [ref=e31]
          - paragraph [ref=e32]: Connect the local models on your Mac.
          - status [ref=e33]: Looking for Ollama…
          - button "Configure a connection" [ref=e34] [cursor=pointer]
        - generic [ref=e35]:
          - heading "Welcome to Atelier" [level=1] [ref=e36]
          - paragraph [ref=e37]: Connect the local models on your Mac.
          - paragraph [ref=e38]: "Start Ollama on your Mac:"
          - code [ref=e39]: ollama serve
          - button "Try again" [ref=e40] [cursor=pointer]
          - button "Configure a connection" [ref=e41] [cursor=pointer]
        - generic [ref=e42]:
          - heading "Welcome to Atelier" [level=1] [ref=e43]
          - paragraph [ref=e44]: Connect the local models on your Mac.
          - generic [ref=e45]:
            - generic [ref=e46]:
              - paragraph [ref=e47]: Ollama
              - paragraph [ref=e48]: 3 models · http://127.0.0.1:18080
            - button "Add all" [ref=e49] [cursor=pointer]
          - button "Configure a connection" [ref=e50] [cursor=pointer]
      - region "Web search states" [ref=e51]:
        - heading "Web search · synthetic fixtures" [level=2] [ref=e52]
        - generic [ref=e53]:
          - heading "Ollama Search · setup needed · synthetic preview" [level=3] [ref=e54]
          - generic [ref=e55]:
            - paragraph [ref=e56]: Search uses your free Ollama account. Your chat model runs on this Mac. Usage limits apply.
            - link "Create an Ollama API key" [ref=e57]:
              - /url: https://ollama.com/settings/keys
            - generic [ref=e58]:
              - text: Ollama search API key
              - textbox "Ollama search API key" [ref=e59]
            - generic [ref=e60]:
              - button "Save Ollama key" [disabled]
              - button "Remove Ollama key" [disabled]
        - generic [ref=e61]:
          - heading "Ollama Search · saved key · synthetic preview" [level=3] [ref=e62]
          - generic [ref=e63]:
            - paragraph [ref=e64]: Search uses your free Ollama account. Your chat model runs on this Mac. Usage limits apply.
            - link "Create an Ollama API key" [ref=e65]:
              - /url: https://ollama.com/settings/keys
            - generic [ref=e66]:
              - text: Ollama search API key · Key saved
              - textbox "Ollama search API key · Key saved" [ref=e67]
            - generic [ref=e68]:
              - button "Save Ollama key" [disabled]
              - button "Remove Ollama key" [ref=e69] [cursor=pointer]
        - button "Searched the web · 1 sources · 1.1 s" [ref=e72] [cursor=pointer]:
          - generic [aria-hidden] [ref=e75]: E
        - generic [ref=e79]:
          - status [ref=e80]
          - paragraph [ref=e82]:
            - text: A sample cited claim
            - 'button "View source: Synthetic design source" [ref=e83] [cursor=pointer]': "1"
            - text: .
        - button [ref=e84] [cursor=pointer]:
          - generic [aria-hidden] [ref=e86]: E
          - text: 1 sources
        - generic [ref=e87]:
          - status [ref=e88]:
            - paragraph [ref=e89]: Web search failed (Synthetic test failure). This answer uses the model's own knowledge.
            - button "Retry with search" [ref=e90] [cursor=pointer]
          - button "Searched the web · 0 sources · 1.1 s" [ref=e92] [cursor=pointer]
        - generic [ref=e99]:
          - status [ref=e100]:
            - paragraph [ref=e101]: The web search found nothing for “Synthetic test failure”. This answer uses the model's own knowledge.
            - button "Retry with search" [ref=e102] [cursor=pointer]
          - button "Searched the web · 0 sources · 1.1 s" [ref=e104] [cursor=pointer]
        - generic [ref=e111]:
          - status [ref=e112]:
            - paragraph [ref=e113]: Couldn't read any of the search results (Synthetic test failure). This answer uses the model's own knowledge.
            - button "Retry with search" [ref=e114] [cursor=pointer]
          - button "Searched the web · 0 sources · 1.1 s" [ref=e116] [cursor=pointer]
        - paragraph [ref=e123]:
          - text: No web search needed ·
          - button "Search anyway" [ref=e124] [cursor=pointer]
        - generic [ref=e126]:
          - button "Searching the web…" [expanded] [ref=e127] [cursor=pointer]:
            - generic [aria-hidden] [ref=e130]: E
          - list [ref=e135]:
            - listitem [ref=e136]: Read example.org
        - paragraph [ref=e137]: This answer doesn't cite specific sources.
      - region "Runtime error copy" [ref=e138]:
        - heading "Runtime errors · synthetic fixtures" [level=2] [ref=e139]
        - paragraph [ref=e140]: Can't reach Ollama at the configured address. Is it running?
        - paragraph [ref=e141]: This model isn't available on Ollama anymore.
        - paragraph [ref=e142]: Ollama couldn't load This model, most likely not enough memory. Eject other models or pick a smaller one.
        - paragraph [ref=e143]: This chat is longer than This model's context window (8192 tokens).
        - paragraph [ref=e144]: The model stopped responding. The partial answer is kept.
        - paragraph [ref=e145]: "Ollama returned an error: Synthetic runtime error"
        - paragraph [ref=e146]: Interrupted because the server restarted.
      - region [ref=e147]:
        - heading "Typography & surfaces" [level=2] [ref=e148]
        - paragraph [ref=e149]: Space for the answer to breathe.
        - paragraph [ref=e150]: Geist for controls. Newsreader for answers. Geist Mono for code.
        - paragraph [ref=e151]: Metadata · 12 / 16 · tabular numbers
        - generic [ref=e152]:
          - generic [ref=e153]: bg
          - generic [ref=e154]: surface
          - generic [ref=e155]: surface-2
          - generic [ref=e156]: surface-3
        - generic [ref=e157]:
          - button "Primary" [ref=e158] [cursor=pointer]
          - button "Secondary" [ref=e159] [cursor=pointer]
          - button "Ghost" [ref=e160] [cursor=pointer]
          - button "Disabled" [disabled]
      - region "Data controls preview" [ref=e161]:
        - heading "Data controls · safe preview" [level=2] [ref=e162]
        - generic [ref=e163]:
          - paragraph [ref=e164]: Export every chat and branch, including citations, as one JSON file. Attachment files are stored separately on your Mac.
          - link "Export all chats" [ref=e165]:
            - /url: "#data-preview"
          - region "Database backups" [ref=e166]:
            - heading "Automatic backups" [level=3] [ref=e167]
            - paragraph [ref=e168]: "Last backup: 10/5/26, 3:30 AM · 7 kept · 41.0 MB"
            - paragraph [ref=e169]: Daily at 03:30 on your Mac; seven copies kept. Attachment files are not included; restore instructions are in the README on your Mac.
            - button "Back up now" [ref=e170] [cursor=pointer]
          - generic [ref=e171]:
            - button "Import old chats" [ref=e172] [cursor=pointer]
            - paragraph [ref=e173]: Copy chats from Chat & Web 0.5. Your old database stays unchanged.
          - button "Delete all chats" [ref=e174] [cursor=pointer]
      - region "Motion foundation" [ref=e175]:
        - heading "Overlay motion" [level=2] [ref=e176]
        - paragraph [ref=e177]: Production primitives. Open and close each surface to inspect normal and reduced motion.
        - generic [ref=e178]:
          - button "Motion rename" [ref=e179] [cursor=pointer]
          - button "Motion delete" [ref=e180] [cursor=pointer]
          - button "Motion export" [ref=e181] [cursor=pointer]
          - generic [ref=e182]:
            - button "Open transcript for fake-motion.wav" [ref=e184] [cursor=pointer]:
              - generic [ref=e185]: fake-motion.wav
              - status [ref=e186]: 1:15 · 18 words · ≈35 tokens
            - button "Recording actions for fake-motion.wav" [ref=e187] [cursor=pointer]
          - button "Always reduce motion" [ref=e188] [cursor=pointer]
          - button "Motion settings" [ref=e189] [cursor=pointer]
          - button "Motion popover" [ref=e190] [cursor=pointer]
          - button "Motion dialog" [ref=e191] [cursor=pointer]
          - button "Motion alert" [ref=e192] [cursor=pointer]
          - button "Motion menu" [ref=e193] [cursor=pointer]
          - combobox "Motion select" [ref=e194] [cursor=pointer]:
            - generic: Text
          - button "Motion tooltip" [ref=e195] [cursor=pointer]
          - button "Motion sheet left" [ref=e196] [cursor=pointer]
          - button "Motion sheet right" [ref=e197] [cursor=pointer]
          - button "Motion sheet top" [ref=e198] [cursor=pointer]
          - button "Motion sheet bottom" [ref=e199] [cursor=pointer]
          - button "Motion drawer" [ref=e200] [cursor=pointer]
      - region "Visual refinement previews" [ref=e201]:
        - heading "4D · title, history loading and offline" [level=2] [ref=e202]
        - generic [ref=e204]:
          - generic [ref=e205]:
            - textbox "Search history" [ref=e206]:
              - /placeholder: Search chats…
            - generic: ⌘K
          - status "Loading chats" [ref=e207]
        - alert [ref=e211]:
          - heading "Can't reach Atelier" [level=1] [ref=e212]
          - paragraph [ref=e213]: Your Mac may be asleep or off the tailnet.
          - group [ref=e214]:
            - generic "Details" [ref=e215] [cursor=pointer]
            - text: "TypeError: Synthetic offline fixture"
          - button "Try again" [ref=e216] [cursor=pointer]
      - region "Conversation motion" [ref=e217]:
        - heading "Conversation motion · synthetic fixtures" [level=2] [ref=e218]
        - generic [ref=e219]:
          - button "Preview optimistic" [ref=e220] [cursor=pointer]
          - button "Preview waiting" [ref=e221] [cursor=pointer]
          - button "Preview reasoning" [ref=e222] [cursor=pointer]
          - button "Preview streaming" [ref=e223] [cursor=pointer]
          - button "Preview search" [ref=e224] [cursor=pointer]
          - button "Preview complete" [ref=e225] [cursor=pointer]
          - button "Preview title change" [ref=e226] [cursor=pointer]
        - generic [ref=e227]:
          - paragraph [ref=e228]: Previous 7 days
          - generic [ref=e229]:
            - link "Synthetic motion chat" [ref=e230]:
              - /url: /c/conversation-motion-fake
            - img "Generating response" [ref=e231]
        - button "Choose model" [ref=e234] [cursor=pointer]:
          - generic [aria-hidden] [ref=e235]: ●
          - generic [ref=e236]: fake-chat
        - generic [ref=e237]:
          - status [ref=e238]
          - log "Conversation" [ref=e239]:
            - generic [ref=e240]:
              - article "user message" [ref=e241]:
                - heading "You said" [level=2] [ref=e242]
                - paragraph [ref=e244]: Synthetic motion request
                - generic [ref=e247]:
                  - button "Copy message" [ref=e248] [cursor=pointer]:
                    - status [ref=e249]
                  - button "Edit message" [ref=e250] [cursor=pointer]
              - article "assistant message" [ref=e251]:
                - heading "fake-chat replied" [level=2] [ref=e252]
                - paragraph [ref=e253]: Fake runtime · fake-chat
                - button "Thought for 0s" [ref=e255] [cursor=pointer]
                - generic [ref=e267]:
                  - status [ref=e268]
                  - generic [ref=e269]:
                    - paragraph [ref=e270]: Synthetic copy example.
                    - generic [ref=e271]:
                      - generic [ref=e272]: python
                      - button "Copy Code" [ref=e275] [cursor=pointer]
                      - region "Code example" [ref=e278]:
                        - code [ref=e280]:
                          - generic [ref=e281]: print("fake")
                - generic [ref=e284]:
                  - button "Copy message" [ref=e285] [cursor=pointer]:
                    - status [ref=e286]
                  - button "Regenerate answer" [ref=e287] [cursor=pointer]
                  - button "Regenerate with another model" [ref=e288] [cursor=pointer]
                  - button "Message info" [ref=e289] [cursor=pointer]
          - button [aria-hidden] [ref=e290] [cursor=pointer]: ↓
        - form "Message" [ref=e291]:
          - textbox "Message fake-chat" [ref=e292]:
            - /placeholder: Message fake-chat…
          - generic [ref=e293]:
            - button "Add attachment" [ref=e294] [cursor=pointer]
            - generic [ref=e295]:
              - img "128 of 16,384 total tokens; 12,032 input allowance; 4,096 reserved for response; 256 safety margin" [ref=e296]
              - generic [ref=e300]:
                - button "Send message" [disabled]
        - generic [ref=e301]:
          - heading "Good afternoon" [level=1] [ref=e302]
          - form "Message" [ref=e303]:
            - textbox "Message fake-chat" [ref=e304]:
              - /placeholder: Message fake-chat…
            - generic [ref=e305]:
              - button "Add attachment" [ref=e306] [cursor=pointer]
              - generic [ref=e307]:
                - img "Context usage unavailable" [ref=e308]
                - generic [ref=e312]:
                  - button "Send message" [disabled]
          - generic [ref=e313]:
            - button "Explain" [ref=e314] [cursor=pointer]
            - button "Write" [ref=e315] [cursor=pointer]
            - button "Code" [ref=e316] [cursor=pointer]
          - paragraph [ref=e317]: Your models. Your Mac.
      - region "Phase 3 previews" [ref=e318]:
        - heading "Polish · synthetic previews" [level=2] [ref=e319]
        - generic [ref=e320]:
          - button "Preview palette ready" [ref=e321] [cursor=pointer]
          - button "Preview palette empty" [ref=e322] [cursor=pointer]
          - button "Preview palette loading" [ref=e323] [cursor=pointer]
          - button "Preview palette error" [ref=e324] [cursor=pointer]
          - button "Preview app update" [ref=e325] [cursor=pointer]
        - generic [ref=e326]:
          - heading "Legacy import · synthetic states" [level=3] [ref=e327]
          - generic [ref=e328]:
            - button "Import preview ready" [ref=e329] [cursor=pointer]
            - button "Import preview loading" [ref=e330] [cursor=pointer]
            - button "Import preview missing" [ref=e331] [cursor=pointer]
            - button "Import preview status-error" [ref=e332] [cursor=pointer]
            - button "Import preview importing" [ref=e333] [cursor=pointer]
            - button "Import preview failed" [ref=e334] [cursor=pointer]
          - generic [ref=e335]:
            - button "Import old chats" [ref=e336] [cursor=pointer]
            - paragraph [ref=e337]: Copy chats from Chat & Web 0.5. Your old database stays unchanged.
      - region "Transcription preview" [ref=e338]:
        - heading "Recordings · synthetic fixtures · T1" [level=2] [ref=e339]
        - paragraph [ref=e340]: Fake engine content. No real recording or transcript is used here.
        - status [ref=e341]:
          - generic [ref=e343]:
            - paragraph [ref=e344]: Synthetic recording.wav
            - progressbar "Upload progress" [ref=e345]
            - paragraph [ref=e347]: Uploading 42%
          - button "Cancel upload" [ref=e348] [cursor=pointer]
        - status [ref=e349]:
          - generic [ref=e351]:
            - paragraph [ref=e352]: Synthetic recording.wav
            - progressbar "Upload progress" [ref=e353]
            - paragraph [ref=e354]: Upload didn't finish
          - button "Remove failed upload" [ref=e355] [cursor=pointer]
        - generic [ref=e356]:
          - button "Synthetic recording.wav" [disabled] [ref=e358]:
            - status [ref=e360]: Waiting for another recording
          - button "Cancel transcription" [ref=e361] [cursor=pointer]
          - button "Remove Synthetic recording.wav" [ref=e362] [cursor=pointer]
        - generic [ref=e363]:
          - button "Synthetic recording.wav" [disabled] [ref=e365]:
            - status [ref=e367]: Transcribing 1:26
          - button "Cancel transcription" [ref=e368] [cursor=pointer]
          - button "Remove Synthetic recording.wav" [ref=e369] [cursor=pointer]
        - generic [ref=e370]:
          - button "Open transcript for Synthetic recording.wav" [ref=e372] [cursor=pointer]:
            - generic [ref=e373]: Synthetic recording.wav
            - status [ref=e374]: 1:15 · 18 words · ≈35 tokens
          - button "Recording actions for Synthetic recording.wav" [ref=e375] [cursor=pointer]
        - generic [ref=e376]:
          - button "Open transcript for Synthetic recording.wav" [ref=e378] [cursor=pointer]:
            - generic [ref=e379]: Synthetic recording.wav
            - status [ref=e380]: 1:15 · 18 words · ≈35 tokens
            - generic [ref=e381]: Transcript saved · audio removed
          - button "Recording actions for Synthetic recording.wav" [ref=e382] [cursor=pointer]
        - generic [ref=e383]:
          - button "Open transcript for Synthetic recording.wav" [ref=e385] [cursor=pointer]:
            - generic [ref=e386]: Synthetic recording.wav
            - status [ref=e387]: 1:15 · 18 words · ≈30,000 tokens
          - button "Recording actions for Synthetic recording.wav" [ref=e388] [cursor=pointer]
          - button "Choose model" [ref=e389] [cursor=pointer]
          - paragraph [ref=e390]: About 30,000 input tokens exceeds the 12,032-token input allowance. 4,096 tokens are reserved for the response. Choose a model with a larger context or lower Max output tokens in Chat controls.
        - generic [ref=e391]:
          - button "Open transcript for Synthetic recording.wav" [ref=e393] [cursor=pointer]:
            - generic [ref=e394]: Synthetic recording.wav
            - status [ref=e395]: No speech found
          - button "Recording actions for Synthetic recording.wav" [ref=e396] [cursor=pointer]
        - generic [ref=e397]:
          - button "Synthetic recording.wav" [disabled] [ref=e399]:
            - status [ref=e401]: "Couldn't transcribe: Synthetic unreadable recording"
          - button "Retry" [ref=e402] [cursor=pointer]
          - button "Remove Synthetic recording.wav" [ref=e403] [cursor=pointer]
        - generic [ref=e404]:
          - button "Synthetic recording.wav" [disabled] [ref=e406]:
            - status [ref=e408]: Interrupted because the server restarted
          - button "Retry" [ref=e409] [cursor=pointer]
          - button "Remove Synthetic recording.wav" [ref=e410] [cursor=pointer]
        - generic [ref=e411]:
          - button "Synthetic recording.wav" [disabled] [ref=e413]:
            - status [ref=e415]: Cancelled
          - button "Retry" [ref=e416] [cursor=pointer]
          - button "Remove Synthetic recording.wav" [ref=e417] [cursor=pointer]
        - generic [ref=e418]:
          - form "Message" [ref=e419]:
            - generic [ref=e420]:
              - button "Open transcript for Synthetic recording.wav" [ref=e422] [cursor=pointer]:
                - generic [ref=e423]: Synthetic recording.wav
                - status [ref=e424]: 1:15 · 18 words · ≈26,861 tokens
              - button "Recording actions for Synthetic recording.wav" [ref=e425] [cursor=pointer]
              - button "Choose model" [ref=e426] [cursor=pointer]
              - paragraph [ref=e427]: About 26,861 input tokens exceeds the 12,032-token input allowance. 4,096 tokens are reserved for the response. Choose a model with a larger context or lower Max output tokens in Chat controls.
            - textbox "Message Fake 16K model" [ref=e428]:
              - /placeholder: Message Fake 16K model…
            - generic [ref=e429]:
              - button "Add attachment" [ref=e430] [cursor=pointer]
              - button "Web search" [disabled] [ref=e431] [cursor=pointer]
              - generic [ref=e432]:
                - img "Context usage unavailable" [ref=e433]
                - generic [ref=e437]:
                  - button "Send message" [disabled]
          - generic [ref=e438]:
            - button "Summarize" [ref=e439] [cursor=pointer]
            - button "Action items" [ref=e440] [cursor=pointer]
            - button "Decisions" [ref=e441] [cursor=pointer]
        - status [ref=e442]: Web search is off in chats with a recording, so nothing from it leaves this Mac.
        - generic [ref=e443]:
          - heading "32K input allowance · default response reserve" [level=3] [ref=e444]
          - form "Message" [ref=e445]:
            - generic [ref=e446]:
              - button "Open transcript for Synthetic recording.wav" [ref=e448] [cursor=pointer]:
                - generic [ref=e449]: Synthetic recording.wav
                - status [ref=e450]: 1:15 · 18 words · ≈26,861 tokens
              - button "Recording actions for Synthetic recording.wav" [ref=e451] [cursor=pointer]
              - button "Choose model" [ref=e452] [cursor=pointer]
              - paragraph [ref=e453]: About 26,861 input tokens exceeds the 24,320-token input allowance. 8,192 tokens are reserved for the response. Choose a model with a larger context or lower Max output tokens in Chat controls.
            - textbox "Message Fake 16K model" [ref=e454]:
              - /placeholder: Message Fake 16K model…
            - generic [ref=e455]:
              - button "Add attachment" [ref=e456] [cursor=pointer]
              - generic [ref=e457]:
                - img "28,509 of 32,768 total tokens; 24,320 input allowance; 8,192 reserved for response; 256 safety margin" [ref=e458]
                - generic [ref=e462]:
                  - button "Send message" [disabled]
          - generic [ref=e463]:
            - button "Summarize" [ref=e464] [cursor=pointer]
            - button "Action items" [ref=e465] [cursor=pointer]
            - button "Decisions" [ref=e466] [cursor=pointer]
        - generic [ref=e467]:
          - heading "32K input allowance · user output limit" [level=3] [ref=e468]
          - form "Message" [ref=e469]:
            - generic [ref=e470]:
              - button "Open transcript for Synthetic recording.wav" [ref=e472] [cursor=pointer]:
                - generic [ref=e473]: Synthetic recording.wav
                - status [ref=e474]: 1:15 · 18 words · ≈26,861 tokens
              - button "Recording actions for Synthetic recording.wav" [ref=e475] [cursor=pointer]
            - textbox "Message Fake 16K model" [ref=e476]:
              - /placeholder: Message Fake 16K model…
            - generic [ref=e477]:
              - button "Add attachment" [ref=e478] [cursor=pointer]
              - generic [ref=e479]:
                - img "28,509 of 32,768 total tokens; 29,440 input allowance; 3,072 reserved for response; 256 safety margin" [ref=e480]
                - generic [ref=e484]:
                  - button "Send message" [disabled]
          - generic [ref=e485]:
            - button "Summarize" [ref=e486] [cursor=pointer]
            - button "Action items" [ref=e487] [cursor=pointer]
            - button "Decisions" [ref=e488] [cursor=pointer]
        - button "Preview transcript panel" [ref=e489] [cursor=pointer]
        - generic "Recording download previews" [ref=e490]:
          - button "Preview download ready" [ref=e491] [cursor=pointer]
          - button "Preview download preparing" [ref=e492] [cursor=pointer]
          - button "Preview download failed" [ref=e493] [cursor=pointer]
          - button "Preview download sharing" [ref=e494] [cursor=pointer]
          - button "Preview download cancelled" [ref=e495] [cursor=pointer]
          - button "Preview download share-failed" [ref=e496] [cursor=pointer]
          - button "Preview download returned" [ref=e497] [cursor=pointer]
        - generic [ref=e498]:
          - heading "Ready · fake engine" [level=3] [ref=e499]
          - paragraph [ref=e500]: ● Ready · fake-0.1.0
          - list [ref=e501]:
            - listitem [ref=e502]:
              - generic [ref=e503]: "Fake engine: OK"
              - paragraph [ref=e504]: Synthetic fixture only
          - generic [ref=e505]:
            - switch "Keep web search off in chats with a recording" [checked] [ref=e506] [cursor=pointer]
            - generic [ref=e507]: Keep web search off in chats with a recording
          - generic [ref=e508]:
            - switch "Keep original audio after transcription" [ref=e509] [cursor=pointer]
            - generic [ref=e510]: Keep original audio after transcription
          - paragraph [ref=e511]: "Off by default: audio is removed after the transcript is saved. Text, timestamps and JSON outputs stay available. Failed recordings are kept for Retry. To transcribe again after removal, upload the original again."
          - generic [ref=e512]:
            - heading "Stored audio" [level=3] [ref=e513]
            - paragraph [ref=e514]: 2 audio files · 128 MB
            - button "Clear stored audio" [ref=e515] [cursor=pointer]
            - paragraph [ref=e516]: Keeps all transcripts and chats. Audio currently being transcribed is skipped. Your original files on your phone or computer are unaffected.
          - region "Transcription glossary" [ref=e517]:
            - heading "Glossary" [level=3] [ref=e518]
            - paragraph [ref=e519]: "One term per line: CORRECT = wrong form, another wrong form. Lines starting with # are comments."
            - generic [ref=e520]: Terms for transcription
            - textbox "Terms for transcription Terms for transcription Terms for transcription" [ref=e521]: Invented Orion = invented orion Invented Ember
            - paragraph [ref=e522]: 2 saved terms
            - button "Save glossary" [ref=e523] [cursor=pointer]
            - paragraph [ref=e524]: New terms apply to recordings you add from now on. To apply them to an older recording, add it again.
          - paragraph [ref=e525]: Transcription stays on your Mac. Transcripts use your local Ollama model.
          - heading "Audio clearing · removing fixture" [level=3] [ref=e526]
          - paragraph [ref=e527]: ● Ready · fake-0.1.0
          - list [ref=e528]:
            - listitem [ref=e529]:
              - generic [ref=e530]: "Fake engine: OK"
              - paragraph [ref=e531]: Synthetic fixture only
          - generic [ref=e532]:
            - switch "Keep web search off in chats with a recording" [checked] [ref=e533] [cursor=pointer]
            - generic [ref=e534]: Keep web search off in chats with a recording
          - generic [ref=e535]:
            - switch "Keep original audio after transcription" [ref=e536] [cursor=pointer]
            - generic [ref=e537]: Keep original audio after transcription
          - paragraph [ref=e538]: "Off by default: audio is removed after the transcript is saved. Text, timestamps and JSON outputs stay available. Failed recordings are kept for Retry. To transcribe again after removal, upload the original again."
          - generic [ref=e539]:
            - heading "Stored audio" [level=3] [ref=e540]
            - paragraph [ref=e541]: 2 audio files · 128 MB
            - button "Clear stored audio" [ref=e542] [cursor=pointer]
            - paragraph [ref=e543]: Keeps all transcripts and chats. Audio currently being transcribed is skipped. Your original files on your phone or computer are unaffected.
          - region "Transcription glossary" [ref=e544]:
            - heading "Glossary" [level=3] [ref=e545]
            - paragraph [ref=e546]: "One term per line: CORRECT = wrong form, another wrong form. Lines starting with # are comments."
            - generic [ref=e547]: Terms for transcription
            - textbox [ref=e548]: Invented Orion = invented orion Invented Ember
            - paragraph [ref=e549]: 2 saved terms
            - button "Save glossary" [ref=e550] [cursor=pointer]
            - paragraph [ref=e551]: New terms apply to recordings you add from now on. To apply them to an older recording, add it again.
          - paragraph [ref=e552]: Transcription stays on your Mac. Transcripts use your local Ollama model.
          - heading "Audio clearing · failed fixture" [level=3] [ref=e553]
          - paragraph [ref=e554]: ● Ready · fake-0.1.0
          - list [ref=e555]:
            - listitem [ref=e556]:
              - generic [ref=e557]: "Fake engine: OK"
              - paragraph [ref=e558]: Synthetic fixture only
          - generic [ref=e559]:
            - switch "Keep web search off in chats with a recording" [checked] [ref=e560] [cursor=pointer]
            - generic [ref=e561]: Keep web search off in chats with a recording
          - generic [ref=e562]:
            - switch "Keep original audio after transcription" [ref=e563] [cursor=pointer]
            - generic [ref=e564]: Keep original audio after transcription
          - paragraph [ref=e565]: "Off by default: audio is removed after the transcript is saved. Text, timestamps and JSON outputs stay available. Failed recordings are kept for Retry. To transcribe again after removal, upload the original again."
          - generic [ref=e566]:
            - heading "Stored audio" [level=3] [ref=e567]
            - paragraph [ref=e568]: 2 audio files · 128 MB
            - button "Clear stored audio" [ref=e569] [cursor=pointer]
            - paragraph [ref=e570]: Keeps all transcripts and chats. Audio currently being transcribed is skipped. Your original files on your phone or computer are unaffected.
          - region "Transcription glossary" [ref=e571]:
            - heading "Glossary" [level=3] [ref=e572]
            - paragraph [ref=e573]: "One term per line: CORRECT = wrong form, another wrong form. Lines starting with # are comments."
            - generic [ref=e574]: Terms for transcription
            - textbox [ref=e575]: Invented Orion = invented orion Invented Ember
            - paragraph [ref=e576]: 2 saved terms
            - button "Save glossary" [ref=e577] [cursor=pointer]
            - paragraph [ref=e578]: New terms apply to recordings you add from now on. To apply them to an older recording, add it again.
          - paragraph [ref=e579]: Transcription stays on your Mac. Transcripts use your local Ollama model.
          - heading "Not set up · fixture" [level=3] [ref=e580]
          - paragraph [ref=e581]: ○ Not set up
          - list [ref=e582]:
            - listitem [ref=e583]:
              - generic [ref=e584]: "Fake engine: Needs attention"
              - paragraph [ref=e585]: Synthetic missing-engine example
          - paragraph [ref=e586]:
            - text: Set
            - code [ref=e587]: WORKBENCH_TRANSCRIBE_HOME
            - text: to the transcription engine folder on your Mac, then restart Atelier.
          - generic [ref=e588]:
            - switch "Keep web search off in chats with a recording" [checked] [ref=e589] [cursor=pointer]
            - generic [ref=e590]: Keep web search off in chats with a recording
          - generic [ref=e591]:
            - switch "Keep original audio after transcription" [ref=e592] [cursor=pointer]
            - generic [ref=e593]: Keep original audio after transcription
          - paragraph [ref=e594]: "Off by default: audio is removed after the transcript is saved. Text, timestamps and JSON outputs stay available. Failed recordings are kept for Retry. To transcribe again after removal, upload the original again."
          - generic [ref=e595]:
            - heading "Stored audio" [level=3] [ref=e596]
            - paragraph [ref=e597]: 2 audio files · 128 MB
            - button "Clear stored audio" [ref=e598] [cursor=pointer]
            - paragraph [ref=e599]: Keeps all transcripts and chats. Audio currently being transcribed is skipped. Your original files on your phone or computer are unaffected.
          - paragraph [ref=e600]: Transcription stays on your Mac. Transcripts use your local Ollama model.
      - region "Reviewed actions and constraints" [ref=e601]:
        - heading "Actions, notifications and configured limits" [level=2] [ref=e602]
        - generic [ref=e603]:
          - paragraph [ref=e604]: Pinned
          - generic [ref=e605]:
            - link "Perfect Thanksgiving Feast" [ref=e606]:
              - /url: /c/design-export
            - img "Pinned chat" [ref=e607]
        - generic [ref=e610]:
          - button "Preview Markdown export" [ref=e611] [cursor=pointer]
          - button "Preview JSON export" [ref=e612] [cursor=pointer]
          - button "Pinned notification" [ref=e613] [cursor=pointer]
          - button "Loading notification" [ref=e614] [cursor=pointer]
          - button "Error notification" [ref=e615] [cursor=pointer]
        - generic [ref=e616]:
          - button "Choose model" [ref=e618] [cursor=pointer]:
            - generic [aria-hidden] [ref=e619]: ○
            - generic [ref=e620]: Fixture model
          - region "Chat controls" [ref=e621]:
            - group [ref=e622]:
              - paragraph [ref=e623]: Fixture model
              - generic [ref=e624]:
                - text: Preset
                - combobox "Preset" [ref=e625] [cursor=pointer]:
                  - generic: None
              - heading "System prompt" [level=3] [ref=e626]
              - generic [ref=e627]:
                - switch "Use default system prompt" [checked] [ref=e628] [cursor=pointer]
                - text: Use default system prompt
              - textbox "System prompt" [disabled] [ref=e629]
              - heading "Sampling" [level=3] [ref=e630]
              - group "Temperature" [ref=e631]:
                - generic [ref=e633]:
                  - switch "Use model default for Temperature" [checked] [ref=e634] [cursor=pointer]
                  - text: Model default
                - paragraph [ref=e635]: Model default
              - group "Top P" [ref=e636]:
                - generic [ref=e638]:
                  - switch "Use model default for Top P" [checked] [ref=e639] [cursor=pointer]
                  - text: Model default
                - paragraph [ref=e640]: Model default
              - group "Top K" [ref=e641]:
                - generic [ref=e643]:
                  - switch "Use model default for Top K" [checked] [ref=e644] [cursor=pointer]
                  - text: Model default
                - paragraph [ref=e645]: Model default
              - group "Max output tokens" [ref=e646]:
                - generic [ref=e648]:
                  - switch "Use model default for Max output tokens" [checked] [ref=e649] [cursor=pointer]
                  - text: Model default
                - paragraph [ref=e650]: Model default
              - group "Seed" [ref=e651]:
                - generic [ref=e653]:
                  - switch "Use model default for Seed" [checked] [ref=e654] [cursor=pointer]
                  - text: Model default
                - paragraph [ref=e655]: Model default
              - button "Save as model defaults" [ref=e656] [cursor=pointer]
              - generic [ref=e657]:
                - text: Reasoning
                - combobox "Reasoning" [ref=e658] [cursor=pointer]:
                  - generic: Model default
              - group "Context length" [ref=e659]:
                - paragraph [ref=e661]: Applies to Fixture model in every chat.
                - spinbutton "Context length" [ref=e662]: "16384"
                - paragraph [ref=e663]: "Configured limit: 16K tokens."
                - generic [ref=e664]:
                  - button "4K" [ref=e665] [cursor=pointer]
                  - button "8K" [ref=e666] [cursor=pointer]
                  - button "16K" [pressed] [ref=e667] [cursor=pointer]
                - button "Apply context length" [disabled]: Apply
              - generic [ref=e668]:
                - button "Save settings" [disabled]
                - button "Reset to model defaults" [ref=e669] [cursor=pointer]
      - region [ref=e670]:
        - heading "Model picker" [level=2] [ref=e671]
        - generic [ref=e672]:
          - generic [ref=e673]:
            - heading "ready" [level=3] [ref=e674]
            - button "Choose model" [ref=e676] [cursor=pointer]:
              - generic [aria-hidden] [ref=e677]: ●
              - generic [ref=e678]: fake-chat
          - generic [ref=e679]:
            - heading "loading" [level=3] [ref=e680]
            - button "Choose model" [ref=e682] [cursor=pointer]:
              - generic [aria-hidden] [ref=e683]: ●
              - generic [ref=e684]: fake-chat
          - generic [ref=e685]:
            - heading "offline" [level=3] [ref=e686]
            - button "Choose model" [ref=e688] [cursor=pointer]:
              - generic [aria-hidden] [ref=e689]: ●
              - generic [ref=e690]: fake-chat
          - generic [ref=e691]:
            - heading "empty" [level=3] [ref=e692]
            - button "Choose model" [ref=e694] [cursor=pointer]:
              - generic [aria-hidden] [ref=e695]: ●
              - generic [ref=e696]: fake-chat
          - generic [ref=e697]:
            - heading "loading-model" [level=3] [ref=e698]
            - button "Choose model" [ref=e700] [cursor=pointer]:
              - generic [aria-hidden] [ref=e701]: ●
              - generic [ref=e702]: fake-chat
      - region [ref=e703]:
        - heading "Sidebar states" [level=2] [ref=e704]
        - generic [ref=e705]:
          - generic [ref=e706]:
            - heading "ready" [level=3] [ref=e707]
            - generic [ref=e709]:
              - generic [ref=e710]:
                - button "Collapse sidebar" [ref=e711] [cursor=pointer]
                - generic [ref=e712]: Atelier
                - link "New chat" [ref=e713]:
                  - /url: /design/chat
              - navigation "Chat history" [ref=e714]:
                - paragraph [ref=e715]: TODAY
                - link "A clearer way to learn" [ref=e717]:
                  - /url: /design/chat/fixture
                - link "Planning a weekend" [ref=e724]:
                  - /url: /design/chat/fixture
                - link "Understanding a short function" [ref=e731]:
                  - /url: /design/chat/fixture
                - link "Making a useful checklist" [ref=e738]:
                  - /url: /design/chat/fixture
                - paragraph [ref=e744]: YESTERDAY
                - link "A fresh perspective" [ref=e745]:
                  - /url: /design/chat/fixture
              - button "Settings" [ref=e749] [cursor=pointer]
          - generic [ref=e750]:
            - heading "loading" [level=3] [ref=e751]
            - generic [ref=e753]:
              - generic [ref=e754]:
                - button "Collapse sidebar" [ref=e755] [cursor=pointer]
                - generic [ref=e756]: Atelier
                - link "New chat" [ref=e757]:
                  - /url: /design/chat
              - navigation "Chat history" [ref=e758]:
                - status "Loading chats" [ref=e759]
              - button "Settings" [ref=e763] [cursor=pointer]
          - generic [ref=e764]:
            - heading "empty" [level=3] [ref=e765]
            - generic [ref=e767]:
              - generic [ref=e768]:
                - button "Collapse sidebar" [ref=e769] [cursor=pointer]
                - generic [ref=e770]: Atelier
                - link "New chat" [ref=e771]:
                  - /url: /design/chat
              - navigation "Chat history" [ref=e772]:
                - paragraph [ref=e773]: No chats yet
              - button "Settings" [ref=e775] [cursor=pointer]
          - generic [ref=e776]:
            - heading "search" [level=3] [ref=e777]
            - generic [ref=e779]:
              - generic [ref=e780]:
                - button "Collapse sidebar" [ref=e781] [cursor=pointer]
                - generic [ref=e782]: Atelier
                - link "New chat" [ref=e783]:
                  - /url: /design/chat
              - navigation "Chat history" [ref=e784]:
                - paragraph [ref=e785]: SEARCH RESULTS
                - link [ref=e787]:
                  - /url: /design/chat/fixture
                  - mark [ref=e788]: A
                  - text: clearer way to learn
                - link [ref=e795]:
                  - /url: /design/chat/fixture
                  - mark [ref=e796]: Planning
                  - text: a weekend
                - link [ref=e803]:
                  - /url: /design/chat/fixture
                  - mark [ref=e804]: Understanding
                  - text: a short function
                - link [ref=e811]:
                  - /url: /design/chat/fixture
                  - mark [ref=e812]: Making
                  - text: a useful checklist
                - paragraph [ref=e818]: YESTERDAY
                - link "A fresh perspective" [ref=e819]:
                  - /url: /design/chat/fixture
              - button "Settings" [ref=e823] [cursor=pointer]
          - generic [ref=e824]:
            - heading "error" [level=3] [ref=e825]
            - generic [ref=e827]:
              - generic [ref=e828]:
                - button "Collapse sidebar" [ref=e829] [cursor=pointer]
                - generic [ref=e830]: Atelier
                - link "New chat" [ref=e831]:
                  - /url: /design/chat
              - navigation "Chat history" [ref=e832]:
                - generic [ref=e833]:
                  - text: Couldn’t load chats
                  - button "Retry" [ref=e834] [cursor=pointer]
              - button "Settings" [ref=e836] [cursor=pointer]
          - generic [ref=e837]:
            - heading "Collapsed rail" [level=3] [ref=e838]
            - generic [ref=e840]:
              - button "Expand sidebar" [ref=e842] [cursor=pointer]
              - link "New chat" [ref=e843]:
                - /url: /design/chat
              - button "Search chats" [ref=e844] [cursor=pointer]
              - navigation "Chat history" [ref=e845]
              - button "Settings" [ref=e847] [cursor=pointer]
      - region [ref=e848]:
        - heading "Messages" [level=2] [ref=e849]
        - generic [ref=e850]:
          - heading "User · text, attachment, edit" [level=3] [ref=e851]
          - article "user message" [ref=e852]:
            - heading "You said" [level=2] [ref=e853]
            - paragraph [ref=e855]: Explain a useful way to learn something new.
            - generic [ref=e858]:
              - button "Copy message" [ref=e859] [cursor=pointer]:
                - status [ref=e860]
              - button "Edit message" [ref=e861] [cursor=pointer]
          - article "user message" [ref=e862]:
            - heading "You said" [level=2] [ref=e863]
            - generic [ref=e864]:
              - paragraph [ref=e865]: Explain a useful way to learn something new.
              - link "fake-notes.md" [ref=e866]:
                - /url: /api/attachments/fake-note
            - generic [ref=e869]:
              - button "Copy message" [ref=e870] [cursor=pointer]:
                - status [ref=e871]
              - button "Edit message" [ref=e872] [cursor=pointer]
          - article "user message" [ref=e873]:
            - heading "You said" [level=2] [ref=e874]
            - generic [ref=e875]:
              - textbox "Edit message" [ref=e876]: Explain a useful way to learn something new.
              - generic [ref=e877]:
                - button "Cancel" [ref=e878] [cursor=pointer]
                - button "Send" [ref=e879] [cursor=pointer]
            - generic [ref=e882]:
              - button "Copy message" [ref=e883] [cursor=pointer]:
                - status [ref=e884]
              - button "Edit message" [ref=e885] [cursor=pointer]
        - generic [ref=e886]:
          - heading "Assistant · complete" [level=3] [ref=e887]
          - article "assistant message" [ref=e888]:
            - heading "fake-chat replied" [level=2] [ref=e889]
            - paragraph [ref=e890]: Fake runtime · fake-chat
            - button "Thought for 0s" [ref=e892] [cursor=pointer]
            - generic [ref=e904]:
              - status [ref=e905]
              - generic [ref=e906]:
                - paragraph [ref=e907]: A small change is easier to understand when you can see each step. Here’s a practical way to approach it.
                - heading "Start with a clear question" [level=2] [ref=e908]
                - paragraph [ref=e909]: "Write down what you want to learn, then keep the first experiment small:"
                - list [ref=e910]:
                  - listitem [ref=e911]: Choose one thing to change.
                  - listitem [ref=e912]: Observe what happens.
                  - listitem [ref=e913]: Compare it with your starting point.
                - region "Answer table" [ref=e914]:
                  - region "Answer table" [ref=e915]:
                    - table [ref=e916]:
                      - rowgroup [ref=e917]:
                        - row [ref=e918]:
                          - columnheader "Step" [ref=e919]
                          - columnheader "What to keep" [ref=e920]
                          - columnheader "What to check" [ref=e921]
                      - rowgroup [ref=e922]:
                        - row [ref=e923]:
                          - cell "Prepare" [ref=e924]
                          - cell "Your original example" [ref=e925]
                          - cell "A clear starting point" [ref=e926]
                        - row [ref=e927]:
                          - cell "Try" [ref=e928]
                          - cell "One small change" [ref=e929]
                          - cell "The result you observed" [ref=e930]
                        - row [ref=e931]:
                          - cell "Reflect" [ref=e932]
                          - cell "Your notes" [ref=e933]
                          - cell "What to try next" [ref=e934]
                - heading "A simple example" [level=2] [ref=e935]
                - generic [ref=e936]:
                  - generic [ref=e937]: python
                  - button "Copy Code" [ref=e940] [cursor=pointer]
                  - region "Code example" [ref=e943]:
                    - code [ref=e945]:
                      - generic [ref=e946]: steps = ["Prepare", "Try", "Reflect"]
                      - generic [ref=e947]: "for step in steps:"
                      - generic [ref=e948]: print(step)
                - blockquote [ref=e949]:
                  - paragraph [ref=e950]: Good notes make the next question easier to ask.
                - paragraph [ref=e951]: This is a fixture from the Fake runtime, for reviewing the interface. No local model generated this answer.
            - generic [ref=e954]:
              - button "Copy message" [ref=e955] [cursor=pointer]:
                - status [ref=e956]
              - button "Regenerate answer" [ref=e957] [cursor=pointer]
              - button "Regenerate with another model" [ref=e958] [cursor=pointer]
              - button "Message info" [ref=e959] [cursor=pointer]
        - generic [ref=e960]:
          - generic [ref=e961]:
            - heading "queued" [level=3] [ref=e962]
            - article "assistant message" [ref=e963]:
              - heading "fake-chat replied" [level=2] [ref=e964]
              - paragraph [ref=e965]: Fake runtime · fake-chat
              - status [ref=e966]: Waiting for Fake runtime · fake-chat…
              - status [ref=e969]
          - generic [ref=e970]:
            - heading "loading-model" [level=3] [ref=e971]
            - article "assistant message" [ref=e972]:
              - heading "fake-chat replied" [level=2] [ref=e973]
              - paragraph [ref=e974]: Fake runtime · fake-chat
              - status [ref=e975]: Loading model…
              - status [ref=e978]
          - generic [ref=e979]:
            - heading "waiting" [level=3] [ref=e980]
            - article "assistant message" [ref=e981]:
              - heading "fake-chat replied" [level=2] [ref=e982]
              - paragraph [ref=e983]: Fake runtime · fake-chat
              - status [ref=e984]:
                - generic [ref=e985]: Generating response
              - status [ref=e989]
          - generic [ref=e990]:
            - heading "reasoning" [level=3] [ref=e991]
            - article "assistant message" [ref=e992]:
              - heading "fake-chat replied" [level=2] [ref=e993]
              - paragraph [ref=e994]: Fake runtime · fake-chat
              - generic [ref=e995]:
                - button "Thinking… 44s" [expanded] [ref=e996] [cursor=pointer]
                - generic [ref=e1008]: Synthetic reasoning. Compare one small change with your starting point.
              - status [ref=e1009]
          - generic [ref=e1010]:
            - heading "streaming" [level=3] [ref=e1011]
            - article "assistant message" [ref=e1012]:
              - heading "fake-chat replied" [level=2] [ref=e1013]
              - paragraph [ref=e1014]: Fake runtime · fake-chat
              - generic [ref=e1015]:
                - status [ref=e1016]
                - paragraph [ref=e1018]:
                  - text: A partial answer from the Fake runtime.
                  - generic [ref=e1019]: Formatting stays readable
                  - text: while the rest arrives.
          - generic [ref=e1020]:
            - heading "stopped" [level=3] [ref=e1021]
            - article "assistant message" [ref=e1022]:
              - heading "fake-chat replied" [level=2] [ref=e1023]
              - paragraph [ref=e1024]: Fake runtime · fake-chat
              - generic [ref=e1025]:
                - status [ref=e1026]
                - paragraph [ref=e1028]: A partial answer from the Fake runtime. Formatting stays readable while the rest arrives.
              - generic [ref=e1029]:
                - generic [ref=e1031]:
                  - button "Copy message" [ref=e1032] [cursor=pointer]:
                    - status [ref=e1033]
                  - button "Regenerate answer" [ref=e1034] [cursor=pointer]
                  - button "Regenerate with another model" [ref=e1035] [cursor=pointer]
                  - button "Message info" [ref=e1036] [cursor=pointer]
                - paragraph [ref=e1038]: Stopped
          - generic [ref=e1039]:
            - heading "error" [level=3] [ref=e1040]
            - article "assistant message" [ref=e1041]:
              - heading "fake-chat replied" [level=2] [ref=e1042]
              - paragraph [ref=e1043]: Fake runtime · fake-chat
              - generic [ref=e1044]:
                - status [ref=e1045]
                - paragraph [ref=e1047]: A partial answer from the Fake runtime. Formatting stays readable while the rest arrives.
              - alert [ref=e1048]:
                - paragraph [ref=e1049]: Can't reach Ollama at the configured address. Is it running?
                - generic [ref=e1052]:
                  - button "Retry" [ref=e1053] [cursor=pointer]
                  - button "Open settings" [ref=e1054] [cursor=pointer]
              - generic [ref=e1057]:
                - button "Copy message" [ref=e1058] [cursor=pointer]:
                  - status [ref=e1059]
                - button "Regenerate answer" [ref=e1060] [cursor=pointer]
                - button "Regenerate with another model" [ref=e1061] [cursor=pointer]
                - button "Message info" [ref=e1062] [cursor=pointer]
          - generic [ref=e1063]:
            - heading "interrupted" [level=3] [ref=e1064]
            - article "assistant message" [ref=e1065]:
              - heading "fake-chat replied" [level=2] [ref=e1066]
              - paragraph [ref=e1067]: Fake runtime · fake-chat
              - generic [ref=e1068]:
                - status [ref=e1069]
                - paragraph [ref=e1071]: A partial answer from the Fake runtime. Formatting stays readable while the rest arrives.
              - alert [ref=e1072]:
                - paragraph [ref=e1073]: Interrupted because the server restarted.
                - button "Retry" [ref=e1077] [cursor=pointer]
              - generic [ref=e1080]:
                - button "Copy message" [ref=e1081] [cursor=pointer]:
                  - status [ref=e1082]
                - button "Regenerate answer" [ref=e1083] [cursor=pointer]
                - button "Regenerate with another model" [ref=e1084] [cursor=pointer]
                - button "Message info" [ref=e1085] [cursor=pointer]
      - region [ref=e1086]:
        - heading "Composer" [level=2] [ref=e1087]
        - generic [ref=e1088]:
          - form "Message" [ref=e1089]:
            - textbox "Message fake-chat" [ref=e1090]:
              - /placeholder: Message fake-chat…
            - generic [ref=e1091]:
              - button "Add attachment" [ref=e1092] [cursor=pointer]
              - button "Web search" [ref=e1093] [cursor=pointer]
              - generic [ref=e1094]:
                - img "6,200 of 16,384 total tokens; 12,032 input allowance; 4,096 reserved for response; 256 safety margin" [ref=e1095]
                - generic [ref=e1099]:
                  - button "Send message" [disabled]
          - generic [ref=e1100]:
            - button "Explain" [ref=e1101] [cursor=pointer]
            - button "Write" [ref=e1102] [cursor=pointer]
            - button "Code" [ref=e1103] [cursor=pointer]
            - button "Search the web" [ref=e1104] [cursor=pointer]
          - form "Message" [ref=e1105]:
            - generic [ref=e1106]:
              - generic [ref=e1107]: fake-notes.md
              - button "Remove fake-notes.md" [ref=e1108] [cursor=pointer]
            - textbox "Message fake-reasoning" [ref=e1109]:
              - /placeholder: Message fake-reasoning…
              - text: An editable fixture message
            - generic [ref=e1110]:
              - button "Add attachment" [ref=e1111] [cursor=pointer]
              - 'button "Think: Model default" [ref=e1112] [cursor=pointer]'
              - generic [ref=e1113]:
                - img "Context usage unavailable" [ref=e1114]
                - button "Send message" [ref=e1119] [cursor=pointer]
          - form "Message" [ref=e1121]:
            - textbox "Message fake-chat" [ref=e1122]:
              - /placeholder: Message fake-chat…
              - text: A fixture message in progress
            - generic [ref=e1123]:
              - button "Add attachment" [ref=e1124] [cursor=pointer]
              - generic [ref=e1125]:
                - img "Context usage unavailable" [ref=e1126]
                - button "Stop generating" [ref=e1131] [cursor=pointer]
      - region [ref=e1133]:
        - heading "Chat controls · model defaults" [level=2] [ref=e1134]
        - region "Chat controls" [ref=e1136]:
          - generic [ref=e1137]:
            - heading "Chat controls" [level=2] [ref=e1138]
            - button "Close chat controls" [ref=e1139] [cursor=pointer]
          - group [ref=e1140]:
            - paragraph [ref=e1141]: fake-reasoning
            - generic [ref=e1142]:
              - text: Preset
              - combobox "Preset" [ref=e1143] [cursor=pointer]:
                - generic: None
            - heading "System prompt" [level=3] [ref=e1144]
            - generic [ref=e1145]:
              - switch "Use default system prompt" [checked] [ref=e1146] [cursor=pointer]
              - text: Use default system prompt
            - textbox "System prompt" [disabled] [ref=e1147]
            - heading "Sampling" [level=3] [ref=e1148]
            - group "Temperature" [ref=e1149]:
              - generic [ref=e1151]:
                - switch "Use model default for Temperature" [checked] [ref=e1152] [cursor=pointer]
                - text: Model default
              - paragraph [ref=e1153]: Model default
            - group "Top P" [ref=e1154]:
              - generic [ref=e1156]:
                - switch "Use model default for Top P" [checked] [ref=e1157] [cursor=pointer]
                - text: Model default
              - paragraph [ref=e1158]: Model default
            - group "Top K" [ref=e1159]:
              - generic [ref=e1161]:
                - switch "Use model default for Top K" [checked] [ref=e1162] [cursor=pointer]
                - text: Model default
              - paragraph [ref=e1163]: Model default
            - group "Max output tokens" [ref=e1164]:
              - generic [ref=e1166]:
                - switch "Use model default for Max output tokens" [checked] [ref=e1167] [cursor=pointer]
                - text: Model default
              - paragraph [ref=e1168]: Model default
            - group "Seed" [ref=e1169]:
              - generic [ref=e1171]:
                - switch "Use model default for Seed" [checked] [ref=e1172] [cursor=pointer]
                - text: Model default
              - paragraph [ref=e1173]: Model default
            - button "Save as model defaults" [ref=e1174] [cursor=pointer]
            - generic [ref=e1175]:
              - text: Reasoning
              - combobox "Reasoning" [ref=e1176] [cursor=pointer]:
                - generic: Model default
            - group "Context length" [ref=e1177]:
              - paragraph [ref=e1179]: Applies to fake-reasoning in every chat.
              - spinbutton "Context length" [ref=e1180]: "16384"
              - paragraph [ref=e1181]: "Configured limit: 16K tokens."
              - generic [ref=e1182]:
                - button "4K" [ref=e1183] [cursor=pointer]
                - button "8K" [ref=e1184] [cursor=pointer]
                - button "16K" [pressed] [ref=e1185] [cursor=pointer]
              - button "Apply context length" [disabled]: Apply
            - generic [ref=e1186]:
              - button "Save settings" [disabled]
              - button "Reset to model defaults" [ref=e1187] [cursor=pointer]
      - region [ref=e1188]:
        - heading "Markdown safety" [level=2] [ref=e1189]
        - generic [ref=e1190]:
          - status [ref=e1191]
          - generic [ref=e1192]:
            - paragraph [ref=e1193]:
              - 'generic "Blocked URL: undefined" [ref=e1194]': Unsafe link [blocked]
            - link "Remote example ↗" [ref=e1195]:
              - /url: https://example.invalid/picture.jpg
        - paragraph [ref=e1196]: Remote images appear as links. Raw HTML and unsafe links are disabled.
      - region [ref=e1197]:
        - heading "Screen previews" [level=2] [ref=e1198]
        - generic [ref=e1199]:
          - link "New chat" [ref=e1200]:
            - /url: /
          - link "Completed chat" [ref=e1201]:
            - /url: /design/chat/fixture
          - button "Settings dialog" [ref=e1202] [cursor=pointer]
          - button "Chat search" [ref=e1203] [cursor=pointer]
        - paragraph [ref=e1204]: Component fixtures are synthetic. Open New chat to use your configured Ollama connection and web search. This guide does not read your chats or perform searches.
  - region "Notifications alt+T"
```

# Test source

```ts
  543 | for (const width of [390, 1440])
  544 |   for (const theme of ["light", "dark"]) {
  545 |     test(`conversation states and chat exports have no serious accessibility findings ${width} ${theme}`, async ({
  546 |       page,
  547 |       request,
  548 |     }) => {
  549 |       const { default: AxeBuilder } = await import("@axe-core/playwright");
  550 |       await request.patch("/api/settings", {
  551 |         data: {
  552 |           "appearance.theme": theme,
  553 |           "appearance.reduce_motion": "system",
  554 |         },
  555 |       });
  556 |       await page.setViewportSize({ width, height: 900 });
  557 |       await page.goto("/design");
  558 |       await page
  559 |         .locator(".design-page > header")
  560 |         .getByRole("button", {
  561 |           name: theme === "dark" ? "Dark" : "Light",
  562 |           exact: true,
  563 |         })
  564 |         .click();
  565 |       const preview = page.getByRole("region", {
  566 |         name: "Conversation motion",
  567 |         exact: true,
  568 |       });
  569 |       const results: { state: string; violations: string[] }[] = [];
  570 |       for (const state of [
  571 |         "optimistic",
  572 |         "waiting",
  573 |         "reasoning",
  574 |         "streaming",
  575 |         "search",
  576 |         "complete",
  577 |       ]) {
  578 |         await preview
  579 |           .getByRole("button", { name: `Preview ${state}`, exact: true })
  580 |           .click();
  581 |         await settle(page);
  582 |         const axe = await new AxeBuilder({ page })
  583 |           .include('[aria-label="Conversation motion"]')
  584 |           .analyze();
  585 |         const violations = axe.violations.filter((item) =>
  586 |           ["serious", "critical"].includes(item.impact ?? ""),
  587 |         );
  588 |         results.push({ state, violations: violations.map((item) => item.id) });
  589 |         expect(violations).toEqual([]);
  590 |       }
  591 |       await page
  592 |         .getByRole("button", { name: "Preview JSON export", exact: true })
  593 |         .click();
  594 |       const dialog = page.getByRole("dialog", {
  595 |         name: "Export chat",
  596 |         exact: true,
  597 |       });
  598 |       await settle(page);
  599 |       await expect(
  600 |         dialog.getByRole("button", { name: "Cancel", exact: true }),
  601 |       ).toBeInViewport({ ratio: 1 });
  602 |       const axe = await new AxeBuilder({ page }).analyze();
  603 |       const violations = axe.violations.filter((item) =>
  604 |         ["serious", "critical"].includes(item.impact ?? ""),
  605 |       );
  606 |       results.push({
  607 |         state: "export-json",
  608 |         violations: violations.map((item) => item.id),
  609 |       });
  610 |       expect(violations).toEqual([]);
  611 |       await mkdir("../artifacts/phase-4/4c", { recursive: true });
  612 |       await page.screenshot({
  613 |         path: `../artifacts/phase-4/4c/export-${width}-${theme}-${test.info().project.name}-fake.png`,
  614 |         animations: "disabled",
  615 |       });
  616 |       await writeFile(
  617 |         `../artifacts/phase-4/4c/axe-${width}-${theme}-${test.info().project.name}-fake.json`,
  618 |         JSON.stringify(results, null, 2),
  619 |       );
  620 |     });
  621 |   }
  622 | 
  623 | test("code and transcript copy show a local check and clear it after 1.5 seconds", async ({
  624 |   page,
  625 | }) => {
  626 |   await page.goto("/design");
  627 |   await page.evaluate(() =>
  628 |     Object.defineProperty(navigator, "clipboard", {
  629 |       configurable: true,
  630 |       value: { writeText: async () => {} },
  631 |     }),
  632 |   );
  633 |   const preview = page.getByRole("region", {
  634 |     name: "Conversation motion",
  635 |     exact: true,
  636 |   });
  637 |   await preview
  638 |     .getByRole("button", { name: "Preview complete", exact: true })
  639 |     .click();
  640 |   const code = preview
  641 |     .locator('[data-streamdown="code-block-copy-button"]')
  642 |     .first();
> 643 |   await code.click();
      |              ^ Error: locator.click: Test timeout of 45000ms exceeded.
  644 |   await expect(code.locator('[data-slot="copy-check"]')).toBeVisible();
  645 |   await expect(
  646 |     preview.getByRole("status").filter({ hasText: "Copied" }),
  647 |   ).toContainText("Copied");
  648 |   await expect(code.locator('[data-slot="copy-check"]')).toHaveCount(0);
  649 |   await page
  650 |     .getByRole("button", { name: "Preview transcript panel", exact: true })
  651 |     .click();
  652 |   const transcript = page.getByRole("dialog", {
  653 |     name: "Synthetic recording.wav",
  654 |     exact: true,
  655 |   });
  656 |   await transcript.getByRole("button", { name: "Copy", exact: true }).click();
  657 |   await expect(transcript.locator('[data-slot="copy-check"]')).toBeVisible();
  658 |   await expect(
  659 |     transcript.getByRole("status").filter({ hasText: "Copied" }),
  660 |   ).toHaveText("Copied");
  661 |   await expect(transcript.locator('[data-slot="copy-check"]')).toHaveCount(0);
  662 |   await expect(page.locator("[data-sonner-toast]")).toHaveCount(0);
  663 | });
  664 | 
  665 | // Capture short-lived flags on the page clock so automation latency cannot miss them.
  666 | test("new-chat send waits for confirmation; edit and regenerate animate only newly confirmed rows", async ({
  667 |   page,
  668 |   request,
  669 | }) => {
  670 |   await existing(page, request);
  671 |   await page.goto("/");
  672 |   await page.addInitScript(() => {
  673 |     document.addEventListener("DOMContentLoaded", () => {
  674 |       const seen: Set<string> = new Set();
  675 |       Object.defineProperty(window, "freshSeen", { value: seen });
  676 |       const inspect = () =>
  677 |         document
  678 |           .querySelectorAll('article[data-fresh="true"]')
  679 |           .forEach((element) =>
  680 |             seen.add(element.getAttribute("data-message-id")!),
  681 |           );
  682 |       new MutationObserver(inspect).observe(document, {
  683 |         subtree: true,
  684 |         attributes: true,
  685 |         childList: true,
  686 |       });
  687 |     });
  688 |   });
  689 |   await page.reload();
  690 |   await page.route("**/api/chats/*/messages", async (route) => {
  691 |     await new Promise((resolve) => setTimeout(resolve, 500));
  692 |     await route.continue();
  693 |   });
  694 |   const field = page.locator(".composer textarea");
  695 |   await field.fill("Synthetic first message #long:30 #slow:30");
  696 |   await page.getByRole("button", { name: "Send message", exact: true }).click();
  697 |   await expect(field).toHaveValue("Synthetic first message #long:30 #slow:30");
  698 |   await expect(page.getByTestId("optimistic-send")).toHaveCount(0);
  699 |   await expect(page).toHaveURL(/\/c\//);
  700 |   const id = page.url().split("/c/")[1];
  701 |   await expect(
  702 |     page.getByRole("button", { name: "Stop generating", exact: true }),
  703 |   ).not.toBeVisible({ timeout: 10000 });
  704 |   let detail = await (await request.get(`/api/chats/${id}`)).json();
  705 |   let seen = await page.evaluate(() => [
  706 |     ...(window as unknown as { freshSeen: Set<string> }).freshSeen,
  707 |   ]);
  708 |   for (const message of detail.messages) expect(seen).toContain(message.id);
  709 |   await page
  710 |     .getByRole("button", { name: "Regenerate answer", exact: true })
  711 |     .click();
  712 |   await expect(
  713 |     page.getByRole("button", { name: "Stop generating", exact: true }),
  714 |   ).toBeVisible();
  715 |   await expect(
  716 |     page.getByRole("button", { name: "Stop generating", exact: true }),
  717 |   ).not.toBeVisible({ timeout: 10000 });
  718 |   detail = await (await request.get(`/api/chats/${id}`)).json();
  719 |   seen = await page.evaluate(() => [
  720 |     ...(window as unknown as { freshSeen: Set<string> }).freshSeen,
  721 |   ]);
  722 |   for (const message of detail.messages) expect(seen).toContain(message.id);
  723 |   await page.getByRole("button", { name: "Edit message", exact: true }).click();
  724 |   await page
  725 |     .getByRole("textbox", { name: "Edit message", exact: true })
  726 |     .fill("Synthetic edited message #long:30 #slow:30");
  727 |   await page.getByRole("button", { name: "Send", exact: true }).click();
  728 |   await expect(
  729 |     page.getByRole("button", { name: "Stop generating", exact: true }),
  730 |   ).toBeVisible();
  731 |   await expect(
  732 |     page.getByRole("button", { name: "Stop generating", exact: true }),
  733 |   ).not.toBeVisible({ timeout: 10000 });
  734 |   detail = await (await request.get(`/api/chats/${id}`)).json();
  735 |   seen = await page.evaluate(() => [
  736 |     ...(window as unknown as { freshSeen: Set<string> }).freshSeen,
  737 |   ]);
  738 |   for (const message of detail.messages) expect(seen).toContain(message.id);
  739 |   await page.reload();
  740 |   await expect(page.getByRole("article")).toHaveCount(2);
  741 |   expect(await page.locator('article[data-fresh="true"]').count()).toBe(0);
  742 | });
  743 | 
```