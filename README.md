# 🩸 BloodBridge — DevSecOps Capstone

**BloodBridge** is a blood-bank operations platform. It keeps a registry of donors, tracks every blood unit from collection to expiry, and fulfils hospital requests with **ABO/Rh compatibility-aware, first-expiry-first-out** allocation. That stops scarce O-negative stock from being wasted and keeps short-lived platelets from expiring on the shelf.

The application is the payload. The project itself is the **path from a laptop to a monitored, autoscaling, GitOps-managed Kubernetes cluster on AWS**:

```text
 Developer ──git push──▶ GitHub ──▶ GitHub Actions
                                     ├─ ruff lint + pytest (40 tests, ≥85% coverage gate)
                                     ├─ Alembic migrations on a real PostgreSQL service container
                                     ├─ React build · terraform validate · helm lint
                                     ├─ Trivy: secrets + dependency CVEs + IaC misconfig
                                     ├─ docker build ─▶ Trivy image scan (blocks HIGH/CRITICAL) ─▶ SBOM
                                     ├─ push to GHCR  (tag = commit SHA)
                                     └─ commit new tag to helm/bloodbridge/values-prod.yaml
                                                        │
          Terraform ──▶ AWS VPC (2 AZ, public+private) ─┤
                        EKS 1.34 + managed node group   │
                                                        ▼
                                                  Argo CD (GitOps) ──sync──▶ Helm chart
                                                                              │
         Internet ──▶ AWS LB ──▶ Traefik Ingress ──┬── /      ─▶ React + Nginx (2 pods)
                                                   └── /api   ─▶ FastAPI (HPA 2→6 pods) ─▶ PostgreSQL StatefulSet (EBS gp3)
                                                                     │ /metrics
                                         Prometheus (ServiceMonitor + alert rules) ─▶ Grafana dashboard
```

---

## Contents

1. [What the application does](#1-what-the-application-does)
2. [Tech stack](#2-tech-stack)
3. [Repository layout](#3-repository-layout)
4. [Run it locally](#4-run-it-locally)
5. [Testing](#5-testing)
6. [Containers](#6-containers)
7. [CI/CD pipeline](#7-cicd-pipeline)
8. [DevSecOps controls](#8-devsecops-controls)
9. [Terraform: AWS infrastructure](#9-terraform-aws-infrastructure)
10. [Kubernetes, Helm and Argo CD](#10-kubernetes-helm-and-argo-cd)
11. [Ingress and autoscaling](#11-ingress-and-autoscaling)
12. [Observability](#12-observability)
13. [Troubleshooting lab](#13-troubleshooting-lab)
14. [Tear down](#14-tear-down)
15. [Design decisions, known issues and limitations](#15-design-decisions-known-issues-and-limitations)

---

## 1. What the application does

| Area | Behaviour |
|---|---|
| **Donor registry** | Register donors with blood group and contact details. Each donor has a computed **eligibility** (90-day gap between whole-blood donations). Search and filter by group, city and eligibility. |
| **Donations → units** | Recording a donation creates a **blood unit** with a component-specific shelf life: whole blood 35 d, red cells 42 d, platelets 5 d, plasma 365 d. Donating again too early is rejected with `409`. |
| **Inventory** | Units move through `AVAILABLE → QUARANTINED → ISSUED / EXPIRED / DISCARDED`. A daily Kubernetes **CronJob** expires stale stock. The dashboard shows stock per group against a low-stock threshold. |
| **Hospital requests** | Requests carry urgency (`ROUTINE / URGENT / CRITICAL`). The queue is ordered by urgency, then age. **Fulfil** allocates compatible units: identical group first and universal donors last, then first-expiry-first-out. It supports **partial** fulfilment when stock is short. Plasma and platelets use the reversed ABO rules. Allocation uses `SELECT … FOR UPDATE SKIP LOCKED`, so two backend replicas can never issue the same bag. |
| **Ops endpoints** | `/health` (liveness, no DB), `/ready` (readiness, checks DB), `/metrics` (Prometheus), `/api/meta` (build SHA shown in the UI footer). |

### REST API (Swagger at `/docs`)

| Method | Path | Purpose |
|---|---|---|
| GET | `/health`, `/ready`, `/metrics`, `/api/meta` | Operations |
| GET / POST | `/api/donors` | List (filters `q`, `blood_group`, `city`, `eligible`) / register |
| GET / PUT / DELETE | `/api/donors/{id}` | Read / update / delete (blocked if the donor has units) |
| POST | `/api/donors/{id}/donations` | Record a donation → creates a blood unit |
| GET | `/api/units` | List units (filters `status`, `blood_group`, `component`, `expiring_within_days`) |
| GET / PUT | `/api/units/{id}` | Read / quarantine / release / discard |
| POST | `/api/units/expire-sweep` | Mark expired stock (called by the CronJob) |
| GET / POST | `/api/requests` | Urgency-ordered queue / create request |
| GET / PUT / DELETE | `/api/requests/{id}` | Read / update or cancel / delete |
| POST | `/api/requests/{id}/fulfil` | Allocate compatible units |
| GET | `/api/inventory/summary` | Dashboard KPIs and stock per group |
| GET | `/api/compatibility?blood_group=AB-&component=RED_CELLS` | Compatible donor groups + usable units |

### Data model (Alembic migration `0001_initial_schema`)

```text
donors (id, full_name, blood_group, email UNIQUE, phone, city, last_donation_date, created_at)
   1 ──< blood_units (id, donor_id FK, blood_group, component, volume_ml, collected_on, expires_on, status, request_id FK)
blood_requests (id, hospital, patient_ref, blood_group, component, units_needed, urgency, status, notes, created_at, fulfilled_at)
   1 ──< blood_units
```

Check constraints protect blood-group values, positive quantities and expiry after collection. The schema has indexes on status, expiry and blood group.

---

## 2. Tech stack

| Layer | Tools |
|---|---|
| Frontend | React 19, Vite 8, hand-written responsive CSS (light and dark), served by **nginx-unprivileged** |
| Backend | Python 3.13, FastAPI, SQLAlchemy 2, Alembic, Pydantic v2, prometheus-fastapi-instrumentator + custom collectors |
| Database | PostgreSQL 17 |
| Quality | pytest + pytest-cov, ruff (lint + format), `alembic check` for model/migration drift |
| Containers | Multi-stage Dockerfiles, non-root users, Docker Compose |
| CI/CD | GitHub Actions, GitHub Container Registry (GHCR), Dependabot |
| Security | Trivy (image CVEs, dependency CVEs, secrets, IaC misconfig), CycloneDX SBOM, Pod Security Admission, NetworkPolicy |
| Infrastructure | Terraform: `terraform-aws-modules` VPC 5.x, EKS 20.x, IAM (IRSA for the EBS CSI driver) |
| Platform | Amazon EKS, EBS gp3, Traefik Ingress, metrics-server, Helm 3, Argo CD |
| Observability | kube-prometheus-stack: Prometheus Operator, Prometheus, Alertmanager, Grafana |

---

## 3. Repository layout

```text
bloodbridge/
├── backend/                     FastAPI service
│   ├── app/
│   │   ├── main.py              app wiring, health/ready/meta, metrics
│   │   ├── routers/             donors, units, requests, inventory
│   │   ├── services/            compatibility rules, allocation (FEFO + SKIP LOCKED)
│   │   ├── metrics.py           domain counters + DB-backed inventory gauges
│   │   └── models.py, schemas.py, db.py, config.py
│   ├── alembic/versions/        database migrations
│   ├── tests/                   40 pytest tests (SQLite in-memory test DB)
│   ├── Dockerfile, docker-entrypoint.sh, requirements*.txt, pytest.ini, ruff.toml
├── frontend/                    React SPA + nginx.conf.template + Dockerfile
├── docker-compose.yml           full local stack
├── .github/workflows/ci-cd.yml  pipeline        .github/dependabot.yml
├── terraform/                   VPC + EKS + IRSA (terraform.tfvars.example)
├── k8s/                         namespace (Pod Security), gp3 StorageClass, quota/limits
├── helm/bloodbridge/            chart: deployments, statefulset, ingress, HPA, PDB, ServiceMonitor,
│                                PrometheusRule, Grafana dashboard, CronJob, NetworkPolicy, helm test
├── argocd/                      Argo CD install values, AppProject, Application
├── monitoring/                  kube-prometheus-stack + Traefik values
├── scripts/                     bootstrap-cluster.sh, seed-data.py, load-test.sh, install-trivy.sh
├── troubleshooting/             5 broken scenarios + RUNBOOK.md
├── demo/                        presentation video + slides (submission)
└── Makefile
```

---

## 4. Run it locally

### Option A — Docker Compose (whole stack, one command)

```bash
docker compose up --build        # or: make up
python3 scripts/seed-data.py     # optional: 40 donors, 32 units, 6 hospital requests
```

| URL | What |
|---|---|
| http://localhost:3000 | BloodBridge UI (Nginx proxies `/api` to the backend) |
| http://localhost:8000/docs | Swagger UI |
| http://localhost:8000/metrics | Prometheus metrics |

Compose waits for PostgreSQL to be healthy before it starts the API (which runs migrations on start), and for the API to be healthy before it starts Nginx. Use `docker compose down -v` to also delete the database volume.

### Option B — run the processes directly

```bash
docker run -d --name bb-pg -e POSTGRES_USER=bloodbridge -e POSTGRES_PASSWORD=bloodbridge -e POSTGRES_DB=bloodbridge -p 5432:5432 postgres:17-alpine

cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# second terminal
cd frontend && npm ci && npm run dev     # http://localhost:5173 (Vite proxies /api → :8000)
```

---

## 5. Testing

```bash
cd backend
pytest -v --cov=app          # 40 passed, ~96% coverage
ruff check . && ruff format --check .
```

* `tests/conftest.py` sets `DATABASE_URL=sqlite:///:memory:` **before** the app is imported. Every test gets freshly created tables, so the suite never touches a real database.
* Coverage spans **every endpoint group**: donors, donations and units, requests and fulfilment, inventory, ops and metrics. It includes the business rules: eligibility window, shelf life, FEFO ordering, O- conservation, plasma reverse-ABO, partial fulfilment, expired-unit exclusion and terminal states.
* CI also runs `alembic upgrade → check → downgrade → upgrade` against a **real PostgreSQL 17** service container. This proves the migration matches the models and is reversible.

---

## 6. Containers

| Image | Base | Hardening |
|---|---|---|
| `bloodbridge-backend` | `python:3.13-slim`, multi-stage (deps built into a venv, copied into a clean runtime) | UID 10001, OS packages upgraded at build, `HEALTHCHECK`, `exec` entrypoint so PID 1 gets SIGTERM, works with read-only root FS |
| `bloodbridge-frontend` | `node:22-alpine` build → `nginxinc/nginx-unprivileged:stable-alpine` runtime | UID 101, port 8080, security headers + CSP, immutable asset caching, `/healthz` probe |

Both images receive `APP_VERSION=<git sha>` at build time. It shows up as an OCI label, in `/api/meta` and in the UI footer, so anyone can trace a running pod back to its commit.

---

## 7. CI/CD pipeline

[`.github/workflows/ci-cd.yml`](.github/workflows/ci-cd.yml) runs on every push and pull request to `main`:

| Stage | Job | Fails the build when… |
|---|---|---|
| Test | **backend** — ruff, pytest (coverage ≥ 85%), migrations on PostgreSQL | lint error, failing test, coverage drop, model/migration drift |
| Test | **frontend** — `npm ci && npm run build` | build error |
| Test | **infra-lint** — `terraform fmt/validate`, `helm lint` + `helm template` for all three values files | invalid HCL or chart |
| Test | **source-scan** — Trivy `fs` (secrets + dependency CVEs) and `config` (IaC) | a secret, or a fixable HIGH/CRITICAL CVE |
| Build | **images** (matrix: backend, frontend) — Buildx build with GHA cache → **Trivy image scan** → JSON report + CycloneDX SBOM artifacts → push to `ghcr.io/<owner>/bloodbridge-<service>:<sha>` | fixable HIGH/CRITICAL CVE in the image |
| Deploy | **gitops** (main only) — `yq` writes the new SHA into `helm/bloodbridge/values-prod.yaml` and commits `deploy: bloodbridge <sha> [skip ci]` | — |

Images are only pushed after every gate passes. They are tagged **only with the commit SHA**, never `latest`, so `commit → image → pod` is always traceable. The pipeline never holds cluster credentials: Argo CD pulls the change from Git (see §10).

**One-time GitHub setup**

1. Repository: <https://github.com/pranay-reddy2/BloodBridge>.
2. *Settings → Actions → General → Workflow permissions* → **Read and write** (lets the gitops job commit).
3. After the first green run, open each package under *Your profile → Packages* → *Package settings* → **Change visibility → Public**. Alternatively, keep them private and create an `imagePullSecret`; see §15.

---

## 8. DevSecOps controls

| Layer | Control |
|---|---|
| Code | ruff security rules (`S` = bandit), parameterised SQL through SQLAlchemy, Pydantic validation of every input |
| Dependencies | Trivy dependency scan of `requirements.txt` and `package-lock.json`; Dependabot weekly PRs for pip, npm, Docker, Actions and Terraform |
| Secrets | Trivy secret scan; `.gitignore` blocks `.env`, `*.tfvars`, `*.pem`, kubeconfigs; production DB password lives in a Secret created out-of-band (`existingSecret`), never in Git |
| Images | Trivy blocks fixable HIGH/CRITICAL CVEs; accepted risks must be listed with a reason in `.trivyignore`; an SBOM is published per build |
| IaC | `trivy config` reports Terraform, Helm and Dockerfile misconfigurations on every run |
| Runtime | Non-root UIDs, `readOnlyRootFilesystem`, all capabilities dropped, `seccompProfile: RuntimeDefault`, no privilege escalation; namespace enforces Pod Security **baseline** and warns on **restricted** |
| Network | NetworkPolicy: only backend pods may reach PostgreSQL (enforced by the VPC CNI network-policy agent enabled in Terraform) |
| Cloud | IRSA: the EBS CSI driver gets an IAM role scoped to its service account; EKS access entries instead of `aws-auth`; API endpoint CIDR allow-list variable; control-plane audit logs |

**Reading a Trivy result** (for the M6 write-up): the image scan lists OS packages (Debian/Alpine) and language packages (pip wheels, Nginx modules) with CVE ID, severity, installed and fixed version. `--ignore-unfixed` hides CVEs that have no patched version yet, because there is nothing to act on. A clean run means *no known, fixable HIGH or CRITICAL vulnerability at build time*. It does not mean "secure forever", which is why Dependabot and rebuilds keep running.

---

## 9. Terraform: AWS infrastructure

```text
AWS ap-south-1
└── VPC 10.42.0.0/16 (2 AZs)
    ├── public  10.42.0.0/24, 10.42.1.0/24    tag kubernetes.io/role/elb      ← AWS load balancer for Traefik
    ├── private 10.42.16.0/20, 10.42.32.0/20  tag kubernetes.io/role/internal-elb
    ├── Internet gateway + 1 NAT gateway
    └── EKS "bloodbridge-dev" (Kubernetes 1.34, API auth mode, audit logs → CloudWatch 7 d)
        ├── add-ons: vpc-cni (NetworkPolicy on), coredns, kube-proxy, pod-identity-agent, aws-ebs-csi-driver (IRSA)
        └── managed node group: 2–4 × t3.medium, Amazon Linux 2023, private subnets
```

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars      # edit owner, optionally node_capacity_type = "SPOT"
aws sts get-caller-identity                        # confirm you are in the right AWS account
terraform init
terraform plan -out tfplan
terraform apply tfplan                             # ~15 minutes
$(terraform output -raw configure_kubectl)         # aws eks update-kubeconfig ...
kubectl get nodes
```

> **Cost:** EKS control plane ≈ $0.10/h, 2 × t3.medium ≈ $0.09/h, NAT gateway ≈ $0.06/h + data, plus one load balancer. That comes to roughly **$6–8 per day**. Run `terraform destroy` as soon as you have recorded the demo (§14).
>
> Before you apply, check that `kubernetes_version` is still in *standard* support. Extended support costs about 6× more:
> `aws eks describe-cluster-versions --query 'clusterVersions[?versionStatus==\`STANDARD_SUPPORT\`].clusterVersion'`

---

## 10. Kubernetes, Helm and Argo CD

### 10.1 Platform bootstrap (once per cluster)

```bash
./scripts/bootstrap-cluster.sh
```

The script applies `k8s/` (namespace with Pod Security labels, default `gp3` StorageClass, ResourceQuota and LimitRange). It then installs **metrics-server**, **kube-prometheus-stack**, **Traefik** and **Argo CD** with Helm.

### 10.2 Database secret (kept out of Git)

```bash
kubectl create secret generic bloodbridge-db -n bloodbridge \
  --from-literal=username=bloodbridge \
  --from-literal=password="$(openssl rand -hex 24)"
```

### 10.3 Deploy with Argo CD (GitOps — the production path)

```bash
kubectl apply -f argocd/project.yaml -f argocd/application.yaml

kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d; echo
kubectl port-forward -n argocd svc/argocd-server 8081:80          # http://localhost:8081  (admin / above)
```

From then on, every push to `main`:
CI builds and pushes `:<sha>` → commits the tag to `values-prod.yaml` → Argo CD notices within ~60 s → rolling update. `selfHeal` reverts manual `kubectl` drift, and `prune` removes resources deleted from Git. To roll back, `git revert` the deploy commit.

### 10.4 Deploy with Helm directly (local clusters or manual testing)

```bash
helm upgrade --install bloodbridge ./helm/bloodbridge -n bloodbridge \
  -f helm/bloodbridge/values-prod.yaml --set backend.image.tag=<sha> --set frontend.image.tag=<sha>

helm list -n bloodbridge
helm test bloodbridge -n bloodbridge        # in-cluster smoke test: /ready, /api/inventory/summary, UI
helm rollback bloodbridge 1 -n bloodbridge  # if needed
```

For kind, minikube or Docker Desktop, use `-f helm/bloodbridge/values-dev.yaml`. It runs 1 replica with no HPA and the chart-managed dev secret, at host `bloodbridge.local`.

### 10.5 What the chart creates

| Resource | Notes |
|---|---|
| `Deployment` backend | Startup probe `/health` (covers migrations), readiness `/ready`, liveness `/health`; `maxUnavailable: 0` rolling updates; pod anti-affinity; replicas omitted when the HPA owns them |
| `Deployment` frontend | 2 replicas, Nginx renders `BACKEND_UPSTREAM` from a template at start |
| `StatefulSet` postgres | `volumeClaimTemplates` on gp3 EBS, runs as UID 70, `pg_isready` probes |
| `Service` ×3 | ClusterIP; ports named `http` / `postgres` |
| `Ingress` | `/api` → backend, `/` → frontend, class `traefik`, optional host + TLS |
| `HorizontalPodAutoscaler` | backend 2→6 at 60% CPU; fast scale-up, 120 s scale-down window |
| `PodDisruptionBudget` | `minAvailable: 1` for backend and frontend, so node drains never take the app down |
| `ConfigMap` / `Secret` | app settings / DB credentials (or `existingSecret`); a config checksum annotation rolls pods on change |
| `CronJob` | daily `POST /api/units/expire-sweep` |
| `NetworkPolicy` | PostgreSQL ingress only from backend pods |
| `ServiceMonitor`, `PrometheusRule`, dashboard `ConfigMap` | see §12 |
| `helm test` Pod | smoke test |

**Migrations with several replicas:** each backend pod runs `alembic upgrade head` before it starts serving. `alembic/env.py` takes a PostgreSQL **advisory lock**, so when 2+ pods start together only one migrates and the rest wait, then find nothing to do.

---

## 11. Ingress and autoscaling

```bash
kubectl get svc -n traefik traefik -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'; echo
# open http://<that-hostname>/        (the UI footer shows the deployed commit SHA)
kubectl get ingress -n bloodbridge
```

An Ingress object is only configuration. The **Traefik** controller is what reads it, and it sits behind an AWS load balancer in the public subnets.

**HPA demo**

```bash
kubectl get hpa -n bloodbridge                 # TARGETS e.g. 3%/60%, REPLICAS 2
./scripts/load-test.sh                         # in-cluster Job, 4 workers × 180 s
kubectl get hpa,pods -n bloodbridge -w         # replicas climb towards 6, then scale in ~2 min after load stops
```

---

## 12. Observability

**Metrics exposed by the backend** (`/metrics`):

| Metric | Type | Meaning |
|---|---|---|
| `http_requests_total{handler,method,status}` | counter | request rate and errors |
| `http_request_duration_seconds_bucket{handler,method}` | histogram | latency percentiles |
| `bloodbridge_donations_total{blood_group,component}` | counter | units collected |
| `bloodbridge_units_issued_total{blood_group,component}` | counter | units issued to hospitals |
| `bloodbridge_fulfilment_shortfall_units_total{blood_group,urgency}` | counter | demand that could not be met |
| `bloodbridge_requests_created_total{urgency}` | counter | incoming demand |
| `bloodbridge_inventory_available_units{blood_group}` | gauge | usable stock, read from PostgreSQL at scrape time |
| `bloodbridge_requests_open{urgency}` | gauge | queue depth |

**Wiring:** the chart's `ServiceMonitor` tells the Prometheus Operator to scrape `bloodbridge-backend:http/metrics` every 15 s. The `PrometheusRule` adds five alerts: backend down, 5xx rate above 5%, p95 above 1 s, **low stock per blood group**, and a CRITICAL request open for more than 15 min. The dashboard `ConfigMap` (label `grafana_dashboard: "1"`) is auto-loaded by the Grafana sidecar.

```bash
kubectl port-forward -n monitoring svc/kube-prometheus-stack-prometheus 9090:9090   # Status → Targets: bloodbridge-backend UP
kubectl port-forward -n monitoring svc/kube-prometheus-stack-grafana 3001:80        # admin / bloodbridge-admin
```

**Grafana dashboard "BloodBridge — Service & Inventory"** has three rows:
*Blood stock* (units per group with thresholds, open requests by urgency, donations vs issues vs shortfall) ·
*API golden signals* (RPS per endpoint, p50/p95/p99 latency, 5xx %, status classes, targets up) ·
*Kubernetes & autoscaling* (HPA current/desired/max replicas, CPU and memory per pod, restarts).

---

## 13. Troubleshooting lab

[`troubleshooting/RUNBOOK.md`](troubleshooting/RUNBOOK.md) walks through five failures, each with its symptoms, the commands that reveal the cause, and the fix:

1. `ImagePullBackOff`: the tag does not exist
2. Service with no endpoints: selector typo
3. Running but never Ready: wrong probe port (and why readiness ≠ liveness)
4. `OOMKilled`: memory limit too low (exit code 137)
5. The real backend gets a wrong DB password. The new pod crash-loops while `maxUnavailable: 0` keeps the old pods serving users, and Argo CD self-heal reverts the change.

Clean-up: `kubectl delete deploy,svc -n bloodbridge -l lab=troubleshooting`

---

## 14. Tear down

```bash
kubectl delete -f argocd/application.yaml        # Argo CD prunes the app (finalizer)
helm uninstall traefik -n traefik                # releases the AWS load balancer BEFORE destroying the VPC
kubectl delete pvc --all -n bloodbridge          # releases the EBS volume
cd terraform && terraform destroy
```

Delete the load balancer and PVCs first. Otherwise AWS resources that Kubernetes created outside Terraform can block deletion of the VPC.

---

## 15. Design decisions, known issues and limitations

* **In-cluster PostgreSQL** keeps the capstone self-contained. For production, use **Amazon RDS** (Multi-AZ, automated backups, PITR): set `postgres.enabled=false` and `postgres.host=<rds-endpoint>`.
* **Traefik instead of ingress-nginx:** the Kubernetes project retired ingress-nginx in March 2026. The chart uses the standard `networking.k8s.io/v1` Ingress API, so any controller works. Change `ingress.className` to switch.
* **Single NAT gateway** saves cost but is a single-AZ dependency. Use one per AZ in production.
* **Private GHCR packages** need a pull secret: `kubectl create secret docker-registry ghcr-pull -n bloodbridge --docker-server=ghcr.io --docker-username=<user> --docker-password=<PAT with read:packages>`, then set `imagePullSecrets: [{name: ghcr-pull}]`.
* **No authentication** on the UI or API. It is out of scope for the DevOps capstone. The next step would be OIDC (Amazon Cognito) in front of the Ingress, with role-based actions.
* **TLS** is not configured by default. Add cert-manager + Let's Encrypt and set `ingress.tls.enabled=true` with a real host.
* **DB password characters:** the backend builds `DATABASE_URL` from the Secret. Use URL-safe passwords (the `openssl rand -hex` command above is).
* **Clinical rules are simplified:** platelets follow plasma ABO rules, Rh for plasma is ignored, and cross-matching is assumed to happen downstream. Do not use for real transfusion decisions.
* **Trivy findings change daily:** a build that was green last week can fail today when a new CVE is published. That is intended. Rebuild to pick up patched base images, or document an accepted risk in `.trivyignore`.
