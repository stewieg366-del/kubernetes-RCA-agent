#!/bin/bash
set -e

CLUSTER_NAME="rca-demo-cluster"

echo "======================================"
echo " Starting K8s RCA Agent Environment"
echo "======================================"

# Check dependencies
for cmd in docker kind kubectl; do
  if ! command -v $cmd &> /dev/null; then
    echo "Error: $cmd is not installed."
    exit 1
  fi
done

echo "[1/4] Creating Kind cluster..."
if kind get clusters | grep -q "^${CLUSTER_NAME}$"; then
  echo "Cluster ${CLUSTER_NAME} already exists. Skipping creation."
else
  kind create cluster --name ${CLUSTER_NAME} --config cluster/kind-config.yaml
fi

echo "[2/4] Setting context..."
kubectl cluster-info --context kind-${CLUSTER_NAME}

echo "[3/4] Creating namespace..."
kubectl apply -f cluster/manifests/namespace.yaml

echo "[4/4] Deploying sample application..."
kubectl apply -f cluster/manifests/database.yaml
kubectl apply -f cluster/manifests/payment.yaml
kubectl apply -f cluster/manifests/checkout.yaml
kubectl apply -f cluster/manifests/frontend.yaml

echo "======================================"
echo " Setup complete! Services are starting."
echo " Run ./health-check.sh to monitor."
echo "======================================"
