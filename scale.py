import asyncio
from bleak import BleakClient, BleakScanner

char_uuid = "0000fff4-0000-1000-8000-00805f9b34fb"

def callback(char, data):
    grams = int.from_bytes(data[3:5], byteorder="little") * (-1 if data[2] == 1 else 1)
    units = ['', '', '', '', 'g', 'lboz', 'oz', 'ml', 'ml milk', 'floz', 'floz milk'][data[8]]
    stable = data[9] == 0

    # print(f"{char.handle} ({char.uuid}) -> 0x{bytes(data).hex()} (len: {len(data)})")
    print(f"g: {grams}, unit: {units}, stable: {stable}")


async def main():
    # ble_devices = await BleakScanner.discover(timeout=3, return_adv=True)
    # print(f"Found {len(ble_devices)} Devices:")
    # print(f"{'RSSI':<4} | {'ADDRESS':<17} | NAME")
    # for [dev, adv] in ble_devices.values():
    #     print(f"{adv.rssi:>4} | {dev.address:<17} | {adv.local_name if adv.local_name else ''}")


    print(f"Scanning for Scale")
    scale_device = None
    while scale_device is None:
        scale_device = await BleakScanner.find_device_by_name("Kitchen Scale", timeout=1)

    print(f"Connecting to Scale ({scale_device.address})")

    async with BleakClient(scale_device) as client:
        while not client.is_connected:
            pass
        print(f"Connected!")

        # for service in client.services:
        #     print(f"├┬─ {service.description:<32} [service - handle: {service.handle}, uuid: {service.uuid}]")
        #     for char in service.characteristics:
        #         # val = "Unknown"
        #         # if 'read' in char.properties:
        #         #     val = bytes(await client.read_gatt_char(char))
        #         print(f"│├┬─ {f'{char.description}':<31} [characteristic - prop: {char.properties}, handle: {char.handle}, uuid: {char.uuid}]")
        #         for desc in char.descriptors:
        #             # val = await client.read_gatt_descriptor(desc.handle)
        #             print(f"││├── {f'{service.description}':<30} [descriptor - handle: {desc.handle}, uuid: {desc.uuid}]")


        await asyncio.sleep(1)
        notify = await client.start_notify(char_uuid, callback)


        while(client.is_connected):
            await asyncio.sleep(5)

    print("Disconnected")


asyncio.run(main())