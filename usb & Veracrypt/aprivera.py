#import string
#import cryptocode
import wmi
import os
import base64
from cryptography.fernet import Fernet
import hashlib
import subprocess
import time


def crea_id(drive_id, drive):
    key="KTrVM5KjLb3jfoi9sTymXD4NUojaLpWhYwo2kT43GuD="
    key=bytes(key,'utf-8')
    #print (key, len (key))
    cipher_suite = Fernet(key)
    cipher_text = cipher_suite.encrypt(bytes(drive_id,'utf-8'))
    plain_text = cipher_suite.decrypt(cipher_text)
    print(plain_text)
    print (str(cipher_text,'utf-8'))
    f = open(f'{drive}\\volume.id',"a")
    f.write(str(cipher_text,'utf-8'))
    f.close()
    

path1="C:\\Users\\Default\\AppData\\Local\\Microsoft\\Windows\\Shell\\"
path2="C:\ProgramData\\"
try:
    masterkey1 = open(path1+"1.", "r").read()
    masterkey2 = open(path2+"2.", "r").read()
    
except:
    print("Sistema non riconosciuto")
    quit()
    
drive_list=[]
drive_listold=[]
descrizione_list=[]
serialnumber_list=[]
input ("Assicurati che la USB-KEY NON sia presente")
c = wmi.WMI ()
for drive in c.Win32_LogicalDisk ():
    # prints all the drives details including name, type and size
    drive_listold.append(drive.deviceid)
input ("Inserisci la USB-KEY desiderata")
for drive in c.Win32_LogicalDisk ():
    # prints all the drives details including name, type and size
    drive_list.append(drive.deviceid)
    descrizione_list.append(drive.description)
    serialnumber_list.append(drive.volumeserialnumber)
list_difference = []
for element in drive_list:
    if element not in drive_listold:
        list_difference.append(element)

usb_id = serialnumber_list[drive_list.index(list_difference[0])]

drive=chr(ord(list_difference[0][0])+1)
print (drive)
capacity=input("Capacità da creare? ")
password = base64.b64encode(hashlib.sha512(str(usb_id+masterkey1+masterkey2).encode('UTF-8')).hexdigest().encode("utf-8"))
 
cmd =f'"C:\Program Files\VeraCrypt\VeraCrypt Format.exe" /create "{list_difference[0]}\\nomefile.vc" /filesystem exfat /size "{capacity}" /password {str(password[:128],"utf-8")} /keyfile "{path1}1." /keyfile "{path2}2." /silent'

print ("individuata USB-KEY ID: "+usb_id+" in drive: "+list_difference[0])
print ("\n"+cmd)
scelta=input("vuoi procedere?")
if scelta=="S" or scelta=="s":
    print ("Attendere la crittografia della USB-KEY")
    crea_id(usb_id,list_difference[0])
    shellcmd = subprocess.Popen(cmd, shell=True)
    count=0
    while shellcmd.poll() == None:
        count=count+1
        print (count,shellcmd.poll())
        time.sleep(5)
        
    print (shellcmd.returncode)
    if shellcmd.returncode != 0:
        print ("Operazione non conclusa")
    else:   
        print ("fatto")
else:
    print ("azione cancellata")
    









    
    
