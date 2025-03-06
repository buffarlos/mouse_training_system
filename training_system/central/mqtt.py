import paho.mqtt.client as mqtt
import threading

def initialize_network(mouse_id, stage):
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    
    # Create an event to wait for confirmation.
    confirmation_event = threading.Event()
    
    # Store mouse_id and the event in userdata for access in callbacks.
    mqttc.user_data_set({'mouse_id': mouse_id, 'confirmation_event': confirmation_event})
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message

    # Connect to the broker.
    mqttc.connect("192.168.0.135", 1883, 60)
    
    # Start the network loop in a background thread.
    mqttc.loop_start()

    # Publish a message to the stage topic.
    mqttc.publish(f"mouse_{mouse_id}/stage", stage)
    
    # Subscribe to the data topic.
    mqttc.subscribe(f"mouse_{mouse_id}/data")
    
    # Wait until the confirmation_event is set (i.e., until 'acknowledged' is received).
    print("Waiting for confirmation...")
    confirmation_event.wait(10)  # You can adjust the timeout as needed.
    print("Confirmation received. Continuing execution.")
    
    return mqttc

# Callback for when the client connects to the broker.
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")

# Callback for when a PUBLISH message is received.
def on_message(client, userdata, msg):
    payload_str = msg.payload.decode('utf-8')
    print(f"Received on {msg.topic}: {payload_str}")
    
    # Check if this is the confirmation message.
    if payload_str == 'acknowledged':
        print("Confirmation received! Starting to save incoming data...")
        confirmation_event = userdata.get('confirmation_event')
        if confirmation_event:
            confirmation_event.set()
        # Do not save the "acknowledged" message to the file.
    else:
        # For all other messages, save the data.
        mouse_id = userdata.get('mouse_id', 'default')
        filename = f"mouse_{mouse_id}.txt"
        with open(filename, "a") as file:
            file.write(payload_str + "\n")
        print(f"Data saved to {filename}.")
