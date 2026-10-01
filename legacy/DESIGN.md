# Chat & Web design

Use the established Graphite & Cobalt appearance tokens in `src/agenticrag/ui/tokens.css`. Geist is the UI font; Newsreader is the default answer font. Retain Light, Dark, Paper and Midnight themes, and persisted font/text-size preferences.

The answer is the primary content. Configuration belongs in Models or Settings. The composer has one text box, a compact Web control, image attachment, dictation and Send/Stop. The selected model stays visible in the header with an accurate loaded-state indicator.

Use a desktop sidebar and a mobile drawer. The composer and scrolling thread occupy separate layout rows; neither overlays the other. Citation snapshots open in a viewport-bounded dialog. Long titles and model IDs truncate in the header and wrap in lists; tables scroll within messages. Buttons have 44px touch targets. Use visible focus rings, accessible control names, reduced-motion support and locally served fonts.
