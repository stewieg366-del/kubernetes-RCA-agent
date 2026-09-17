#!/bin/bash
set -e
echo "Triggering OOM Scenario..."
cat << 'YAML' | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: oom-workload
  namespace: rca-demo
spec:
  replicas: 1
  selector:
    matchLabels:
      app: oom-workload
  template:
    metadata:
      labels:
        app: oom-workload
    spec:
      containers:
      - name: memory-hog
        image: python:3.11-alpine
        command: ["python", "-c", "import time; a=[]; \nwhile True: a.append(' ' * 10**6); time.sleep(0.1)"]
        resources:
          requests:
            memory: "32Mi"
          limits:
            memory: "64Mi"
YAML
echo "OOM workload deployed."
