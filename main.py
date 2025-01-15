from machine import Pin, I2C
import network
import time
from bme280 import BME280
from umqtt.robust import MQTTClient
import ssl
import config

led_pin = Pin('LED', Pin.OUT)

# Setup Wi-Fi
ssid = config.ssid
password = config.pwd

# Connect to Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

connection_timeout = 10
while connection_timeout > 0:
    if wlan.status() == 3:  # Connected
        break
    connection_timeout -= 1
    print('Waiting for Wi-Fi connection...')
    time.sleep(1)

# Check if connection was successful
if wlan.status() != 3:
    led_pin.on()
    time.sleep_ms(1000)
    led_pin.off()
    raise RuntimeError('[ERROR] Failed to establish a network connection')
else:
    led_pin.on()
    time.sleep_ms(500)
    led_pin.off()
    time.sleep_ms(500)
    led_pin.on()
    time.sleep_ms(500)
    led_pin.off()
    print('[INFO] CONNECTED!')
    network_info = wlan.ifconfig()
    print('[INFO] IP address:', network_info[0])

# Config SSL connection with Transport Layer Security encryption (no cert)
context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)  # Connect as client, not server/broker
context.verify_mode = ssl.CERT_NONE  # Do not verify server/broker cert

# MQTT client connect
client = MQTTClient(
    client_id=b'picow2',
    server=config.MQTT_BROKER,
    port=config.MQTT_PORT,
    user=config.MQTT_USER,
    password=config.MQTT_PWD,
    ssl=context,
    keepalive=300  # Keep-alive set to 5 minutes
)
client.connect()

# Unified callback function
def on_message(topic, msg):
    print(f"Received message: {msg} on topic: {topic}")
    if msg == b"up":
        led_pin.on()  
        time.sleep_ms(500)
        led_pin.off()
        time.sleep_ms(500)
        led_pin.on()
        time.sleep_ms(500)
        led_pin.off()
        print("Optimal temperature to move up")
    elif msg == b"down":
        led_pin.on()
        time.sleep_ms(500)
        led_pin.off()
        time.sleep_ms(500)
        led_pin.on()
        time.sleep_ms(500)
        led_pin.off()
        time.sleep_ms(500)
        led_pin.on()
        time.sleep_ms(500)
        led_pin.off()
        print("Optimal temperature to move down")

client.set_callback(on_message)
client.subscribe(b"picow/temp_control")

# Main loop with reconnection and keep-alive
while True:
    try:
        # Check for incoming messages
        client.check_msg()

        # Optional: Publish a keep-alive message every 60 seconds
        if time.ticks_ms() % 60000 == 0:
            publish(client, b"picow/keepalive", b"ping")

    except OSError as e:
        print(f"[ERROR] MQTT connection lost: {e}. Attempting to reconnect...")
        time.sleep(5)  # Wait before attempting to reconnect
        try:
            client.connect()  # Reconnect to the broker
            client.subscribe(b"picow/control")  # Resubscribe to topics
            print("[INFO] Reconnected to MQTT broker.")
        except Exception as e:
            print(f"[ERROR] Reconnection failed: {e}")

    # Sleep to control the loop frequency
    time.sleep(2)
