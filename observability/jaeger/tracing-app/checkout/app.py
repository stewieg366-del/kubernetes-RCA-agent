import os
import time
import requests
from flask import Flask
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource

app = Flask(__name__)

resource = Resource(attributes={"service.name": "trace-checkout"})
provider = TracerProvider(resource=resource)
otlp_endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "http://jaeger.jaeger.svc.cluster.local:4318/v1/traces")
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

@app.route("/")
def checkout():
    time.sleep(0.05)
    payment_url = os.environ.get("PAYMENT_URL", "http://trace-payment.jaeger.svc.cluster.local:8080")
    response = requests.get(payment_url)
    return f"Checkout -> {response.text}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
