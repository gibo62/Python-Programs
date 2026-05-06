import win32com.client
def get_usb_device():
    try:
        usb_list = []
        wmi = win32com.client.GetObject("winmgmts:")
        for usb in wmi.InstancesOf("Win32_USBHub"):
            if 'archiviazione' in usb.description:
                usb_list.append(usb.deviceid)

        print(usb_list)
        return usb_list
    except Exception as error:
        print('error', error)


get_usb_device()
