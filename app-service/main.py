import os
import json
import time
import random
import logging
from flask import Flask, Response

app = Flask(__name__)

LOG_FILE_PATH = "/var/log/app/app.log"
os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)

def write_log(level, message):
    entry = {
        "level": level,
        "message": message,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
    }
    with open(LOG_FILE_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")

@app.route('/health')
def health():
    return "OK", 200

@app.route('/')
def root():
    write_log("info", f"Root endpoint accessed on {os.getenv('SERVICE_NAME')}")
    return f"Hello from {os.getenv('SERVICE_NAME')}"

@app.route('/metrics')
def metrics():
    requests_count = random.randint(10, 100)
    metric_data = f'http_requests_total{{method="GET", path="/"}} {requests_count}\n'
    return Response(metric_data, mimetype='text/plain')

if __name__ == "__main__":
    port = int(os.getenv("PORT", 3000))
    app.run(host="0.0.0.0", port=port)