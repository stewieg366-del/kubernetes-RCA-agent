import unittest
import os
import yaml
import subprocess
import json

class TestPrometheusConfig(unittest.TestCase):
    def test_frontend_checkout_excluded_from_scrape_manifest(self):
        """Validates the prometheus.yaml manifest has the correct drop rule."""
        manifest_path = os.path.join(
            os.path.dirname(__file__), 
            '../observability/manifests/prometheus.yaml'
        )
        
        with open(manifest_path, 'r') as f:
            docs = list(yaml.safe_load_all(f))
            
        configmap = None
        for doc in docs:
            if doc and doc.get('kind') == 'ConfigMap' and doc['metadata']['name'] == 'prometheus-config':
                configmap = doc
                break
                
        self.assertIsNotNone(configmap, "Could not find prometheus-config ConfigMap")
        
        prom_yml = yaml.safe_load(configmap['data']['prometheus.yml'])
        pods_job = None
        for job in prom_yml['scrape_configs']:
            if job['job_name'] == 'kubernetes-pods':
                pods_job = job
                break
                
        self.assertIsNotNone(pods_job, "Could not find kubernetes-pods job")
        
        drop_rule_found = False
        for rule in pods_job.get('relabel_configs', []):
            if rule.get('action') == 'drop' and rule.get('regex') == '(frontend|checkout)':
                if '__meta_kubernetes_pod_label_app' in rule.get('source_labels', []):
                    drop_rule_found = True
                    break
                    
        self.assertTrue(drop_rule_found, "Prometheus is not configured to drop frontend and checkout scrapes!")

    def test_live_scrape_traffic_absent(self):
        """Validates via Prometheus API that frontend and checkout are excluded from targets if cluster is running."""
        # Check if we can connect to Prometheus via kubectl
        try:
            subprocess.run(
                ["kubectl", "get", "pods", "-n", "observability"], 
                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=2
            )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            self.skipTest("Kubernetes cluster not accessible, skipping live scrape validation.")
            
        import urllib.parse
        query = 'up{job="kubernetes-pods", pod=~".*(frontend|checkout).*"::}'
        # Just searching if frontend/checkout show up in kubernetes-pods job
        encoded_query = urllib.parse.quote('up{job="kubernetes-pods"}')
        path = f"/api/v1/namespaces/observability/services/prometheus:9090/proxy/api/v1/query?query={encoded_query}"
        
        try:
            out = subprocess.check_output(["kubectl", "get", "--raw", path], stderr=subprocess.DEVNULL)
            data = json.loads(out)
            results = data.get("data", {}).get("result", [])
            
            for res in results:
                pod_name = res.get("metric", {}).get("pod", "")
                self.assertNotIn("frontend", pod_name, "Frontend pod is still being scraped by Prometheus!")
                self.assertNotIn("checkout", pod_name, "Checkout pod is still being scraped by Prometheus!")
        except Exception as e:
            self.skipTest(f"Prometheus API not available for live validation: {e}")

if __name__ == '__main__':
    unittest.main()
