#import string
import cryptocode
import wmi
import os
from cryptography.fernet import Fernet

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
fernet=Fernet(passkey)

print (passkey)

message = 'la password per VeraCrypt'
encMessage = fernet.encrypt(message.encode())
 
print("original string: ", message)
print("encrypted string: ", encMessage)

message = 'la password per VeraCrypt'
encMessage = fernet.encrypt(message.encode())
 
print("original string: ", message)
print("encrypted string: ", encMessage)


str_encoded = cryptocode.encrypt(str1,passkey)
print (str_encoded)
print (cryptocode.decrypt(str_encoded,passkey))
str_encoded = cryptocode.encrypt(str1,passkey)
print (str_encoded)
print (cryptocode.decrypt(str_encoded,passkey))

encoded_data = base64.b64encode(passkey)
print (encoded_data)


print("Encoded text with base 64 is")
print(encoded_data)
cmd ='"C:\Program Files\VeraCrypt\VeraCrypt Format.exe" /create '+list_difference[0]+"\\nomefile.vc"+' /size "200M" /password '+str_encoded+' /encryption AES /hash sha-512 /filesystem exfat /pim 0 /silent'
print (cmd)






    
    
