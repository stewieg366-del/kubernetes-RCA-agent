#!/bin/bash
set -e
echo "Resetting OOM Scenario..."
kubectl delete deployment oom-workload -n rca-demo --ignore-not-found
echo "OOM workload removed."
