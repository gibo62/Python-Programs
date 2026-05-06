#import string
#import cryptocode
import wmi
import os
import subprocess
import base64
import time
from guizero import App, Text, TextBox, Box, PushButton, ListBox


c = wmi.WMI()

def azzera_usb():
    global drive_list
    global drive_listold
    global descrizione_list
    global serialnumber_list
    drive_list=[]
    drive_listold=[]
    descrizione_list=[]
    serialnumber_list=[]
    for drive in c.Win32_LogicalDisk ():
        drive_listold.append(drive.deviceid)
        
def leggi_usb():
    global usb_id
    global drive_vera
    global password
    global drive_usb
    for drive in c.Win32_LogicalDisk ():
        drive_list.append(drive.deviceid)
        descrizione_list.append(drive.description)
        serialnumber_list.append(drive.volumeserialnumber)
    list_difference = []
    for element in drive_list:
        if element not in drive_listold:
            list_difference.append(element)
    if len(list_difference) == 0:
        usb_id="N/A"
        return       
    usb_id = serialnumber_list[drive_list.index(list_difference[0])]
    drive_vera=chr(ord(list_difference[0][0])+1)
    password = base64.b64encode(usb_id.encode("utf-8"))
    drive_usb=list_difference[0]
    return 

def change_message(message):
    message_text.value = message

def clicked_the_button1():
    button1.hide()
    azzera_usb()
    
    change_message("Inserire USB-KEY")
    button2.show()
 #   app.after(2000, message3)

def clicked_the_button2():
    button2.hide()
    leggi_usb()
    if usb_id== "N/A":
        change_message("Togliere USB-KEY")
        button1.show()
    else:
        change_message("individuata USB-KEY ID: "+usb_id+" in drive: "+drive_usb)
        button3.show()
 #   app.after(2000, message3)
 
def clicked_the_button3():
    button3.hide()
    cmd ='"C:\Program Files\VeraCrypt\VeraCrypt.exe" /v "'+drive_usb+"\\nomefile.vc"+'" /l '+drive_vera+' /m ro /p '+str(password)+ ' /q /s'
    print (cmd)
    comando=os.popen(cmd)
    while  True:
        try:
            entries = os.listdir(drive_vera+":/")
            break
        except:
 #           print(".",end="")
            time.sleep(1)
    for i in range(len(entries)):
        listafile.insert(i,entries[i])
    listafile.show()
    
 
app = App(layout="grid")

message_text = Text(app, text = "togliere USB-KEY", align="left",grid=[0,0])
button1 = PushButton(app, clicked_the_button1, text = "Next", align="left",grid=[1,0])
button2 = PushButton(app, clicked_the_button2, text = "Next", align="left",grid=[1,0])
button3 = PushButton(app, clicked_the_button3, text = "Next", align="left",grid=[1,0])
listafile=ListBox(app,width="fill", align="top",grid=[0,1])
button2.hide()
button3.hide()
app.display()

    









    
    
