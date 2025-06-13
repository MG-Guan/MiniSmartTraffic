import RPi.GPIO as GPIO
import time
from queue import Queue
import os

import paho.mqtt.client as mqtt
import json
from datetime import datetime, timezone

# -------- GPIO设置 --------
RED_PIN = 11      # Pin 11
YELLOW_PIN = 13   # Pin 13
GREEN_PIN = 15    # Pin 15

GPIO.setmode(GPIO.BOARD)
GPIO.setup(RED_PIN, GPIO.OUT)
GPIO.setup(YELLOW_PIN, GPIO.OUT)
GPIO.setup(GREEN_PIN, GPIO.OUT)

# -------- 状态机定义 --------
STATES = ["Green", "Yellow", "Red"]
STATE_PINS = {
    "Red":     (GPIO.HIGH, GPIO.LOW,  GPIO.LOW),
    "Yellow":  (GPIO.LOW,  GPIO.HIGH, GPIO.LOW),
    "Green":   (GPIO.LOW,  GPIO.LOW,  GPIO.HIGH)
}
STATE_DURATION = 3   # 每个状态10秒

# Local file settings.
TMP_FILE = '/tmp/traffic_light.json'
TMP_TMP_FILE = '/tmp/traffic_light.json.tmp'

# -------- MQTT设置 --------
MQTT_BROKER = 'mqtt-dashboard.com'  # MQTT代理地址
INTERSECTION_ID = '0'
MQTT_COMMAND_TOPIC = f'traffic_light/{INTERSECTION_ID}/command'
MQTT_STATUS_TOPIC = f'traffic_light/{INTERSECTION_ID}/status'

# -------- 全局变量 --------
mode = "Auto"            # 当前模式
auto_index = 0           # 自动状态机索引
current_state = STATES[0]
state_start_time = time.time()
command_queue = Queue()
mqtt_client = None

# -------- 状态广播 --------
def publish_status(state):
    payload = {
        "timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat() + "Z",
        "status": state,
        "intersection_id": INTERSECTION_ID
    }

    # Publish to local file.
    with open(TMP_TMP_FILE, 'w') as f:
        f.write(json.dumps(payload).encode('utf-8'))
        f.flush()
        os.fsync(f.fileno())
    os.rename(TMP_TMP_FILE, TMP_FILE)  # rename to ensure atomic write

    # Publish to MQTT.
    try:
        mqtt_client.publish(MQTT_STATUS_TOPIC, json.dumps(payload), qos=1)
    except Exception as e:
        print(f"MQTT publish failed: {e}")

# -------- 控制灯 --------
def set_lights(state):
    red, yellow, green = STATE_PINS[state]
    GPIO.output(RED_PIN, red)
    GPIO.output(YELLOW_PIN, yellow)
    GPIO.output(GREEN_PIN, green)
    pass

def set_state(new_state, report=True):
    global current_state, state_start_time
    if new_state != current_state:
        current_state = new_state
        state_start_time = time.time()
        set_lights(new_state)
        if report:
            publish_status(new_state)

# -------- MQTT回调 --------
def on_message(client, userdata, msg):
    payload = msg.payload.decode('utf-8').strip()
    command_queue.put(payload)

def parse_command(command):
    json_command = json.loads(command)
    if isinstance(json_command, dict):
        return json_command.get('command', 'None').strip()
    return command.strip()

# -------- 主循环 --------
def main():
    global mqtt_client, mode, auto_index

    # 设置初始状态
    set_state(STATES[auto_index])

    # 配置MQTT
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(MQTT_BROKER)
    client.subscribe(MQTT_COMMAND_TOPIC)
    mqtt_client = client
    client.loop_start()

    try:
        while True:
            # 1. 处理MQTT命令
            while not command_queue.empty():
                cmd = parse_command(command_queue.get())
                print('Get a command:', cmd)
                if cmd == "Auto":
                    mode = "Auto"
                    # 回到自动时，从之前auto_index的下一个状态开始
                    auto_index = (auto_index + 1) % len(STATES)
                    set_state(STATES[auto_index])
                elif cmd in STATES:
                    mode = "Manual"
                    set_state(cmd)
                else:
                    print(f"未知命令: {cmd}")

            # 2. 自动状态周期切换
            now = time.time()
            if mode == "Auto":
                if now - state_start_time >= STATE_DURATION:
                    auto_index = (auto_index + 1) % len(STATES)
                    set_state(STATES[auto_index])

            time.sleep(0.05)

    except KeyboardInterrupt:
        print("Ctrl+C 退出 清理GPIO ...")
    finally:
        GPIO.output(RED_PIN, GPIO.LOW)
        GPIO.output(YELLOW_PIN, GPIO.LOW)
        GPIO.output(GREEN_PIN, GPIO.LOW)
        GPIO.cleanup()
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()