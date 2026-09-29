# Installed model health check — 29 September 2026

Checks ran against an isolated, in-memory workbench pointed at the Mac mini's Ollama runtime. Each chat model received the same short streamed Direct prompt and the workbench's structured agent-contract check. Times include any model load or swap and are not speed benchmarks.

| Chat model | Direct | Agent contract |
| --- | --- | --- |
| `gemma4:12b-mlx` | Pass, 0.25 s | Pass, 1.05 s |
| `gpt-oss:20b` | Pass, 3.58 s | Pass, 6.72 s |
| `qwen3:30b-a3b-workbench-32k` | Pass, 3.91 s | Pass, 0.88 s |
| `qwen3:30b-a3b-instruct-2507-q4_K_M` | Pass, 3.12 s | Pass, 0.84 s |
| `llama3.3:70b-workbench-16k` | Pass, 8.83 s | Pass, 9.23 s |
| `llama3.3:70b-instruct-q4_K_M` | Pass, 91.18 s | **Timed out**, 185.18 s |

`qwen3-embedding:0.6b` returned one valid 1,024-dimensional vector in 0.82 s.

Gemma also passed a vision request through both the Ollama API and the workbench's Direct streaming endpoint. A phone-sized browser run attached `icon-192.png`, sent an image question, received the answer and reported no JavaScript errors. The user's screenshot showed a browser exception from a progress callback that assumed the loading note still existed after streaming replaced its markup. That callback now checks for the element before updating it.

The full-context Llama 70B model can answer Direct prompts, but its agent contract exceeded the configured 180-second provider timeout. Use `llama3.3:70b-workbench-16k` for agent workflows on this machine. A single contract pass does not establish reliability or answer quality across tasks.
