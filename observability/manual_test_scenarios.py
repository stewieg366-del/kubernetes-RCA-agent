import sys
import time
import subprocess
from kubernetes_tools import get_pod, get_pod_events, get_container_status, get_service
from prometheus_tools import query_prometheus
from loki_tools import query_loki

def run_cmd(cmd):
    subprocess.run(cmd, shell=True, check=True)

def print_ev(ev):
    print(f"[{ev.source}] {ev.type} on {ev.resource}: {ev.observation}")

print("=== OOM SCENARIO ===")
run_cmd("../scenarios/run.sh trigger oom")
time.sleep(10)
try:
    print_ev(get_pod("rca-demo", "oom-workload-something")) # We can't predict exact pod name easily in script, let's use a query
except:
    pass # In real test we extract pod name
run_cmd("../scenarios/run.sh reset oom")

print("\n=== BAD DEPLOYMENT SCENARIO ===")
run_cmd("../scenarios/run.sh trigger bad-deployment")
time.sleep(10)
run_cmd("../scenarios/run.sh reset bad-deployment")

print("\n=== DEPENDENCY FAILURE SCENARIO ===")
run_cmd("../scenarios/run.sh trigger dependency-failure")
time.sleep(10)
try:
    print_ev(get_service("rca-demo", "payment"))
    # Loki logs
    print_ev(query_loki('{namespace="rca-demo", container="checkout"} |= "error"'))
except Exception as e:
    print("Error:", e)
run_cmd("../scenarios/run.sh reset dependency-failure")
