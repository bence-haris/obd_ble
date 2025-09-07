#!/usr/bin/env python3

import asyncio
from bleak import BleakClient

# Hardcode MAC Address, Characteristics
MAC = "81:23:45:67:89:BA"
TX_CHAR = "0000fff2-0000-1000-8000-00805f9b34fb"
RX_CHAR = "0000fff1-0000-1000-8000-00805f9b34fb"

commands = {"rpm":"30313043300d", "echo":"415445300d", "device":"4154490d", "speed": "30313044300d", "fuel":"30313545300d"}
response_data = []

# Incoming notifications
# Receive response bytearray
def notification_handler(sender, data: bytearray):
    response_data.append(data)
    
    # Process response
    if response_data:
        # Combine all notification data
        full_response = b''.join(response_data)
        ascii_response = full_response.decode('ascii', errors='ignore').strip()
        print(ascii_response)
    else:
        print("No response")


async def send_obd2_command(client, command):
    # Send command as bytes
    await client.write_gatt_char(TX_CHAR, bytes.fromhex(command), response=True)
    # Wait for response
    await asyncio.sleep(3)

    
async def main():
    command = commands["device"]
    async with BleakClient(MAC) as client:
        # Enable notifications
        await client.start_notify(RX_CHAR, notification_handler)
        
        # Send command
        await send_obd2_command(client, command)
        
        # Stop notifications
        await client.stop_notify(RX_CHAR)

if __name__ == "__main__":
    asyncio.run(main())