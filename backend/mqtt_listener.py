import json
import sqlite3
import paho.mqtt.client as mqtt
import sys
import time
from datetime import datetime

MQTT_BROKER = 'localhost'
MQTT_PORT = 1883
MQTT_TOPIC = 'traffic/violation'

DB_FILE = 'traffic_data.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS violations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            type TEXT,
            plate TEXT,
            location TEXT,
            image_base64 TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_violation(data):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO violations (timestamp, type, plate, location, image_base64)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            data.get('timestamp'),
            data.get('type'),
            data.get('plate'),
            data.get('location'),
            data.get('image')
        ))
        conn.commit()
        conn.close()
        print("[DB] Record inserted:", data)
    except Exception as e:
        print("[ERROR] Failed to insert:", e)

def on_message(client, userdata, msg):
    print(f"[MQTT] Received message on {msg.topic}")
    try:
        data = json.loads(msg.payload.decode())
        insert_violation(data)
    except Exception as e:
        print("[ERROR] MQTT message processing failed:", e)

def start_mqtt():
    init_db()
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.subscribe(MQTT_TOPIC)
    print(f"[MQTT] Subscribed to topic: {MQTT_TOPIC}")
    client.loop_forever()

def run_test_inserts(n=5):
    init_db()
    for i in range(n):
        test_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": "Running Red",
            "plate": f"TEST{i:03}",
            "location": "Intersection X",
            "image": None
        }
        insert_violation(test_data)
        time.sleep(1)

# === 主入口 ===
if __name__ == '__main__':
    if '--test' in sys.argv:
        print("[MODE] Running in test mode: inserting fake data...")
        run_test_inserts()
    else:
        print("[MODE] MQTT mode. To insert test data, run: python mqtt_listener.py --test")
        # start_mqtt()
