import os

os.system("color")

Usb = os.popen("wmic logicaldisk where drivetype=2 get description ,deviceid ,volumename").read()
print(Usb[1]
      )
input ("pause")

if Usb.find("DeviceID") != -1:
    print("\033[1;32mUsb is plugged")
    input("")

else:
    print("\033[0;31mUsb is not plugged")
    input("")
