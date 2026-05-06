#import string
#import cryptocode
import wmi
import os
import base64
from cryptography.fernet import Fernet
import hashlib
import subprocess
import time
import uuid

def verify_usb(drive):
    key="KTrVM5KjLb3jfoi9sTymXD4NUojaLpWhYwo2kT43GuD="
    key=bytes(key,'utf-8')
    print (key, len (key))
    cipher_suite = Fernet(key)
    f = open(f'{drive}\\volume.id',"r")
    cipher_text=bytes(f.read(),'utf-8')
    f.close()
    return str(cipher_suite.decrypt(cipher_text),'utf-8')

def print_and_press(testo):
    print (testo)
    input ("premi un tasto per continuare.....")

macAddress = str(hex(uuid.getnode()))
macAddress = (macAddress[3:]+"KTrVM5KjLb3jfoi9sTymXD4NUojaLpWhYwo2kT43GuD=")[:43]+"="


def crypt(dacrittare,Chiave):
    key=bytes(Chiave,'utf-8')
    print ("key=",key, "dacrittare=",dacrittare)
    cipher_suite = Fernet(key)
    return (cipher_suite.encrypt(dacrittare.encode()))

def decrypt(dadecrittare,Chiave):
    key=bytes(Chiave,'utf-8')
    print ("key=",key,"dadecrittare=",dadecrittare)
    cipher_suite = Fernet(key)
    return (cipher_suite.decrypt(dadecrittare).decode())

path1="C:\\Users\\Default\\AppData\\Local\\Microsoft\\Windows\\Shell\\"
path2="C:\ProgramData\\"
try:
#    key1 = open(path1+"1.new", "rb").read()
#    key2 = open(path2+"2.new", "rb").read()
#    print (key1,key2)
    masterkey1=decrypt(open(path1+"1.new", "rb").read(),macAddress)
    masterkey2=decrypt(open(path2+"2.new", "rb").read(),macAddress)
    print (masterkey1)
    print (masterkey2)
except:
    print_and_press("Sistema non riconosciuto")
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
#if verify
if verify_usb(list_difference[0]) != usb_id:
    print_and_press("USB KEY non riconosciuta!!!!")
    quit()
print (drive)
password = base64.b64encode(hashlib.sha512(str(usb_id+masterkey1+masterkey2).encode('UTF-8')).hexdigest().encode("utf-8"))
cmd = f'"C:\Program Files\VeraCrypt\VeraCrypt.exe" /v "{list_difference[0]}\\nomefile.vc" /l {drive} /m rm /p {str(password[:128],"utf-8")} /k "{path1}1." /k "{path2}2." /q /s /e'
print ("individuata USB-KEY ID: "+usb_id+" in drive: "+list_difference[0])
print ("\n"+cmd)
scelta=input("vuoi procedere?")
if scelta=="S" or scelta=="s":
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
    









    
    
