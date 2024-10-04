import asyncio
from bleak import BleakClient, BleakScanner
from contextlib import suppress

char_uuid = "0000fff4-0000-1000-8000-00805f9b34fb"

def status_cb(char, data):
    # grams = int.from_bytes(data[3:5], byteorder="little") * (-1 if data[2] == 1 else 1)
    # units = ['', '', '', '', 'g', 'lboz', 'oz', 'ml', 'ml milk', 'floz', 'floz milk'][data[8]]
    # stable = data[9] == 0

    print(f"{char.handle} ({char.uuid}) -> 0x{bytes(data).hex()} (len: {len(data)})")
    # print(f"g: {grams}, unit: {units}, stable: {stable}")

def machine_cb(char, data):
    # grams = int.from_bytes(data[3:5], byteorder="little") * (-1 if data[2] == 1 else 1)
    # units = ['', '', '', '', 'g', 'lboz', 'oz', 'ml', 'ml milk', 'floz', 'floz milk'][data[8]]
    # stable = data[9] == 0

    print(f"{char.handle} ({char.uuid}) -> 0x{bytes(data).hex()} (len: {len(data)})")
    # print(f"g: {grams}, unit: {units}, stable: {stable}")


def training_cb(char, data):
    print(f"{char.handle} ({char.uuid}) -> 0x{bytes(data).hex()} (len: {len(data)})")

def mystery_cb(char, data):
    print(f"{char.handle} ({char.uuid}) -> 0x{bytes(data).hex()} (len: {len(data)})")


async def main():
    # ble_devices = await BleakScanner.discover(timeout=3, return_adv=True)
    # print(f"Found {len(ble_devices)} Devices:")
    # print(f"{'RSSI':<4} | {'ADDRESS':<17} | NAME")
    # for [dev, adv] in ble_devices.values():
    #     print(f"{adv.rssi:>4} | {dev.address:<17} | {adv.local_name if adv.local_name else ''}")


    print(f"Scanning for Walkingpad")
    scale_device = None
    while scale_device is None:
        scale_device = await BleakScanner.find_device_by_name("KS-HD-Z1D", timeout=1)

    print(f"Connecting to Scale ({scale_device.address})")

    async with BleakClient(scale_device) as client:
        while not client.is_connected:
            pass
        print(f"Connected!")

        # await client.pair()
        print(f"Paired!")

        for service in sorted(client.services, key=lambda x: x.handle):
            print(f"├┬─ {service.description:<96} [service - handle: {service.handle}, uuid: {service.uuid}]")
            for char in sorted(service.characteristics, key=lambda x: x.handle):
                val = ""
                if 'read' in char.properties:
                    data = await client.read_gatt_char(char)
                    val = f"0x{bytes(data).hex()}, {repr(bytes(data).decode(errors='replace'))}, {len(data)}"

                print(f"│├┬─ {f'{char.description:<31}{val}':<95} [characteristic - prop: {char.properties}, handle: {char.handle}, uuid: {char.uuid}]")
                for desc in sorted(char.descriptors, key=lambda x: x.handle):
                    data = await client.read_gatt_descriptor(desc.handle)
                    val = f"0x{bytes(data).hex()}, {repr(bytes(data).decode(errors='replace'))}, {len(data)}"
                    print(f"││├── {f'{service.description:<30}{val}':<94} [descriptor - handle: {desc.handle}, uuid: {desc.uuid}]")

        # current status
        notify1 = await client.start_notify(22, status_cb)
        notify2 = await client.start_notify(19, machine_cb)
        notify3 = await client.start_notify(25, training_cb)
        notify4 = await client.start_notify(50, mystery_cb)

        # count down
        await client.write_gatt_char(34, bytearray([0x00]))
        await client.write_gatt_char(34, bytearray([0x07]))
        await asyncio.sleep(100)

        # # set speed
        # await client.write_gatt_char(34, bytearray([0x00]))
        # await client.write_gatt_char(34, bytearray([0x02, 0x0a, 0x00]))
        # await asyncio.sleep(5)

        #         # set speed
        # await client.write_gatt_char(34, bytearray([0x00]))
        # await client.write_gatt_char(34, bytearray([0x02, 0x08, 0x00]))
        # await asyncio.sleep(5)

        #         # set speed
        # await client.write_gatt_char(34, bytearray([0x00]))
        # await client.write_gatt_char(34, bytearray([0x02, 0x04, 0x00]))
        # await asyncio.sleep(5)

        # turn off
        await client.write_gatt_char(34, bytearray([0x00]))
        await client.write_gatt_char(34, bytearray([0x08, 0x02]))
        await asyncio.sleep(5)

        exit()

        await asyncio.sleep(1)


        while(client.is_connected):
            await asyncio.sleep(5)

    print("Disconnected")


asyncio.run(main())