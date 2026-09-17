#!/bin/bash
set -e
echo "Resetting Dependency Failure Scenario..."
# The script can be executed from anywhere, so we resolve paths relative to the script location
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
kubectl apply -f "$DIR/../../cluster/manifests/payment.yaml"
echo "Payment service restored."
