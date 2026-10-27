# QA wrapper failure, retained

After make check passed, run-final-qa.py initially used a second, incorrect
bundle calculation: gzip level 6 and the classic theme initializer as well as
module imports. It asserted 256,600 bytes against 256,000 and stopped before
starting browsers. This is not the repository measurement used for the baseline.
The existing scripts/measure_bundle.py uses the Vite entry/static-import graph
and its unchanged gzip settings; it reports 255,345 /256,000 bytes, passing.
The wrapper now calls that script directly. No product, threshold, baseline or
performance-test change. The successful make-check-final.log remains intact;
make e2e starts separately on exactly the same 526 frozen source files.
