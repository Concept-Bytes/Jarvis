import asyncio
from kasa import Discover, SmartPlug

async def main():
    # Discover devices
    print("Discovering devices...")
    devices = await Discover.discover()
    
    if not devices:
        print("No devices found")
        return
    
    # Print all discovered devices
    for addr, dev in devices.items():
        print(f"Found {dev} at {addr}")

    # Use the IP address of the first discovered device
    for addr, dev in devices.items():
        plug = SmartPlug(addr)
        await plug.update()
        
        # Debugging: Print available attributes
        print(dir(plug))
        
        # Correctly accessing the state
        print(f"Alias: {plug.alias}")
        print(f"Is on: {plug.is_on}")
        
        # Turn the plug on
        await plug.turn_on()
        print(f"Turned on {plug.alias}")

        await asyncio.sleep(5)  # Keep it on for 5 seconds

        # Turn the plug off
        await plug.turn_off()
        print(f"Turned off {plug.alias}")
        break  # Exit after controlling the first device

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
