from kubernetes import client, config
from .models import Evidence
from datetime import datetime
from zoneinfo import ZoneInfo
import json

try:
    config.load_kube_config()
except:
    config.load_incluster_config()

v1 = client.CoreV1Api()
appsv1 = client.AppsV1Api()

ALLOWED_NAMESPACES = ["rca-demo"]

def validate_namespace(ns):
    if ns not in ALLOWED_NAMESPACES:
        raise ValueError(f"SECURITY BLOCK: Namespace {ns} is not permitted for read access.")

def get_pods(namespace: str):
    validate_namespace(namespace)
    pods = v1.list_namespaced_pod(namespace)
    return Evidence(
        source="kubernetes",
        type="pod_list",
        resource=f"{namespace}",
        observation=f"Found {len(pods.items)} pods",
        timestamp=datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(),
        metadata={"pod_names": [p.metadata.name for p in pods.items]}
    )

def get_pod(namespace: str, pod_name: str):
    validate_namespace(namespace)
    pod = v1.read_namespaced_pod(pod_name, namespace)
    return Evidence(
        source="kubernetes",
        type="pod_status",
        resource=f"{namespace}/{pod_name}",
        observation=f"Pod phase is {pod.status.phase}",
        timestamp=datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(),
        metadata={"phase": pod.status.phase}
    )

def get_pod_events(namespace: str, pod_name: str):
    validate_namespace(namespace)
    events = v1.list_namespaced_event(namespace, field_selector=f"involvedObject.name={pod_name}")
    obs = [f"{e.reason}: {e.message}" for e in events.items]
    return Evidence(
        source="kubernetes",
        type="pod_events",
        resource=f"{namespace}/{pod_name}",
        observation=f"Found {len(obs)} events",
        timestamp=datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(),
        metadata={"events": obs[-5:]}  # limit to last 5 for brevity
    )

def get_container_status(namespace: str, pod_name: str):
    validate_namespace(namespace)
    pod = v1.read_namespaced_pod(pod_name, namespace)
    statuses = pod.status.container_statuses or []
    obs = []
    restarts = 0
    for cs in statuses:
        restarts += cs.restart_count
        if cs.state.terminated:
            obs.append(f"Terminated ({cs.state.terminated.reason}): exit {cs.state.terminated.exit_code}")
        elif cs.state.waiting:
            obs.append(f"Waiting ({cs.state.waiting.reason})")
        elif cs.state.running:
            obs.append(f"Running (restarts: {cs.restart_count})")
            
        if cs.last_state and cs.last_state.terminated:
             obs.append(f"LastState Terminated ({cs.last_state.terminated.reason}): exit {cs.last_state.terminated.exit_code}")

    return Evidence(
        source="kubernetes",
        type="container_status",
        resource=f"{namespace}/{pod_name}",
        observation=" | ".join(obs),
        timestamp=datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(),
        metadata={"restarts": restarts}
    )

def get_service(namespace: str, service_name: str):
    validate_namespace(namespace)
    try:
        svc = v1.read_namespaced_service(service_name, namespace)
        return Evidence(
            source="kubernetes",
            type="service_status",
            resource=f"{namespace}/{service_name}",
            observation=f"Service exists with IP {svc.spec.cluster_ip}",
            timestamp=datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(),
            metadata={"exists": True}
        )
    except client.exceptions.ApiException as e:
        if e.status == 404:
             return Evidence(
                source="kubernetes",
                type="service_status",
                resource=f"{namespace}/{service_name}",
                observation="Service not found",
                timestamp=datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(),
                metadata={"exists": False}
            )
        raise e

def get_deployment(namespace: str, deployment_name: str):
    validate_namespace(namespace)
    try:
        dep = appsv1.read_namespaced_deployment(deployment_name, namespace)
        return Evidence(
            source="kubernetes",
            type="deployment_status",
            resource=f"{namespace}/{deployment_name}",
            observation=f"Deployment ready_replicas: {dep.status.ready_replicas}/{dep.status.replicas}",
            timestamp=datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(),
            metadata={"ready": dep.status.ready_replicas, "replicas": dep.status.replicas}
        )
    except client.exceptions.ApiException as e:
        if e.status == 404:
            return Evidence(
                source="kubernetes",
                type="deployment_status",
                resource=f"{namespace}/{deployment_name}",
                observation="Deployment not found",
                timestamp=datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(),
                metadata={"exists": False}
            )
        raise e
