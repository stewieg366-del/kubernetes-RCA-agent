#!/bin/bash
set -e

echo "======================================"
echo " RCA Demo Cluster Health Check"
echo "======================================"

echo "Namespace: rca-demo"
kubectl get pods -n rca-demo -o wide

echo "---"
echo "Waiting for all pods to be ready..."
kubectl wait --for=condition=ready pod -l app=database -n rca-demo --timeout=90s || true
kubectl wait --for=condition=ready pod -l app=payment -n rca-demo --timeout=90s || true
kubectl wait --for=condition=ready pod -l app=checkout -n rca-demo --timeout=90s || true
kubectl wait --for=condition=ready pod -l app=frontend -n rca-demo --timeout=90s || true

echo "---"
echo "Current Status:"
kubectl get pods -n rca-demo
