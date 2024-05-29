import asyncio
from kasa import Discover, SmartPlug

# Global variable to store the plug
plug1 = None

async def init_smart_plug():
    global plug1
    devices = await Discover.discover()
    if not devices:
        print("No devices found")
        return
    for addr, dev in devices.items():
        await dev.update()
        if dev.alias == "TP-LINK_Smart Plug_95EF":
            plug1 = dev
            break

    if plug1:
        print(f"Found plug: {plug1.alias}")
    else:
        print("Specific plug not found")

async def parse_command(command):
    global plug1
    if not plug1:
        print("Plug not initialized")
        return
    
    if command == "light1-on":
        await plug1.turn_on()
        print("Turning on the light")
    elif command == "light1-off":
        await plug1.turn_off()
        print("Turning off the light")
    elif command == "exit-program":
        print("Exiting program")
        exit()
    else:
        print("Invalid command")
