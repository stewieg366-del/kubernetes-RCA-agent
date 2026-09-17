#!/bin/bash
echo "Validating OOM Scenario..."

# Get the pod name
POD_NAME=$(kubectl get pods -n rca-demo -l app=oom-workload -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

if [ -z "$POD_NAME" ]; then
    echo "Error: OOM workload pod not found."
    echo "FAIL"
    exit 1
fi

STATUS=$(kubectl get pod $POD_NAME -n rca-demo -o jsonpath='{.status.phase}')
RESTARTS=$(kubectl get pod $POD_NAME -n rca-demo -o jsonpath='{.status.containerStatuses[0].restartCount}')
LAST_REASON=$(kubectl get pod $POD_NAME -n rca-demo -o jsonpath='{.status.containerStatuses[0].lastState.terminated.reason}')
LAST_EXIT_CODE=$(kubectl get pod $POD_NAME -n rca-demo -o jsonpath='{.status.containerStatuses[0].lastState.terminated.exitCode}')

echo "Current pod status      : ${STATUS:-Unknown}"
echo "Restart count           : ${RESTARTS:-0}"
echo "Last termination reason : ${LAST_REASON:-None}"
echo "Last termination exit code: ${LAST_EXIT_CODE:-None}"

if [ "$LAST_REASON" == "OOMKilled" ] && [ "$LAST_EXIT_CODE" == "137" ]; then
    echo ""
    echo "PASS: Genuine OOM event detected."
    exit 0
else
    echo ""
    echo "FAIL: OOM event not detected."
    exit 1
fi
