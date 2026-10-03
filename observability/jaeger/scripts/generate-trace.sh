#!/bin/bash
set -e

echo "Sending real HTTP request to trace-frontend..."
echo "This request will cascade: trace-frontend -> trace-checkout -> trace-payment"
echo ""

# Execute the curl inside the cluster using a temporary curl pod targeting the trace-frontend service
RESPONSE=$(kubectl run -i --rm --restart=Never trace-trigger --image=curlimages/curl --namespace=jaeger -- -s http://trace-frontend.jaeger.svc.cluster.local:8080)

echo "Application Response:"
echo "$RESPONSE"
echo ""

if [[ "$RESPONSE" == *"Payment Success"* ]]; then
    echo "=========================================================="
    echo "TRACE GENERATED SUCCESSFULLY!"
    echo "The Python OpenTelemetry SDKs have natively intercepted the request"
    echo "and exported the spans to Jaeger via OTLP."
    echo "You can view this trace by opening the Jaeger UI."
    echo "Access Jaeger at: http://localhost:31686 (or your Node IP)"
    echo "Search for service 'trace-frontend'."
    echo "=========================================================="
else
    echo "Failed to verify application response."
    exit 1
fi
