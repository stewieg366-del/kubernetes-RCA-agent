#!/bin/bash
set -e
echo "Setting up Phase 3 Observability (Prometheus & Loki)..."
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
kubectl apply -f "$DIR/manifests/namespace.yaml"
kubectl apply -f "$DIR/manifests/"

echo "Waiting for observability pods to be ready..."
kubectl wait --for=condition=ready pod -l app=prometheus -n observability --timeout=90s
kubectl wait --for=condition=ready pod -l app=loki -n observability --timeout=90s
kubectl wait --for=condition=ready pod -l app=promtail -n observability --timeout=90s

echo "Observability setup complete!"
