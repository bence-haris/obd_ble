#!/usr/bin/env python3

import asyncio
from bleak import BleakClient

# Hardcode MAC Address, Characteristics
MAC = "81:23:45:67:89:BA"
TX_CHAR = "0000fff2-0000-1000-8000-00805f9b34fb"
RX_CHAR = "0000fff1-0000-1000-8000-00805f9b34fb"

commands = {"rpm":"30313043300d", "echo":"415445300d", "device":"4154490d", "speed": "30313044300d", "fuel":"30313545300d"}
commands_binary = {'echo':b'ATE0\r', 'device':b'ATI\r', 'rpm':b'010C0\r', 'speed': b'010D0\r', 'fuel':b'015E0\r'}
response_data = []


def calculate_rpm(high_bit, low_bit):
    return (high_bit * 256 + low_bit) / 4


def decode_response(response_bytes):
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

                        output = f"RPM: {calculate_rpm(val_high, val_low)}"
                        return output
                    # Speed
                    case "0D":
                        val_speed = int(data_snippet[6:8], 16)

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
    command = commands_binary["echo"]
    async with BleakClient(MAC) as client:
        # Enable notifications
        await client.start_notify(RX_CHAR, notification_handler)

        # Send command
        await send_obd2_command(client, command)

        # Stop notifications
        await client.stop_notify(RX_CHAR)

if __name__ == "__main__":
    asyncio.run(main())
