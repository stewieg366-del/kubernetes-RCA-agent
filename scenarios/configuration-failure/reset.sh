#!/bin/bash
set -e

echo "Resetting configuration-failure scenario..."

# 1. Restore the original ConfigMap
kubectl apply -f cluster/manifests/checkout.yaml

# 2. Restart the deployment
kubectl rollout restart deployment checkout -n rca-demo

# 3. Wait for rollout
kubectl rollout status deployment checkout -n rca-demo --timeout=90s

echo "Scenario reset successfully."
