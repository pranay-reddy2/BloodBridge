# Demo assets

Put the two **mandatory** submission files here before you submit:

| File | What |
|---|---|
| `presentation.mp4` | Screen recording — slides first, then the live walkthrough below |
| `slides.pdf` (or `.pptx`) | At least 8 slides: overview, tech stack, architecture, CI/CD, infrastructure, Kubernetes, observability, key learnings |

> Videos over 100 MB cannot be pushed to GitHub normally — attach the MP4 to a **GitHub Release** instead, or use Git LFS.

## Recording script (≈12 minutes)

1. **Slides (2 min)** — the problem (blood banks lose units to expiry and waste scarce O-), the architecture diagram from the README, the pipeline.
2. **App (1.5 min)** — open the Ingress URL. Register a donor → record a donation → watch stock tile change. Create a CRITICAL AB- request: the form shows compatible groups. Fulfil it and point out it used A-/B- before O-. Footer shows the build SHA.
3. **Codebase (1 min)** — `backend/app/services/allocation.py` (FEFO + compatibility + `SKIP LOCKED`), `backend/tests/`, `helm/bloodbridge/templates/`.
4. **CI/CD (2 min)** — make a small visible change (e.g. KPI label), `git commit -m "feat(ui): ..." && git push`. Show jobs: tests → Trivy → GHCR push → GitOps bump commit. Open a Trivy log and the SBOM artifact.
5. **Terraform (1 min)** — `terraform plan` output (no changes), AWS Console: VPC with 2 public + 2 private subnets, EKS cluster + node group.
6. **Argo CD (1.5 min)** — the app turns OutOfSync → Synced with the new SHA; show the resource tree. Run `kubectl scale deploy/bloodbridge-frontend --replicas=5 -n bloodbridge` and watch self-heal put it back.
7. **Kubernetes (1 min)** — `make status`, `helm list -n bloodbridge`, `helm test bloodbridge -n bloodbridge`.
8. **HPA (1 min)** — `./scripts/load-test.sh` and watch replicas grow from 2.
9. **Prometheus + Grafana (1 min)** — Targets page shows `bloodbridge-backend` UP; the *BloodBridge — Service & Inventory* dashboard; Alerts page shows `BloodBridgeLowStock` for the scarce groups.
10. **Troubleshooting (1 min)** — apply `troubleshooting/02-service-no-endpoints.yaml`, diagnose with the RUNBOOK, fix it live.
