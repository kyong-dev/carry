

class BluetoothDevice:
    """
    BluetoothDevice class creates the BluetoothDevice object
    used to identify which MAC address to register
    """

    def __init__(self, dev, number, named_devices = []):
        self.dev = dev
        self.number = number
        self.name = "default"
        self.named_devices = named_devices

    def __init__(self, number, mac_addr, saved_devices = []):
        self.number = number
        self.mac_addr = mac_addr
        self.saved_devices = saved_devices

    def setName(self, name):
        self.name = name

    def setNumber(self, number):
        self.number = number

    def getDevice(self, mac_addr):
        #for device in self.named_devices:
        for device in self.saved_devices:
            if device == mac_addr:
                return device