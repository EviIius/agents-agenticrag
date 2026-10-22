# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: photo-mask-protection.spec.ts >> zoom and move retain submitted pointer coordinates
- Location: tests/photo-mask-protection.spec.ts:152:1

# Error details

```
Test timeout of 45000ms exceeded.
```

# Page snapshot

```yaml
- generic:
  - generic:
    - generic [aria-hidden]:
      - complementary:
        - generic:
          - generic:
            - button
            - generic: Aether
            - link:
              - /url: /
          - navigation:
            - generic:
              - textbox:
                - /placeholder: Search chats…
              - generic: ⌘K
            - navigation:
              - generic:
                - link:
                  - /url: /workflows
                  - text: Workflows
              - generic:
                - link:
                  - /url: /images
                  - text: Images
            - region:
              - generic:
                - heading [level=2]: Folders
                - button
              - paragraph: No folders yet
            - paragraph: No chats yet
          - generic:
            - button: Settings
      - main:
        - generic:
          - generic:
            - button:
              - generic [aria-hidden]: ●
              - generic: fake-chat
              - generic: Fake runtime
          - button
        - generic:
          - heading [level=1]: Good evening
          - form:
            - generic:
              - generic:
                - button
                - generic:
                  - paragraph: Photo reference
                  - paragraph: Ready · 1024 × 1024
                - button
              - generic:
                - button: Select edit area
              - paragraph: Select an area to protect the rest. Without a selection, the whole photo can change. Your original stays private.
            - textbox:
              - /placeholder: Describe what to change…
              - text: Synthetic protected change
            - generic:
              - button
              - button: Edit photo
              - generic:
                - generic:
                  - button
          - paragraph: Your models. Your Mac.
    - region "Notifications alt+T"
  - dialog [ref=e2]:
    - heading "Select edit area" [level=2] [ref=e3]
    - paragraph [ref=e4]: Paint the existing area to replace and room for additions. Protect removes paint; those pixels stay unchanged.
    - group "Selection tool" [ref=e5]:
      - button "Paint" [active] [pressed] [ref=e6] [cursor=pointer]
      - button "Protect" [ref=e7] [cursor=pointer]
      - button "Move" [ref=e8] [cursor=pointer]
    - generic [ref=e9]:
      - group "Photo zoom" [ref=e10]:
        - button "Zoom out" [ref=e11] [cursor=pointer]: −
        - button "Fit photo" [ref=e12] [cursor=pointer]: 3×
        - button "Zoom in" [ref=e13] [cursor=pointer]: +
      - group "Mask view" [ref=e14]:
        - button "Overlay" [pressed] [ref=e15] [cursor=pointer]
        - button "Selected" [ref=e16] [cursor=pointer]
        - button "Protected" [ref=e17] [cursor=pointer]
    - img "Photo selection canvas. Paint or protect with a pointer, or use arrow keys and Space. Choose Move to pan." [ref=e20]
    - paragraph [ref=e21]: Painted areas may change. The rest stays protected. Zoom in for details; choose Move to pan.
    - generic [ref=e22]:
      - generic [ref=e23]: Brush size
      - generic "Brush size" [ref=e24]:
        - slider "Brush size" [ref=e28]
    - status [ref=e29]: 1 brush stroke · about less than 1% selected
    - paragraph [ref=e30]: "Check coverage before applying: include the surface beneath each addition, not just the empty space around it."
    - generic [ref=e31]:
      - button "Undo" [ref=e32] [cursor=pointer]
      - button "Redo" [disabled]
      - button "Clear" [ref=e33] [cursor=pointer]
      - button "Cancel" [ref=e34] [cursor=pointer]
      - button "Use selection" [ref=e35] [cursor=pointer]
    - button "Close" [ref=e36] [cursor=pointer]
```