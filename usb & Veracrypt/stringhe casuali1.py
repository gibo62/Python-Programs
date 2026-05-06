#import string
#import cryptocode
import wmi
import os
import base64

DRIVE_TYPES = {
  0 : "Unknown",
  1 : "No Root Directory",
  2 : "Removable Disk",
  3 : "Local Disk",
  4 : "Network Drive",
  5 : "Compact Disc",
  6 : "RAM Disk"
}

drive_list=[]
drive_listold=[]
descrizione_list=[]
serialnumber_list=[]
c = wmi.WMI ()
for drive in c.Win32_LogicalDisk ():
    # prints all the drives details including name, type and size
    drive_listold.append(drive.deviceid)
print (drive_listold)
input ("ora metti la penna")
for drive in c.Win32_LogicalDisk ():
    # prints all the drives details including name, type and size
    drive_list.append(drive.deviceid)
    descrizione_list.append(drive.description)
    serialnumber_list.append(drive.volumeserialnumber)
list_difference = []
for element in drive_list:
    if element not in drive_listold:
        list_difference.append(element)

passkey = serialnumber_list[drive_list.index(list_difference[0])]
encode = base64.b64encode(passkey.encode("utf-8"))

cmd ='"C:\Program Files\VeraCrypt\VeraCrypt Format.exe" /create '+list_difference[0]+"\\nomefile.vc"+' /size "200M" /password '+str(encode)+' /encryption AES /hash sha-512 /filesystem exfat /pim 0 /silent'
print ("individuata USB-KEY ID: "+passkey+" in drive: "+list_difference[0])
scelta=input("vuoi procedere alla creazione area crittografata?")
if scelta=="S" or scelta=="s":
    shellcmd = os.popen(cmd)
    print ("fatto")
else:
    print ("azione cancellata")
    









    
    
