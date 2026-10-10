# Local image generation options — 10 October 2026

## Recommendation

Yes: this Mac is a credible host for local image generation. Read-only hardware
inspection reports **Mac mini, Apple M5 Pro, 64 GB unified memory, 16 GPU cores**.
This is a hardware-fit inference supported by existing Apple implementations;
none of these models has been downloaded or benchmarked here.

Start with **FLUX.2 klein 4B** for a general generation/editing trial, then compare
**Z-Image-Turbo** for photography. Their smaller distilled pipelines are sensible
first candidates. The ranking below is a testing recommendation, not a measured
quality ranking. Keep Qwen image models as separate image candidates; they are
different pipelines from the currently installed Qwen chat models.

## Shortlist

| Candidate | Intended trial | Size/steps and published fit | License shown by publisher | Mac assessment |
| --- | --- | --- | --- | --- |
| [FLUX.2 klein 4B](https://huggingface.co/black-forest-labs/FLUX.2-klein-4B) | First: general images and reference editing | 4B image transformer, four steps; publisher reports about 13 GB consumer-GPU VRAM | Apache 2.0 | Credible first fit; Draw Things and MFLUX implementations exist |
| [Z-Image-Turbo](https://huggingface.co/Tongyi-MAI/Z-Image-Turbo) | Second: photographic scenes and short English/Chinese text | 6B, eight function evaluations; publisher reports fitting 16 GB consumer VRAM | Apache 2.0 | Credible first fit; compare prompt adherence and speed locally |
| [Qwen-Image-2512](https://huggingface.co/Qwen/Qwen-Image-2512) | Detailed layouts and text in images | Larger Qwen Image family; publisher reports improved realism and text accuracy | Apache 2.0 | Plausible on 64 GB with quantization; test after the smaller candidates |
| [FLUX.2 klein 9B](https://huggingface.co/black-forest-labs/FLUX.2-klein-9B) | Compare reference editing with 4B | 9B transformer plus 8B text encoder, four steps | FLUX non-commercial; gated weights | Plausible, but larger residency and restricted license make it a later comparison |
| [Qwen-Image-2.1](https://huggingface.co/Qwen/Qwen-Image-2.1) | Watchlist: transparent images and multi-reference editing | 7B visual component; publisher examples use 40 steps, up to ten references | Qwen Research License | MLX implementation exists; newest features and intended-use terms require separate verification |
| [SDXL 1.0 base](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0) | Established fallback for illustrations and model ecosystem | Base can run alone; refiner is optional | CreativeML Open RAIL++-M | Useful fallback; measure its quality against the newer candidates |

The VRAM figures above describe publisher consumer-GPU configurations, **not
measured Apple unified-memory peaks**. H800/RTX sub-second claims do not establish
Mac mini latency. Transformer parameter counts omit encoders, VAE, activations
and temporary conversion/storage costs.

## Two practical Mac implementations

**Draw Things is my first choice for a manual Mac trial.** Its release notes
explicitly list klein, Z-Image-Turbo and Qwen Image 2512 support, plus M5-specific
inference improvements. Use local computation for the proposed trial. This is
documentation review, not a verified installation or API test.
[Official release history](https://drawthings.ai/downloads/).

Its public HTTP server implements text-to-image and image-to-image routes, so
an Atelier adapter is technically plausible. That source returns results after
generation; it does not establish the progress, cancellation or multi-reference
capabilities needed for a good phone workflow. Verify those before choosing it
for integration. [HTTP server source](https://github.com/drawthingsai/draw-things-community/blob/main/Libraries/HTTPAPIServer/Sources/HTTPAPIServer.swift).

**MFLUX is the alternative for a controlled worker.** The project provides MLX
implementations, CLI/Python entry points and quantization. It lists klein, Z-Image,
Qwen Image and Qwen Image 2.1. A separate environment would keep its dependencies
out of the existing chat server. Its first model execution can download weights;
no command has been run. [Project documentation](https://github.com/mflux-community/mflux).

MFLUX's klein documentation estimates about **15 GB** of default weight downloads
for 4B and **32 GB** for 9B, with smaller quantized options. Disk footprint and
peak memory must be measured separately. [Klein implementation notes](https://github.com/mflux-community/mflux/blob/main/src/mflux/models/flux2/README.md).

For Qwen 2.1, MFLUX describes about **33 GB** of BF16 weights, including a large
text encoder. Its default generation path returns RGB; reference editing has a
separate path. Publisher RGBA capability therefore cannot be assumed for every
Mac entry point. [Qwen 2.1 implementation notes](https://github.com/mflux-community/mflux/blob/main/src/mflux/models/qwen21/README.md).

Draw Things publishes 11–16 GiB quantized peaks and roughly 30 GiB unquantized for
**original Qwen Image 1.0**. This supports Apple feasibility, but is not a 2512 or
2.1 benchmark. [Original Qwen Image measurements](https://releases.drawthings.ai/p/introducing-qwen-image-support).

## Proposed Atelier integration, after a local trial

The phone could send a prompt over the existing Tailscale connection; Atelier
would submit an explicit image job to a local worker on the Mac and return the
saved result. The Mac remains the compute host and needs to be available. Keep
the existing 8787 listener and Tailscale configuration. The current app has no
image-generation feature; this is a proposal requiring a named runtime and model
approval, not an implemented feature.

- Separate image-generation controls from the chat model picker; show verified
  runtime capabilities, size and job state. No automatic specialist routing.
- One image job at a time initially. Measure overlap with chat before allowing
  simultaneous heavy workloads; no automatic ejection of the user's chat model.
- A cancellable job screen, honest progress, recoverable errors and the existing
  save/share dialog for PNG outputs. Do not assume a blocking API can cancel GPU
  work just because the HTTP request is cancelled.
- Keep weights/caches ignored by Git. Record output images, seed, exact prompt,
  model revision and settings in app data, with bulk delete and storage totals.

## Concrete first trial proposal

Approve Draw Things plus `black-forest-labs/FLUX.2-klein-4B` separately, then freeze
the app/model revision, quantization, resolution and settings before evaluation.
Use six synthetic prompts at two fixed seeds: photograph, interior, illustration,
poster with exact text, a counted-object scene and a product arrangement. Start
at 1024×1024, one image per job; test reference editing with a synthetic input.

Measure cold/warm median and p90 generation time, actual peak memory, swap,
download/cache size, cancellation and resulting chat responsiveness. Manually
check requested objects, relationships, readable text and edit consistency. Keep
every image and failure; do not pick only favorable seeds. Set acceptable latency
with Jake from the measured results before adding a phone UI. No images or image
models were generated, installed or downloaded in this research checkpoint.
