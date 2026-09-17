#!/bin/bash
echo "Validating Bad Deployment Scenario..."
kubectl get pods -n rca-demo -l app=payment
echo "Expected evidence: Payment pod status shows ImagePullBackOff or ErrImagePull."
