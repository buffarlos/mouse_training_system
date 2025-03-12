import paho.mqtt.client as mqtt
import threading

def initialize_network(mouse_id, stage, ip):
    """
    Initializes the MQTT client, subscribes to topics, and publishes the stage.
    Waits for a 'ping' confirmation before publishing the stage.
    """
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    # Set up userdata with mouse_id.
    mqttc.user_data_set({'mouse_id': mouse_id})
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message

    # Connect to the broker.
    mqttc.connect(ip, 1883, 60)
    
    # Start the network loop in a background thread.
    mqttc.loop_start()

    # Subscribe to topics.
    mqttc.subscribe(f"mouse_{mouse_id}/data")
    mqttc.subscribe(f"mouse_{mouse_id}/request")

    # Wait for a ping before publishing the stage.
    if wait_for_ping(mqttc, timeout=100):
        mqttc.publish(f"mouse_{mouse_id}/stage", stage)
        print(f"Published stage '{stage}' after receiving ping.")
    else:
        print("Timeout waiting for ping. Stage not published during initialization.")

    return mqttc

def wait_for_ping(client, timeout=10):
    ping_event = threading.Event()
    userdata = client._userdata
    userdata['ping_event'] = ping_event
    userdata['waiting_for_ping'] = True  # Set the flag indicating we are waiting for a ping

    print("Waiting for ping on request topic before publishing stage...")
    received = ping_event.wait(timeout)
    print("Ping received!" if received else "Ping wait timed out.")

    # Clean up: remove both the ping event and waiting flag
    userdata.pop('waiting_for_ping', None)
    userdata.pop('ping_event', None)
    return received


def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")

def on_message(client, userdata, msg):
    payload_str = msg.payload.decode('utf-8')
    mouse_id = userdata.get('mouse_id', 'default')
    print(f"Received on {msg.topic}: {payload_str}")

    if msg.topic == f"mouse_{mouse_id}/request" and payload_str == 'ping':
        # Only react if we are explicitly waiting for a ping
        if userdata.get('waiting_for_ping', False):
            ping_event = userdata.get('ping_event')
            if ping_event:
                ping_event.set()
                print("Ping processed for waiting event!")
    else:
        # Save any non-ping messages to a file.
        filename = f"mouse_{mouse_id}/mouse_{mouse_id}.txt"
        with open(filename, "a") as file:
            file.write(payload_str + "\n")
        print(f"Data saved to {filename}.")

