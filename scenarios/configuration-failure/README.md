# Configuration Failure Scenario

## Description
This scenario demonstrates a configuration error where the Kubernetes workload (`checkout` Deployment) remains `Running` and fully `Available`, but application requests fail. 

The `checkout` Nginx proxy is dynamically configured to point to an upstream service. We simulate a human error where the ConfigMap (`checkout-config`) is updated with a typo in the upstream hostname (`payment-service-typo.rca-demo.svc.cluster.local`).

Because Nginx resolves variables at runtime, it does not crash on startup. The Kubernetes health probes (which are absent or purely TCP-based) report the pod as healthy. However, when traffic flows in from the frontend, Nginx attempts to resolve the bad DNS name, fails, and returns a `502 Bad Gateway`.

## Evidence
- `get_deployment("rca-demo", "checkout")` shows 1/1 replicas Available.
- `get_pod("rca-demo", "<checkout-pod>")` shows Phase: Running.
- `query_loki` for checkout or frontend logs will reveal `502` errors. Specifically, `checkout` logs will show `payment-service-typo.rca-demo.svc.cluster.local could not be resolved (3: Host not found)`.

## Execution
```bash
./trigger.sh
./validate.sh
./reset.sh
```
