import paho.mqtt.client as mqtt
import json

from datetime import datetime, timezone

def test_publish_status(mqtt_client, topic, state):
    payload = {
        "timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat() + "Z",
        "status": state,
        "intersection_id": '0'
    }
    try:
        mqtt_client.publish(topic, json.dumps(payload), qos=1)
        print(f"Published to {topic}: {payload}")
    except Exception as e:
        print(f"MQTT publish failed: {e}")

if __name__ == "__main__":
    # MQTT配置
    MQTT_BROKER = "mqtt-dashboard.com"

    MQTT_STATUS_TOPIC = "traffic_light/0/status"
    
    # 创建MQTT客户端
    mqtt_client = mqtt.Client()
    mqtt_client.port = 8884
    mqtt_client.connect(MQTT_BROKER)
    
    # 测试发布状态
    test_publish_status(mqtt_client, MQTT_STATUS_TOPIC, "Green")
    
    # 断开连接
    mqtt_client.disconnect()