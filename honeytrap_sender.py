import json
import time
import requests
import os

LOG_FILE = "/logs/events.jsonl"
INGEST_URL = "https://ingestion-production-c968.up.railway.app/ingest/event"

print("Honeytrap sender waiting for log file...")
while not os.path.exists(LOG_FILE):
    time.sleep(2)

print("Honeytrap sender started!")

with open(LOG_FILE, "r") as f:
    f.seek(0, 2)
    while True:
        line = f.readline()
        if not line:
            time.sleep(0.5)
            continue
        try:
            event = json.loads(line.strip())

            # normalize honeytrap event to ingestion format
            normalized = {
                "eventid": f"honeytrap.{event.get('type', 'connection')}",
                "src_ip": event.get("source-ip") or event.get("src_ip") or "unknown",
                "dst_port": event.get("destination-port") or event.get("dst_port"),
                "protocol": event.get("protocol", "tcp"),
                "sensor": "honeytrap",
                "timestamp": event.get("date") or event.get("timestamp"),
                "raw": event,
            }

            r = requests.post(INGEST_URL, json=normalized, timeout=5)
            print(f"Sent: {normalized['eventid']} port={normalized['dst_port']} → {r.status_code}")

        except json.JSONDecodeError:
            pass
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)
