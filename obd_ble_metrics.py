#!/usr/bin/python3


import time
import asyncio
import logging
from prometheus_client import Gauge, start_http_server

rpm_gauge = Gauge('obd_ble_rpm', 'RPM Value', ['device_id'])
kmh_gauge = Gauge('obd_ble_kmh', 'Speed Value', ['device_id'])


DEVICE_ID = "ELM327"
PROMETHEUS_PORT = 9100
COLLECTION_INTERVAL = 10

async def read_obd_metrics():
    try:
        import random
        rpm = random.randint(1000, 3000)  # Simulated RPM between 1000-3000
        speed = random.randint(20, 120)   # Simulated speed between 20-120 km/h
        print(f"Read RPM: {rpm}, Speed: {speed} km/h")
        return rpm, speed
    except Exception as e:
        print("Failed to read metrics")
        return None, None

async def main():
    start_http_server(PROMETHEUS_PORT)
    print("Server Started")

    while True:
        try:
            rpm, speed = await read_obd_metrics()

            if rpm is not None:
                rpm_gauge.labels(device_id=DEVICE_ID).set(rpm)

            if speed is not None:
                kmh_gauge.labels(device_id=DEVICE_ID).set(speed)

        except Exception as e:
            print("Problem in main")

        await asyncio.sleep(COLLECTION_INTERVAL)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting down collector")
