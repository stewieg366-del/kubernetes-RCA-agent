#!/bin/bash

# Ensure the pod is actually running and available
AVAILABLE=$(kubectl get deployment checkout -n rca-demo -o jsonpath='{.status.availableReplicas}')
if [ "$AVAILABLE" != "1" ]; then
    echo "Validation failed: checkout deployment is not available (it should be running and green)."
    exit 1
fi

# Send a request to frontend, which routes to checkout. It should return HTTP 502 (Bad Gateway)
HTTP_STATUS=$(kubectl exec -n rca-demo deployment/frontend -- curl -s -o /dev/null -w "%{http_code}" http://localhost)

if [ "$HTTP_STATUS" == "502" ]; then
    echo "Validation passed: frontend returned HTTP 502 due to checkout misconfiguration."
    exit 0
else
    echo "Validation failed: expected HTTP 502, got HTTP $HTTP_STATUS."
    exit 1
fi
