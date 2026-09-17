#!/bin/bash
echo "Validating Observability Stack..."

# 1. Prometheus
PROM_RES=$(kubectl get --raw "/api/v1/namespaces/observability/services/prometheus:9090/proxy/api/v1/query?query=up" 2>/dev/null)
if echo "$PROM_RES" | grep -q '"status":"success"'; then
    echo "[PASS] Prometheus is running and answering queries."
else
    echo "[FAIL] Prometheus query failed."
fi

# 2. Loki
# Make a request to frontend to ensure there's at least one log
kubectl exec -n rca-demo deployment/frontend -- curl -s -I http://localhost > /dev/null || true
sleep 3
LOKI_RES=$(kubectl get --raw "/api/v1/namespaces/observability/services/loki:3100/proxy/loki/api/v1/query?query={namespace=\"rca-demo\"}&limit=50" 2>/dev/null)

if echo "$LOKI_RES" | grep -q '"status":"success"'; then
    echo "[PASS] Loki is running and answering queries."
    if echo "$LOKI_RES" | grep -q 'frontend'; then
        echo "[PASS] rca-demo logs (frontend) successfully retrieved from Loki."
    else
        echo "[FAIL] rca-demo logs were not found in Loki."
    fi
else
    echo "[FAIL] Loki query failed."
fi
if echo "$LOKI_RES" | grep -q 'checkout'; then
    echo "[PASS] rca-demo logs (checkout) successfully retrieved from Loki."
fi
if echo "$LOKI_RES" | grep -q 'payment'; then
    echo "[PASS] rca-demo logs (payment) successfully retrieved from Loki."
fi
