from bluepy.btle import DefaultDelegate
from utilities.btle_device import BluetoothDevice

class ScanDelegate(DefaultDelegate):
    """
    ScanDelegate class handles discovery of new bluetooth devices with the Scanner object
    """

    i = 1

    def __init__(self, saved_devices, discovered_devices):
        """
        Init initialises lists of devices that new/saved are to be appended to
        """
        DefaultDelegate.__init__(self)
        self.saved_devices = saved_devices
        self.discovered_devices = discovered_devices

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            flag = False
            #if not self.named_devices:
            if not self.saved_devices:
                print("[%d] New device detected %s" % (ScanDelegate.i, dev.addr))
                new_device = BluetoothDevice(ScanDelegate.i, dev.addr, self.saved_devices)
                self.discovered_devices.append(new_device)
            else:
                for device in self.saved_devices:
                    if device == dev.addr:
                        flag = True

                if flag:
                    bt_dev = BluetoothDevice(dev.addr, ScanDelegate.i, self.saved_devices)
                    self.discovered_devices.append(bt_dev.getDevice(dev.addr))
                else:
                    print("[%d] New device detected %s" % (ScanDelegate.i, dev.addr))
                    new_device = BluetoothDevice(ScanDelegate.i, dev.addr, self.saved_devices)
                    self.discovered_devices.append(new_device)
            
            ScanDelegate.i += 1


class ScanDelegateTracking(DefaultDelegate):

    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData): pass
