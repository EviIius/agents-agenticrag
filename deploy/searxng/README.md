# Local free search

Docker Desktop 4.93.0 was installed on the Mac with Jake's approval on 1 October 2026.
The tested SearXNG 2026.9.30 image is pinned by digest in compose.yaml.
The service listens only on **127.0.0.1:8888**. The app still uses port 8787 and
the existing Tailscale routing. No Brave API key or paid search service is needed.

## Start

From the repo root, load the tool paths with `. scripts/tool-env.sh`.
Create `deploy/searxng/settings.yml` from the template, replace
`REPLACE_WITH_RANDOM_SECRET` with a random secret, and set permissions to 600.
The local file already exists on Jake's Mac, is ignored by Git, and must never be
committed. Then run:

```sh
docker compose -f deploy/searxng/compose.yaml up -d
curl 'http://127.0.0.1:8888/search?q=test&format=json'
```

Open Workbench Settings → Search → Test. JSON must remain enabled in
`search.formats`. Docker Desktop must be running; `restart: unless-stopped` starts
the container when the Docker engine returns, but does not start Docker Desktop
itself after a Mac reboot. Enable Docker Desktop's login startup if desired.

## Engine qualification

The template retains Google CSE, Yahoo and Wikipedia. Initial probes found Google
CSE and Yahoo working; DuckDuckGo and Qwant returned CAPTCHA, and Bing failed to
connect. Brave's scraped engine was also rate-limited and is excluded.
An unknown engine name can cause SearXNG to use its defaults, so a 200 response
alone is insufficient: check the actual `results[].engines` provenance.

After the full evaluations, Google CSE also rate-limited requests. Yahoo returned
results during a later smoke test, but also temporarily failed all six everyday
queries during the sustained evaluation session. Both can be unavailable at once.
These are free upstream engines with no availability guarantee;
keep caching, bounded requests and visible failure notices. A successful SearXNG
HTTP response may contain zero results and engine errors.

The tested Google CSE implementation supports `week` as seven days despite the
Search API documentation listing only day/month/year. This was checked against
the pinned container implementation and a real API request; do not assume it for
other engines or future versions.

Evidence: `artifacts/phase-2/searxng-qualified.json`,
`searxng-after-rate-limit.json`, and the dated real-model evaluation reports.
Never expose port 8888 to the LAN or Tailscale.
