# Local workbench mode guide

This original example describes the four workbench modes so a user can test answers against a known source.

| Mode | What it does | Uses indexed sources? |
| --- | --- | --- |
| Direct | Chats with the selected local model using recent turns from this conversation. | No |
| Fixed | Retrieves relevant passages, then answers from them with source citations. | Yes |
| Agentic | Plans a bounded sequence of read-only search, lookup, and calculation actions before reviewing a cited answer. | Yes |
| Supervisor | Plans up to three bounded specialist assignments and synthesizes their reports. | Usually |

The collection ID groups indexed documents. The access label is an authorization filter used when retrieving them. The initial local example collection uses the ID `research` and access label `private`. These are labels in the local workbench, not a login system and not proof that the service is safe to expose publicly.

Conversations are saved on the Mac mini in a separate local database. Recent prior turns are passed to Direct responses; questions explicitly asking about previous chat questions use that same conversation context even if a grounded mode is selected. A new chat begins without earlier turns. This conversation history is separate from the indexed source corpus.
