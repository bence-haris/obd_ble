#!/usr/bin/env python3

import asyncio
from bleak import BleakClient
from prometheus_client import Gauge, start_http_server

# Hardcode MAC Address, Characteristics
MAC = "81:23:45:67:89:BA"
TX_CHAR = "0000fff2-0000-1000-8000-00805f9b34fb"
RX_CHAR = "0000fff1-0000-1000-8000-00805f9b34fb"

commands_binary = {'echo':b'ATE0\r', 'device':b'ATI\r', 'rpm':b'010C0\r', 'speed': b'010D0\r'}

response_data = []
metrics = {'speed':0,'rpm':0.0}

rpm_gauge = Gauge('obd_ble_rpm', 'RPM Value', ['device_id'])
kmh_gauge = Gauge('obd_ble_kmh', 'Speed Value', ['device_id'])

DEVICE_ID = "ELM327"
PROMETHEUS_PORT = 9100


def calculate_rpm(high_bit, low_bit):
    return (high_bit * 256 + low_bit) / 4


def decode_response(response_bytes):
    output = ""
    response_array=response_bytes.decode('ascii', errors='ignore').strip().split('\n')
    output = str()
    for data_snippet in response_array:
        try:
            # Service 01 Response - Show current data
            if data_snippet[:2] == "41":
                # PID (in Hex)
                match data_snippet[3:5]:
                    # RPM
                    case "0C":
                        val_high=int(data_snippet[6:8],16)
                        val_low=int(data_snippet[9:11],16)
                        rpm = calculate_rpm(val_high, val_low)


                        metrics.update({'rpm':rpm})
                        output = f"RPM: {rpm}"
                        return output
                    # Speed
                    case "0D":
                        val_speed = int(data_snippet[6:8], 16)

                        metrics.update({'speed':val_speed})
                        output = f"Speed: {val_speed}"
                        return output
            # Other command given or response is undefined
            else:
                output += str(data_snippet).replace("\r","")
        except IndexError:
            output += str(data_snippet).replace("\r","")
            continue
    return output


# Incoming notifications
# Receive response bytearray
def notification_handler(sender, data: bytearray):
    response_data = []
    # TODO
    # Check if data arrives
    response_data.append(data)

    # Process response
    if response_data:
        # Combine all notification data
        full_response = b''.join(response_data)
        response_decoded = decode_response(full_response)
        print(response_decoded)
    else:
        print("No response")


async def send_obd2_command(client, command_binary):
    # Send command as bytes
    await client.write_gatt_char(TX_CHAR, command_binary, response=True)
    # Wait for response
    await asyncio.sleep(1)


async def main():

    start_http_server(PROMETHEUS_PORT)
    print(f"Exporter exporting on {PROMETHEUS_PORT}")

    while True:
        for key in commands_binary:
            #print(key)
            command = commands_binary[key]
            async with BleakClient(MAC) as client:
                # Enable notifications
                await client.start_notify(RX_CHAR, notification_handler)

                # Send command
                await send_obd2_command(client, command)

                rpm_gauge.labels(device_id=DEVICE_ID).set(metrics['rpm'])
                kmh_gauge.labels(device_id=DEVICE_ID).set(metrics['speed'])

                # Stop notifications
                await client.stop_notify(RX_CHAR)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exporter stopped")
