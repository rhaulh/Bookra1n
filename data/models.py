class DeviceInfo:
    pair: str = None
    name: str = None
    model: str = None
    ios: str = None
    serial: str = None
    udid: str = None
    imei: str = None
    region: str = None
    guid:str = None
    authorized:bool = False
    activated:bool = False

class DeviceCleanInfo(DeviceInfo):
    name="N/A"
    serial="N/A"
    ios="N/A"
    imei="N/A"
    model="N/A"
    pair="Disconnected"
    authorized=False

class DeviceBasicConnectionInfo(DeviceInfo):
    pair = "Limited"
    name="Unknown"
    serial="Unknown"
    ios="Unknown"
    model="Unknown"
    imei="Unknown"
    pair="Disconnected"
    authorized=False