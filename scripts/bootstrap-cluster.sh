#!/usr/bin/env bash
# One-time platform setup on a fresh cluster (after `terraform apply` + `aws eks update-kubeconfig`).
# Installs: metrics-server (HPA), kube-prometheus-stack (Prometheus/Grafana), Traefik (Ingress), Argo CD.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> Helm repositories"
helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/ >/dev/null
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts >/dev/null
helm repo add traefik https://traefik.github.io/charts >/dev/null
helm repo add argo https://argoproj.github.io/argo-helm >/dev/null
helm repo update >/dev/null

echo "==> Namespace, default StorageClass, quotas"
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/storageclass-gp3.yaml
kubectl apply -f k8s/resource-quota.yaml

echo "==> metrics-server (CPU metrics for the HPA)"
helm upgrade --install metrics-server metrics-server/metrics-server -n kube-system --wait

echo "==> kube-prometheus-stack (Prometheus Operator, Prometheus, Grafana)"
helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace -f monitoring/kube-prometheus-stack-values.yaml --wait --timeout 10m

echo "==> Traefik ingress controller (AWS load balancer)"
helm upgrade --install traefik traefik/traefik \
  -n traefik --create-namespace -f monitoring/traefik-values.yaml --wait

echo "==> Argo CD"
helm upgrade --install argocd argo/argo-cd -n argocd --create-namespace -f argocd/argocd-values.yaml --wait

cat <<'NEXT'

Platform ready. Next steps:
  1. Create the database secret (never committed to Git):
       kubectl create secret generic bloodbridge-db -n bloodbridge \
         --from-literal=username=bloodbridge --from-literal=password="$(openssl rand -hex 24)"
  2. Register the app with Argo CD:
       kubectl apply -f argocd/project.yaml -f argocd/application.yaml
  3. Public URL:
       kubectl get svc -n traefik traefik -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'
  4. Argo CD UI  (user: admin):
       kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d; echo
       kubectl port-forward -n argocd svc/argocd-server 8081:80
  5. Grafana UI  (admin / bloodbridge-admin):
       kubectl port-forward -n monitoring svc/kube-prometheus-stack-grafana 3001:80
NEXT
