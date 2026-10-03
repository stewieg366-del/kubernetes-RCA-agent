#!/bin/bash
set -e

echo "Deploying Jaeger Distributed Tracing Showcase..."

# 1. Build and load images
./observability/jaeger/scripts/build-images.sh

# 2. Apply manifests
kubectl apply -f observability/jaeger/manifests/jaeger.yaml
kubectl apply -f observability/jaeger/manifests/tracing-app.yaml

# 3. Wait for readiness
echo "Waiting for Jaeger and tracing apps to become ready..."
kubectl rollout status deployment jaeger -n jaeger --timeout=120s
kubectl rollout status deployment trace-frontend -n jaeger --timeout=120s
kubectl rollout status deployment trace-checkout -n jaeger --timeout=120s
kubectl rollout status deployment trace-payment -n jaeger --timeout=120s

echo "Jaeger and tracing services are ready!"
echo ""
echo "=========================================================="
echo "Access Jaeger UI locally:"
echo "If using Docker Desktop / Mac, you can usually access it at:"
echo "http://localhost:31686"
echo ""
echo "If localhost doesn't work, find your Kind node IP:"
echo "kubectl get nodes -o wide"
echo "and access http://<NODE_IP>:31686"
echo "=========================================================="
