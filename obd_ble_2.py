#!/usr/bin/env python3

import asyncio
from bleak import BleakClient

# Hardcode MAC Address, Characteristics
MAC = "81:23:45:67:89:BA"
TX_CHAR = "0000fff2-0000-1000-8000-00805f9b34fb"  # Send commands
RX_CHAR = "0000fff1-0000-1000-8000-00805f9b34fb"  # Receive responses

response_data = []

# Incoming notifications
def notification_handler(sender, data):
    global response_data
    response_data.append(data)

async def send_obd2_command(client, command):
    """Send OBD2 command and wait for response"""
    global response_data
    response_data.clear()
    
    # Send command as bytes
    await client.write_gatt_char(TX_CHAR, bytes.fromhex(command))
    
    # Wait for response
    await asyncio.sleep(3)
    
    # Process response
    if response_data:
        # Combine all notification data
        full_response = b''.join(response_data)
        ascii_response = full_response.decode('ascii', errors='ignore').strip()
        print(ascii_response)
    else:
        print("No response")

async def main():
    #command = sys.argv[1] if len(sys.argv) > 1 else "30313043300d"  # Default: RPM
    command = "415445300d"
    async with BleakClient(MAC) as client:
        # Enable notifications
        await client.start_notify(RX_CHAR, notification_handler)
        
        # Send command
        await send_obd2_command(client, command)
        
        # Stop notifications
        await client.stop_notify(RX_CHAR)

if __name__ == "__main__":
    asyncio.run(main())