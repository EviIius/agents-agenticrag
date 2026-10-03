SHELL := /bin/sh
.PHONY: setup dev dev-server fake-runtime api-types build check e2e fmt record-fixtures eval-web deploy
setup:
	./scripts/setup.sh
# The installed app still owns 8787 during Phase 0. Vite previews fixture UI on 5173.
dev:
	. scripts/tool-env.sh; npm run dev --prefix web
# Start only after stopping the installed service; the production bind never changes.
dev-server:
	. scripts/tool-env.sh; WORKBENCH_DEV=1 uv run --directory server uvicorn app.main:app --host 127.0.0.1 --port 8787 --workers 1
fake-runtime:
	. scripts/tool-env.sh; uv run --directory server uvicorn tests.fake_runtime:app --host 127.0.0.1 --port 18080 --workers 1
api-types:
	. scripts/tool-env.sh; uv run --directory server python ../scripts/generate_api_types.py
build:
	. scripts/tool-env.sh; npm run build --prefix web
check:
	. scripts/tool-env.sh; uv run --directory server ruff check app tests
	. scripts/tool-env.sh; uv run --directory server ruff format --check app tests
	. scripts/tool-env.sh; uv run --directory server mypy app tests
	. scripts/tool-env.sh; uv run --directory server python ../scripts/check_coverage.py
	. scripts/tool-env.sh; uv run --directory server python ../scripts/check_contrast.py
	. scripts/tool-env.sh; uv run --directory server python ../scripts/generate_api_types.py --check
	. scripts/tool-env.sh; npm run check --prefix web
e2e:
	. scripts/tool-env.sh; npm run e2e --prefix web
fmt:
	. scripts/tool-env.sh; uv run --directory server ruff check app tests --fix; uv run --directory server ruff format app tests
	. scripts/tool-env.sh; npm run fmt --prefix web
record-fixtures:
	. scripts/tool-env.sh; uv run --directory server python ../scripts/record_provider_fixtures.py
eval-web:
	. scripts/tool-env.sh; uv run --directory server python evals/web/run_eval.py $(if $(CASE),--case $(CASE),) $(if $(MODEL),--model $(MODEL),) $(if $(LIVE),--live,) $(if $(RANKING),--ranking $(RANKING),)
eval-web-record:
	. scripts/tool-env.sh; uv run --directory server python evals/web/run_eval.py --record $(if $(CASE),--case $(CASE),) $(if $(MODEL),--model $(MODEL),)
deploy:
	./scripts/deploy.sh --apply $(DEPLOY_ARGS)
