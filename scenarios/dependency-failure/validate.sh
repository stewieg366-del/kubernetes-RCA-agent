#!/bin/bash
echo "Validating Dependency Failure Scenario..."
echo "Testing frontend response:"
# We use kubectl exec into frontend to curl its own localhost since port-forwarding might not be set up in the script
kubectl exec deployment/frontend -n rca-demo -- curl -s -I http://localhost | head -n 1
echo "Expected evidence: Frontend returns 502 Bad Gateway because checkout cannot reach payment."
echo "Kubernetes evidence: No 'payment' service exists in 'kubectl get svc -n rca-demo'."
