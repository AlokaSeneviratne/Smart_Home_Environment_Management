# Smart Home Environment Management

A smart home system that automates heating control and presence detection for a single-person living environment, built using a Raspberry Pi Pico W, MQTT (HiveMQ), Node-RED, InfluxDB, and a React Native mobile app.

## Overview

The system detects whether a person is entering or leaving the apartment and adjusts the AC unit based on temperature readings, reducing wasted energy from heating/cooling an empty home.

## Architecture

Pressure Sensors + Accelerometer → Pico W → HiveMQ ↔ Node-RED → InfluxDB, with the Mobile App (React Native) connected to HiveMQ as well.

- **Sensor layer:** 2x pressure sensors + accelerometer (entrance detection), BMP280 (temperature/pressure)
- **Networking layer:** Pico W publishes sensor data to HiveMQ via MQTT; Node-RED handles processing
- **Data layer:** HiveMQ for messaging, InfluxDB for storage/visualization
- **Application layer:** React Native app for real-time monitoring and AC control
<img width="792" height="501" alt="extendedIoTArchitecture drawio" src="https://github.com/user-attachments/assets/4a7f5dc1-035a-4b6d-a1ca-cacff703a5dd" />

## Components

**Hardware:** Raspberry Pi Pico W, 2x BMP280, ISM330DLC (accelerometer/gyroscope)

**Software:** MicroPython (umqtt.simple, bmp280, machine), HiveMQ, Node-RED, InfluxDB, React Native (MQTT.js, react-native-chart-kit)

## MQTT Topics

- `entrance` — person entering/leaving
- `pressure1`, `pressure2` — entrance pressure sensor readings
- `accelerometer` — door movement readings
- `temperature` — ambient temperature
- `temp_control` — commands to (mocked) AC unit

## Detection Logic

Sliding window approach (11s window, 2s read interval): a sensor is "activated" if its max reading exceeds the mean by a threshold epsilon. Combining accelerometer triggers with the order of pressure sensor activations determines entry vs. exit direction.


<img width="894" height="450" alt="node_red_flow_temp_control" src="https://github.com/user-attachments/assets/67a8f832-39c8-4954-8a99-08be7d8da95d" />
<img width="871" height="363" alt="node_red_flow_main_entrance" src="https://github.com/user-attachments/assets/d30d61b4-1f1d-4e08-99ba-95c4aeb8b77b" />

## Mobile App

Two screens — Login (authentication) and Dashboard (live temperature chart, heating/cooling status, up/down controls via MQTT).


<img width="374" height="822" alt="dashboard" src="https://github.com/user-attachments/assets/dbd8bf7e-47a6-4617-b9f3-a904baed9d61" />
<img width="391" height="838" alt="Login_page" src="https://github.com/user-attachments/assets/a63b5e27-3c7d-4387-967a-9148f3d79914" />

## Evaluation Results

- Reading frequency: 2s intervals worked well; 10s was too sparse and missed events. 3s was a good balance.
- Evaluation frequency: 5-minute windows caused misclassified or missed events; 20s avoided this while saving resources.

## Limitations & Future Work

- Entrance detection via sensors is a workaround; real deployments could use phone geofencing/WiFi presence.
- AC control is mocked; real systems would integrate with existing smart AC APIs or a custom radiator controller.
- Event-driven sensing would reduce unnecessary messages vs. fixed polling.
- Planned: multi-user support with personalized preferences, integration with other smart devices (lighting), and a low-power mode.
