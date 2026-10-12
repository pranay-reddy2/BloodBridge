# BloodBridge troubleshooting runbook

Every scenario lives in the `bloodbridge` namespace and is labelled `lab=troubleshooting`, so cleanup is one command:

```bash
kubectl delete deploy,svc -n bloodbridge -l lab=troubleshooting
```

The general loop for any incident:

```text
kubectl get pods -n bloodbridge            # what state is it in?
kubectl describe pod <pod> -n bloodbridge  # Events at the bottom say *why*
kubectl logs <pod> -n bloodbridge [--previous]
kubectl get events -n bloodbridge --sort-by=.lastTimestamp
```

---

## 1. ImagePullBackOff — tag does not exist

```bash
kubectl apply -f troubleshooting/01-image-pull-backoff.yaml
kubectl get pods -n bloodbridge -l app=lab-bad-image        # ErrImagePull -> ImagePullBackOff
kubectl describe pod -n bloodbridge -l app=lab-bad-image | tail -8
```

**Evidence:** `Failed to pull image "...:this-tag-does-not-exist": not found`.
**Cause:** the tag was never pushed (or the registry is private and `imagePullSecrets` is missing — then the message says `unauthorized` / `403`).
**Fix:** use a tag that exists. In this project CI only writes a SHA into `values-prod.yaml` *after* the image was pushed, which is why this cannot happen through the pipeline.

```bash
kubectl set image deploy/lab-bad-image web=nginxinc/nginx-unprivileged:stable-alpine -n bloodbridge
```

## 2. Service with no endpoints — label typo

```bash
kubectl apply -f troubleshooting/02-service-no-endpoints.yaml
kubectl get endpointslices -n bloodbridge -l kubernetes.io/service-name=lab-echo   # ENDPOINTS: <unset>
kubectl get svc lab-echo -n bloodbridge -o jsonpath='{.spec.selector}'; echo
kubectl get pods -n bloodbridge --show-labels -l lab=troubleshooting
```

**Evidence:** selector is `app=lab-ecoh`, the pod is labelled `app=lab-echo`.
**Fix:**

```bash
kubectl patch svc lab-echo -n bloodbridge -p '{"spec":{"selector":{"app":"lab-echo"}}}'
kubectl run curl -n bloodbridge --rm -it --restart=Never --image=busybox:1.37 -- wget -qO- http://lab-echo | head -3
```

## 3. Running but never Ready — wrong probe port

```bash
kubectl apply -f troubleshooting/03-readiness-never-ready.yaml
kubectl get pods -n bloodbridge -l app=lab-not-ready      # READY 0/1, RESTARTS 0
kubectl describe pod -n bloodbridge -l app=lab-not-ready | grep -A2 Readiness
```

**Evidence:** `Readiness probe failed: ... connect: connection refused` on port 80.
**Why no restarts?** A failing *readiness* probe only removes the pod from Service endpoints; only a failing *liveness* probe restarts it. BloodBridge uses this split deliberately: `/ready` checks PostgreSQL, `/health` does not, so a database blip never causes a restart storm.
**Fix:** `kubectl patch deploy lab-not-ready -n bloodbridge --type=json -p '[{"op":"replace","path":"/spec/template/spec/containers/0/readinessProbe/httpGet/port","value":8080}]'`

## 4. OOMKilled — limit too low

```bash
kubectl apply -f troubleshooting/04-oomkilled.yaml
kubectl get pods -n bloodbridge -l app=lab-oom -w                 # OOMKilled -> CrashLoopBackOff
kubectl describe pod -n bloodbridge -l app=lab-oom | grep -A4 "Last State"
```

**Evidence:** `Reason: OOMKilled`, `Exit Code: 137` (128 + SIGKILL).
**Fix:** raise `limits.memory` above the real working set (use the Grafana "Memory per pod" panel to size it), e.g. `kubectl set resources deploy/lab-oom -n bloodbridge --limits=memory=320Mi`.

## 5. The real app: database credentials wrong

```bash
./troubleshooting/05-db-wrong-password.sh
kubectl get pods -n bloodbridge -l app.kubernetes.io/component=backend          # one new pod in CrashLoopBackOff
kubectl logs -n bloodbridge -l app.kubernetes.io/component=backend --prefix --tail=5   # password authentication failed
kubectl rollout status deploy/bloodbridge-backend -n bloodbridge                 # hangs: rollout cannot progress
```

**What you will see:**
- The new pod runs `alembic upgrade head` on start, cannot authenticate, exits, and goes into CrashLoopBackOff.
- Because the Deployment uses `maxUnavailable: 0`, the **old pods keep serving traffic**, so users are not affected. That is the point of start-up/readiness probes combined with a safe rollout strategy.
- In Grafana, *Backend targets UP* stays green (old pods are fine) and *Container restarts* climbs for the new pod.
- If Argo CD self-heal is enabled it reverts the manual change within about a minute — drift correction in action.

**Fix:** `./troubleshooting/05-db-wrong-password.sh --restore`

---

## Other quick checks

| Symptom | Command | Usual cause |
|---|---|---|
| PVC `Pending` | `kubectl describe pvc -n bloodbridge` | No default StorageClass / EBS CSI add-on missing → `kubectl apply -f k8s/storageclass-gp3.yaml` |
| HPA shows `<unknown>/60%` | `kubectl top pods -n bloodbridge` | metrics-server not installed, or no CPU `requests` on the container |
| Ingress has no ADDRESS | `kubectl get svc -n traefik` | Load balancer still provisioning (2-3 min) or public subnets missing the `kubernetes.io/role/elb` tag |
| Prometheus target missing | Prometheus → Status → Targets | ServiceMonitor label/port name mismatch; Service port must be named `http` |
| Argo CD `OutOfSync` / `Degraded` | `argocd app get bloodbridge` or the UI | Image tag not pushed yet, or a manual change being self-healed |
