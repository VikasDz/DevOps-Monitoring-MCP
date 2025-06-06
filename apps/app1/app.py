from flask import Flask
import random
import time
import logging
from pythonjsonlogger import jsonlogger
from prometheus_client import make_wsgi_app, Counter, start_http_server

app = Flask(__name__)

# Configure JSON logging
logger = logging.getLogger()
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

@app.route('/')
def healthy():
    logger.info("Health check OK", extra={"app": "app1", "type": "healthcheck"})
    return "App1 Running OK"


# Add these lines after Flask app creation
REQUEST_COUNT = Counter(
    'app1_request_count',
    'Application Request Count',
    ['method', 'endpoint', 'http_status']
)

@app.route('/metrics')
def metrics():
    return make_wsgi_app()


@app.route('/error')
def error_endpoint():
    try:
        if random.random() > 0.5:
            time.sleep(10)
            logger.error("Intentional error triggered", extra={"app": "app1", "type": "error"})
            return "Error triggered", 500
        return "Normal response"
    except Exception as e:
        logger.error("Endpoint failed", exc_info=True, extra={"app": "app1", "type": "error"})
        return "Internal error", 500

@app.route('/health')
def health():
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)