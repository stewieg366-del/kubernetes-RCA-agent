#!/bin/bash
set -e
echo "Triggering Dependency Failure Scenario..."
kubectl delete service payment -n rca-demo
echo "Payment service deleted. Checkout will fail to resolve the upstream."
