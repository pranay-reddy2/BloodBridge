#!/usr/bin/env bash
# Generates CPU load on the backend so the HPA scales out. It runs as a Kubernetes Job *inside*
# the cluster, so it behaves the same on EKS, kind or minikube and needs nothing installed locally.
#
#   ./scripts/load-test.sh                      # 4 workers for 180 s
#   WORKERS=8 DURATION=300 ./scripts/load-test.sh
#
# Watch in another terminal:   kubectl get hpa,pods -n bloodbridge -w
set -euo pipefail
NAMESPACE="${NAMESPACE:-bloodbridge}"
TARGET="${TARGET:-http://bloodbridge-backend:8000}"
WORKERS="${WORKERS:-4}"
DURATION="${DURATION:-180}"

kubectl delete job bloodbridge-load -n "$NAMESPACE" --ignore-not-found >/dev/null

kubectl apply -n "$NAMESPACE" -f - <<YAML
apiVersion: batch/v1
kind: Job
metadata:
  name: bloodbridge-load
spec:
  parallelism: ${WORKERS}
  completions: ${WORKERS}
  backoffLimit: 0
  activeDeadlineSeconds: $((DURATION + 60))
  ttlSecondsAfterFinished: 120
  template:
    spec:
      restartPolicy: Never
      securityContext: {runAsNonRoot: true, runAsUser: 65534, seccompProfile: {type: RuntimeDefault}}
      containers:
        - name: load
          image: busybox:1.37
          securityContext: {allowPrivilegeEscalation: false, capabilities: {drop: ["ALL"]}}
          resources: {requests: {cpu: 20m, memory: 16Mi}, limits: {cpu: 250m, memory: 32Mi}}
          command:
            - sh
            - -c
            - |
              end=\$(( \$(date +%s) + ${DURATION} ))
              while [ \$(date +%s) -lt \$end ]; do
                wget -qO- ${TARGET}/api/inventory/summary >/dev/null
                wget -qO- "${TARGET}/api/donors?limit=200" >/dev/null
                wget -qO- "${TARGET}/api/compatibility?blood_group=AB%2B&component=RED_CELLS" >/dev/null
              done
YAML

echo "Load test running: ${WORKERS} workers x ${DURATION}s against ${TARGET}"
echo "Stop early with: kubectl delete job bloodbridge-load -n ${NAMESPACE}"
kubectl get hpa -n "$NAMESPACE" -w &
WATCH_PID=$!
trap 'kill $WATCH_PID 2>/dev/null || true' EXIT
sleep "$((DURATION + 30))"
