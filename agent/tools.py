from langchain_core.tools import tool
import sys
import os

# Add parent directory to path to import observability
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from observability import kubernetes_tools, prometheus_tools, loki_tools

@tool
def get_pods(namespace: str) -> str:
    """Gets a list of all pods in the specified namespace."""
    return kubernetes_tools.get_pods(namespace).json()

@tool
def get_pod(namespace: str, pod_name: str) -> str:
    """Gets the basic status of a specific pod."""
    return kubernetes_tools.get_pod(namespace, pod_name).json()

@tool
def get_pod_events(namespace: str, pod_name: str) -> str:
    """Gets recent Kubernetes events for a specific pod."""
    return kubernetes_tools.get_pod_events(namespace, pod_name).json()

@tool
def get_deployment(namespace: str, deployment_name: str) -> str:
    """Gets the status of a specific deployment."""
    return kubernetes_tools.get_deployment(namespace, deployment_name).json()

@tool
def get_service(namespace: str, service_name: str) -> str:
    """Gets the status of a specific service."""
    return kubernetes_tools.get_service(namespace, service_name).json()

@tool
def get_container_status(namespace: str, pod_name: str) -> str:
    """Gets detailed container status including restarts, exit codes, and termination reasons."""
    return kubernetes_tools.get_container_status(namespace, pod_name).json()

@tool
def query_prometheus(query: str) -> str:
    """Executes a PromQL query against Prometheus to retrieve metrics."""
    return prometheus_tools.query_prometheus(query).json()

@tool
def query_prometheus_range(query: str, start: str, end: str) -> str:
    """Executes a PromQL range query against Prometheus."""
    return prometheus_tools.query_prometheus_range(query, start, end).json()

@tool
def query_loki(query: str, limit: int = 10) -> str:
    """Executes a LogQL query against Loki to retrieve application logs."""
    return loki_tools.query_loki(query, limit).json()

SAFE_TOOLS = [
    get_pods, get_pod, get_pod_events, get_deployment, get_service,
    get_container_status, query_prometheus, query_prometheus_range, query_loki
]
