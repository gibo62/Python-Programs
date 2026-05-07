#import string
#import cryptocode
import wmi
import os
import base64
#from cryptography.fernet import Fernet
import hashlib
import subprocess
import time
import uuid
#from cryptography.hazmat.primitives import hashes
#from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

#from cryptdecrypt import crypt,decrypt

macAddress = str(hex(uuid.getnode()))

def verify_usb(drive,Chiave):
    f = open(f'{drive}\\volume.id',"rb")
    drive_id=f.read()
    f.close()
    return (decrypt(drive_id,Chiave))

def print_and_press(testo):
    print (testo)
    input ("premi un tasto per continuare.....")



  
drive_list=[]
drive_listold=[]
descrizione_list=[]
serialnumber_list=[]
print_and_press("Assicurati che la USB-KEY NON sia presente")
c = wmi.WMI ()
for drive in c.Win32_LogicalDisk ():
    # prints all the drives details including name, type and size
    drive_listold.append(drive.deviceid)
print_and_press("Inserisci la USB-KEY desiderata")
time.sleep(10)
for drive in c.Win32_LogicalDisk ():
    # prints all the drives details including name, type and size
    drive_list.append(drive.deviceid)
    descrizione_list.append(drive.description)
    serialnumber_list.append(drive.volumeserialnumber)
list_difference = []
for element in drive_list:
    if element not in drive_listold:
        list_difference.append(element)

if len(list_difference) == 0:
    print_and_press("USB KEY NON valida!!!!")
    quit()

usb_id = serialnumber_list[drive_list.index(list_difference[0])]  
drive=chr(ord(list_difference[0][0])+1)

#if verify_usb(list_difference[0],masterkey1+masterkey2) != usb_id:
#    print_and_press("USB KEY non riconosciuta!!!!")
#    quit()
#print (drive)

password = base64.b64encode(hashlib.sha512(str(usb_id).encode('UTF-8')).hexdigest().encode("utf-8"))
cmd = f'"C:\Program Files\VeraCrypt\VeraCrypt.exe" /v "{list_difference[0]}\\nomefile.vc" /l {drive} /m rm /p {str(password[:128],"utf-8")} /q /s /e'
print ("individuata USB-KEY ID: "+usb_id+" in drive: "+list_difference[0])
while True:
    scelta = input('Premere S per confermare operazione ')
    if scelta=="":
        continue
    else:
        break
if scelta.upper()=="S":
    shellcmd = subprocess.Popen(cmd, shell=True)
    while shellcmd.poll() == None:
        print (".",end="")
        time.sleep(5)
        
    print (shellcmd.returncode)
    if shellcmd.returncode != 0:
        print_and_press ("Operazione non conclusa")
    else:   
        print (f'USB-KEY ID: {usb_id} montata in drive: {drive}')
        input ("premi un tasto quando devi togliere la USB-KEY")
        cmd = f'"C:\Program Files\VeraCrypt\VeraCrypt.exe" /d /q /s'
        shellcmd = subprocess.Popen(cmd, shell=True)
        while shellcmd.poll() == None:
            print (".",end="")
            time.sleep(5)
        print_and_press ("operazione completata")
else:
    print_and_press ("azione cancellata")
    









    
    
