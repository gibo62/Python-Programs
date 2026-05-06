import win32com.client
wmi = win32com.client.GetObject("winmgmts:")

for usb in wmi.InstancesOf("Win32_UsbHub"):
    print ('DeviceID: ' + str(usb.DeviceID))
    
for usb in wmi.InstancesOf ("Win32_UsbController"):
    print ('Manufacturer: ' + str(usb.Manufacturer))
