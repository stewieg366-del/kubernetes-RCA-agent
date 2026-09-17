#!/bin/bash
set -e
echo "Resetting Bad Deployment Scenario..."
kubectl set image deployment/payment payment=nginx:alpine -n rca-demo
kubectl rollout status deployment/payment -n rca-demo --timeout=60s
echo "Payment deployment restored."
