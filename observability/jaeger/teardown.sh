#!/bin/bash
set -e

echo "Tearing down Jaeger Distributed Tracing Showcase..."

# Remove ONLY the Jaeger resources
kubectl delete -f observability/jaeger/manifests/tracing-app.yaml --ignore-not-found=true
kubectl delete -f observability/jaeger/manifests/jaeger.yaml --ignore-not-found=true

echo "Teardown complete. RCA system remains untouched."
