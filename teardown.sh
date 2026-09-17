#!/bin/bash
set -e

CLUSTER_NAME="rca-demo-cluster"

echo "======================================"
echo " Tearing down K8s RCA Agent Env"
echo "======================================"

if kind get clusters | grep -q "^${CLUSTER_NAME}$"; then
  kind delete cluster --name ${CLUSTER_NAME}
  echo "Cluster deleted successfully."
else
  echo "Cluster ${CLUSTER_NAME} does not exist."
fi
