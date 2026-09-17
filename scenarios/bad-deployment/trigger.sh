#!/bin/bash
set -e
echo "Triggering Bad Deployment Scenario..."
kubectl set image deployment/payment payment=nginx:invalid-version-123 -n rca-demo
echo "Payment deployment updated with an invalid image."
