from bluepy.btle import Scanner, DefaultDelegate
from utilities.btle_device import BluetoothDevice
from utilities.btle_delegate import ScanDelegate, ScanDelegateTracking

discovered_devices = []

class BluetoothUnlock():
    """
    Class scans and tracks bluetooth devices through a ScanDelegate and ScanDelegateTracker
    providing the MAC address of bluetooth devices to be saved in MP
    """
    def __init__(self, saved_devices):
        self.saved_devices = saved_devices

    def scanTracking(self, selected_device, scanTracker):
        """
        ScanTracking function tracks the signals of devices in checks if any saved
        devices are in the area and gives the signal strength
        Returns:
            True - if saved device is discovered
        """

        print("Scanning...")
        stop = False

        while stop is False:
            for n in range(7):
                devices = scanTracker.scan(4.0)
                for dev in devices:
                    if selected_device != None:
                        if dev.addr == selected_device.mac_addr:
                            print("Selected device detected. RSSI=%d dB\n" % (dev.rssi))
                            return True
                    else:
                        for saved in self.saved_devices:
                            if dev.addr == saved:
                                print("Saved device detected. RSSI=%d dB\n" % (dev.rssi))
                                return True
            return False

    def trackSaved(self, scanTracker):
        """
        TrackSaved keeps track of the saved devices and bypasses the registration
        of a new device if one is found in ScanDevices much like scanTracking but
        with with different print statements.
        Arguments:
            scanTracker {ScanDelegateTracker} -- scanner object with ScanDelegateTracking as delegate 
        Returns:
            True - if saved device is discovered
            False - if saved device is NOT discovered
        """
        selected_device = None
        discovered = scanTracker.scan(4.0)
        for saved in self.saved_devices:
            #print(saved + " saved")
            for dis in discovered:
                #print(dis.addr + " discovered")
                if dis.addr == saved:
                    return self.scanTracking(selected_device, scanTracker)

        return False

    def scanDevices(self):
        """
        ScanDevices runs instances of ScanDelegate and it's HandleDiscovery function
        to handle the discovery of new devices to be registered for auto login.
        Returns:
            Bool - True or False determined by scanTracking
        """
        scanTracker = Scanner().withDelegate(ScanDelegateTracking())
        self.trackSaved(scanTracker)

        scan_delegate = ScanDelegate(self.saved_devices, discovered_devices)
        scanner = Scanner().withDelegate(scan_delegate)
        scanner.scan(4.0)#how long to scan for in seconds
        selected_device = None
        
        for saved in self.saved_devices:
            for discovered in discovered_devices:
                if discovered == saved:
                    return self.scanTracking(selected_device, scanTracker)     

        saved = False
        selected_number = input("Select device number: ")
        
        for device in discovered_devices:
            if int(device.number) == int(selected_number):
                selected_device = device
                self.saved_devices.append(selected_device.mac_addr)
                print("Device saved.")

        for device in self.saved_devices:
            if selected_device == device:
                # print("Device" + device + "found.")
                saved = True

        if not saved:
            self.saved_devices.append(selected_device.mac_addr)

        return self.scanTracking(selected_device, scanTracker)

    def getSavedDevices(self):
        """
        Returns:
            saved_devices - list of mac address as strings
        """
        return self.saved_devices             
            