import hmac
import hashlib
import json
import time
from locust import HttpUser, task, between

SECRET_KEY = b"this_is_a_secret_key_for_webhooks"

class StressTestRunner(HttpUser):
    """
    Stress & Load Testing - Simulate heavy webhook traffic.
    Floods the /ingest/webhook endpoint with signed payloads.
    """
    wait_time = between(0.1, 0.5)  # High frequency

    def on_start(self):
        self.doc_url = "https://raw.githubusercontent.com/pdf-association/pdf-test-suite/master/Large_files/extremely_large_file_mock.pdf"
        # In a real stress test, we'd point to a 10MB+ file in S3 or local mock server.

    @task
    def simulate_heavy_load(self):
        """
        Generates a signed webhook payload and hits the ingestion endpoint.
        """
        payload = {
            "reference_id": f"STRESS-TEST-{time.time()}",
            "document_url": self.doc_url,
            "provider": "locust-stress-agent",
            "metadata": {
                "batch_id": "STRESS_S43",
                "is_stress_test": True
            }
        }
        
        json_payload = json.dumps(payload).encode('utf-8')
        
        # Compute HMAC signature for the payload
        signature = hmac.new(
            SECRET_KEY,
            json_payload,
            hashlib.sha256
        ).hexdigest()

        headers = {
            "Content-Type": "application/json",
            "X-Signature": signature
        }

        with self.client.post("/api/v1/ingest/webhook", data=json_payload, headers=headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed with status: {response.status_code}")

    @task(3)
    def view_health(self):
        """Monitor API health latency during the flood."""
        self.client.get("/health")
