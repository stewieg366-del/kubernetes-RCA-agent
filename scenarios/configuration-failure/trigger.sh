#!/bin/bash
set -e

echo "Triggering configuration-failure scenario..."

# 1. Update the ConfigMap with a broken upstream URL
kubectl patch configmap checkout-config -n rca-demo -p '{"data":{"default.conf":"server {\n    listen 80;\n    resolver kube-dns.kube-system.svc.cluster.local valid=5s;\n    set $upstream http://payment-service-typo.rca-demo.svc.cluster.local;\n    location / {\n        proxy_pass $upstream;\n        proxy_connect_timeout 5s;\n        proxy_read_timeout 5s;\n    }\n}\n"}}'

# 2. Restart the deployment so it picks up the bad config
kubectl rollout restart deployment checkout -n rca-demo

# 3. Wait for the rollout to complete. Because there are no liveness probes that check the upstream,
# the pod will successfully become Ready and the deployment will be Available!
kubectl rollout status deployment checkout -n rca-demo --timeout=90s

echo "Scenario triggered successfully."
