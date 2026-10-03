#!/bin/bash
set -e

echo "Building Python OpenTelemetry images..."
cd observability/jaeger/tracing-app

docker build -t trace-frontend:latest ./frontend
docker build -t trace-checkout:latest ./checkout
docker build -t trace-payment:latest ./payment

echo "Loading images into Kind cluster (rca-demo-cluster)..."
kind load docker-image trace-frontend:latest --name rca-demo-cluster
kind load docker-image trace-checkout:latest --name rca-demo-cluster
kind load docker-image trace-payment:latest --name rca-demo-cluster

echo "Images successfully loaded."
