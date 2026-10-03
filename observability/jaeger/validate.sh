#!/bin/bash
set -e

echo "Validating Jaeger Showcase..."

JAEGER_POD=$(kubectl get pod -n jaeger -l app=jaeger -o jsonpath="{.items[0].status.phase}" 2>/dev/null || true)
if [ "$JAEGER_POD" == "Running" ]; then
    echo "PASS: Jaeger pod running"
else
    echo "FAIL: Jaeger pod not running ($JAEGER_POD)"
    exit 1
fi

FRONTEND_POD=$(kubectl get pod -n jaeger -l app=trace-frontend -o jsonpath="{.items[0].status.phase}" 2>/dev/null || true)
if [ "$FRONTEND_POD" == "Running" ]; then
    echo "PASS: trace-frontend pod running"
else
    echo "FAIL: trace-frontend pod not running ($FRONTEND_POD)"
    exit 1
fi

JAEGER_SVC=$(kubectl get svc -n jaeger jaeger -o jsonpath="{.metadata.name}" 2>/dev/null || true)
if [ "$JAEGER_SVC" == "jaeger" ]; then
    echo "PASS: Jaeger service available"
else
    echo "FAIL: Jaeger service not found"
    exit 1
fi

# Wait briefly for UI to be responsive
sleep 2

# Check UI reachable from within cluster
UI_STATUS=$(kubectl run -i --rm --restart=Never jaeger-ui-check --image=curlimages/curl --namespace=jaeger -- -s -o /dev/null -w "%{http_code}" http://jaeger.jaeger.svc.cluster.local:16686 2>/dev/null | grep -o "[0-9]\{3\}" | head -n 1 || true)
if [ "$UI_STATUS" == "200" ]; then
    echo "PASS: Jaeger UI reachable"
else
    echo "FAIL: Jaeger UI not reachable (HTTP $UI_STATUS)"
    exit 1
fi

# Generate trace
./observability/jaeger/scripts/generate-trace.sh > /dev/null 2>&1
echo "PASS: Trace generated"

echo "PASS: Distributed tracing showcase ready"
