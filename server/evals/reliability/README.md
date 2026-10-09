# Isolated reliability evidence

These scripts exercise already-installed models. They never deploy or change
production data, preferences, sampling or runtime versions. Read
`docs/RELIABILITY-PLAN.md` before running anything.

- `run.py --version vN --repeat 1 --profile baseline|candidate|both` runs the
  original everyday/Web/Library suites with frozen alternative modules. Existing
  output names are exclusive: a failed trial is retained, not overwritten.
- `planner_probe.py --model ID --version original|vN --repeat 1|2|3` runs the 18
  supplementary planner decisions. Decision correctness is not query usefulness.
- `regrade_library.py` writes a separate citation-binding regrade. Its current
  v3 output already exists; do not rerun or overwrite it. Original reports remain
  the comparison baseline. It checks required-fact placement, not arbitrary truth.
- `extractive/run_probe.py --model ID` runs eight predeclared retained inputs in
  the separate exact-excerpt contract. It uses one answer call per input and no
  retries. Relevance and coverage still need manual review.
- `extractive/ids_probe.py --model ID` runs the separately frozen v3 host-ID
  contract on the same eight inputs. Both profiles have completed it; existing
  output names are exclusive. Its manual review fails relevance/context/coverage
  despite 8/8 valid-ID responses. Do not treat provenance as answer correctness.
- `table_probe.py` retains an offline table-selection comparison on saved bytes.
  Its output already exists; it is coverage evidence, not a full pipeline pass.

The alternative modules under `trials/` are failed/diagnostic prototypes, not
production packages. Their bytes are frozen in `artifacts/reliability/vN/manifest.json`.
Do not format or edit a frozen version after inference. Create a new version with
its documented generic change instead. Production still imports `server/app`.

Report provenance: root `source_hashes` identify the stable application tree;
effective prompt/builder/pipeline/context hashes and each trial's manifest identify
the alternatives actually imported. Raw request payloads and response deltas are
retained. Do not mistake a root hash for the effective alternative module hash.
v1 ran before the import isolation was added. Its source is archived under
`artifacts/reliability/v1/server/app`; the modern loader refuses v1 instead of
accidentally replaying it with the restored production modules.

Web corpus replay runs a real planner and answer against the same saved search
results/pages, regardless of the planner's query wording. It tests intent,
selection and generation, not live query quality. A changed query cannot recover
a fact absent from that frozen corpus. Keep that distinction in reports.

Model comparison labels and corpus inputs are public or authored synthetic data.
Never substitute real user attachments or include private credentials in evidence.
