#import string
#import cryptocode
import wmi
import os
import base64
from cryptography.fernet import Fernet
import hashlib
import subprocess
import time
from datetime import datetime
import uuid
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

macAddress = str(hex(uuid.getnode()))
macAddress = (macAddress[3:]+"KTrVM5KjLb3jfoi9sTymXD4NUojaLpWhYwo2kT43GuD=")[:43]+"="
path1="C:\\Users\\Default\\AppData\\Local\\Microsoft\\Windows\\Shell\\"
path2="C:\ProgramData\\"

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

def crea_id(drive_id, drive):
    f = open(f'{drive}\\volume.id',"wb")
    f.write(crypt(drive_id,masterkey1+masterkey2[44:]))
    f.close()

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

try:
    masterkey1=decrypt(open(path1+"1.new", "rb").read(),macAddress)
    masterkey2=decrypt(open(path2+"2.new", "rb").read(),macAddress)
    print (type(masterkey1),masterkey1)
except:
    print("Sistema non riconosciuto")
    quit()
    
drive_list=[]
drive_listold=[]
descrizione_list=[]
serialnumber_list=[]
size_list=[]
size_usb=[]
usb_id=[]
capacity=[]
cmd=[]
shellcmd=[]
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
    size_list.append(drive.Freespace)
list_difference = []
for element in drive_list:
    if element not in drive_listold:
        list_difference.append(element)
        usb_id.append(serialnumber_list[drive_list.index(element)])
        if (int(size_list[drive_list.index(element)])//1073741824) > 0:
            size_usb.append(str(int(size_list[drive_list.index(element)])//1073741824)+"G")
        elif (int(size_list[drive_list.index(element)])//1048576) > 0:
            size_usb.append(str(int(size_list[drive_list.index(element)])//1048576)+"M")
        elif (int(size_list[drive_list.index(element)])//1024) > 0:
            size_usb.append(str(int(size_list[drive_list.index(element)])//1024)+"K")
print (list_difference,len(list_difference))
print (usb_id,len(usb_id))                      
#usb_id = serialnumber_list[drive_list.index(list_difference[0])]
primo_drive=chr(ord(list_difference[len(list_difference)-1][0])+1)
print (primo_drive)
for i, drive_vera in enumerate(list_difference):
    capacita=input(f'Drive: {drive_vera} Capacità da creare ({size_usb[i]})? ')
    if (capacita == ""):
        capacity.append(size_usb[i])
    else:
        capacity.append(capacita)
    password = base64.b64encode(hashlib.sha512(str(usb_id[i]+masterkey1+masterkey2).encode('UTF-8')).hexdigest().encode("utf-8"))
    cmd.append(f'"C:\Program Files\VeraCrypt\VeraCrypt Format.exe" /create "{list_difference[i]}\\nomefile.vc" /filesystem exfat /size "{capacity[i]}" /password {str(password[:128],"utf-8")} /keyfile "{path1}1." /keyfile "{path2}2." /quick /fastcreatefile /silent')
    print ("individuata USB-KEY ID: "+usb_id[i]+" in drive: "+list_difference[i]+" capacità: "+capacity[i])
#    print ("\n"+cmd[i])
#exit()
start = datetime.now()
scelta=input("vuoi procedere?")
if scelta=="S" or scelta=="s":
    print ("Attendere la crittografia della USB-KEY")
    for i, drive_vera in enumerate(list_difference):
        crea_id(usb_id[i],list_difference[i])
        shellcmd.append(subprocess.Popen(cmd[i], shell=True))
        count=0
    for i, drive_vera in enumerate(list_difference):    
        while shellcmd[i].poll() == None:
            count=count+1
            #print (drive_vera,count,shellcmd[i].poll())
            print (".", end='')
            time.sleep(5)
        print (drive_vera,shellcmd[i].returncode)
        if shellcmd[i].returncode != 0:
            print (f'\nDrive: {drive_vera} Operazione non conclusa')
        else:   
            print (f'\nDrive: {drive_vera} fatto')
else:
    print ("azione cancellata")
delta = datetime.now() - start
diff=int(delta.total_seconds())
diff_ore=int(diff/3600)
diff_minuti=int((diff-diff_ore*3600)/60)
diff_secondi=int((diff-diff_ore*3600-diff_minuti*60))
print("Tempo di elaborazione (hh:mm:ss): {:02}:{:02}:{:02}".format(diff_ore,diff_minuti,diff_secondi))









    
    
