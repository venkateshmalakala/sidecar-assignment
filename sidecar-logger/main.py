import time
import os
import json
import requests
import sys

LOG_FILE_PATH = "/var/log/app/app.log"
AGGREGATOR_URL = os.getenv("LOG_AGGREGATOR_URL")
SERVICE_NAME = os.getenv("SERVICE_NAME")
ENVIRONMENT = os.getenv("ENVIRONMENT")

def follow(file):
    # Read from the beginning of the file to catch startup logs
    file.seek(0, 0)
    while True:
        line = file.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line

def run():
    print(f"Sidecar Logger for {SERVICE_NAME} started.", flush=True)
    while not os.path.exists(LOG_FILE_PATH):
        print("Waiting for log file...", flush=True)
        time.sleep(1)
    
    print(f"Log file found at {LOG_FILE_PATH}. Tailing...", flush=True)
    with open(LOG_FILE_PATH, "r") as f:
        for line in follow(f):
            try:
                log_entry = json.loads(line)
                log_entry["service_name"] = SERVICE_NAME
                log_entry["environment"] = ENVIRONMENT
                
                # Send to aggregator
                resp = requests.post(AGGREGATOR_URL, json=log_entry)
                if resp.status_code != 202:
                    print(f"Failed to send log: {resp.status_code}", flush=True)
            except Exception as e:
                print(f"Error processing log line: {e}", flush=True)

if __name__ == "__main__":
    run()