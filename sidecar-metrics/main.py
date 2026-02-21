import time
import os
import requests
import threading
from flask import Flask, Response

app = Flask(__name__)

APP_METRICS_URL = os.getenv("APP_METRICS_URL")
SERVICE_NAME = os.getenv("SERVICE_NAME")
ENVIRONMENT = os.getenv("ENVIRONMENT")
SCRAPE_INTERVAL = 15

latest_metrics = ""

def enrich_metrics(raw_data):
    enriched = []
    lines = raw_data.split('\n')
    for line in lines:
        if line.strip() and not line.startswith('#'):
            # Split from the right to handle spaces in labels correctly
            parts = line.rsplit(' ', 1)
            if len(parts) == 2:
                metric_part = parts[0]
                value_part = parts[1]
                
                if '{' in metric_part:
                    base_name, labels = metric_part.split('{', 1)
                    labels = labels.rstrip('}')
                    new_labels = f'{labels},service_name="{SERVICE_NAME}",environment="{ENVIRONMENT}"'
                    enriched.append(f'{base_name}{{{new_labels}}} {value_part}')
                else:
                    new_labels = f'service_name="{SERVICE_NAME}",environment="{ENVIRONMENT}"'
                    enriched.append(f'{metric_part}{{{new_labels}}} {value_part}')
    return "\n".join(enriched)

def scraper_loop():
    global latest_metrics
    while True:
        try:
            resp = requests.get(APP_METRICS_URL)
            if resp.status_code == 200:
                latest_metrics = enrich_metrics(resp.text)
        except Exception as e:
            print(f"Scrape failed: {e}", flush=True)
        time.sleep(SCRAPE_INTERVAL)

@app.route('/metrics')
def metrics():
    return Response(latest_metrics, mimetype='text/plain')

if __name__ == "__main__":
    t = threading.Thread(target=scraper_loop, daemon=True)
    t.start()
    port = int(os.getenv("PORT", 9100))
    app.run(host="0.0.0.0", port=port)