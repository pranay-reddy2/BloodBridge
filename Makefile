# Convenience targets. Run `make help` for the list.
.DEFAULT_GOAL := help
NAMESPACE ?= bloodbridge

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

venv: ## Create backend/.venv with dev dependencies
	cd backend && python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt

test: ## Run backend tests with coverage
	cd backend && .venv/bin/pytest -v --cov=app --cov-report=term-missing

lint: ## Lint + format-check the backend
	cd backend && .venv/bin/ruff check . && .venv/bin/ruff format --check .

up: ## Build and start the full stack (http://localhost:3000)
	docker compose up --build -d && docker compose ps

seed: ## Load demo data into the running compose stack
	python3 scripts/seed-data.py http://localhost:8000

down: ## Stop the stack (keeps the database volume)
	docker compose down

clean: ## Stop the stack and delete the database volume
	docker compose down -v

helm-lint: ## Lint and render the Helm chart for every environment
	for v in values.yaml values-dev.yaml values-prod.yaml; do helm lint helm/bloodbridge -f helm/bloodbridge/$$v && helm template bb helm/bloodbridge -f helm/bloodbridge/$$v >/dev/null; done

tf-check: ## terraform fmt + validate (no AWS calls)
	cd terraform && terraform fmt -check -recursive && terraform init -backend=false -input=false >/dev/null && terraform validate

status: ## Show everything running in the app namespace
	kubectl get pods,svc,ingress,hpa,pvc -n $(NAMESPACE)

.PHONY: help venv test lint up seed down clean helm-lint tf-check status
