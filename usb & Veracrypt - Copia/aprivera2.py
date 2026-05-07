#import string
#import cryptocode

import os
import subprocess
import base64
import time
import wmi
from guizero import App, Text, TextBox, Box, PushButton, ListBox


c = wmi.WMI()

def azzera_usb():
    global drive_list
    global drive_listold
    global descrizione_list
    global serialnumber_list
    drive_list = []
    drive_listold = []
    descrizione_list = []
    serialnumber_list = []
    for drive in c.Win32_LogicalDisk():
        drive_listold.append(drive.deviceid)
        

def leggi_usb():
    global usb_id
    global drive_vera
    global password
    global drive_usb
    for drive in c.Win32_LogicalDisk():
        drive_list.append(drive.deviceid)
        descrizione_list.append(drive.description)
        serialnumber_list.append(drive.volumeserialnumber)
    list_difference = []
    for element in drive_list:
        if element not in drive_listold:
            list_difference.append(element)
    if len(list_difference) == 0:
        usb_id = "N/A"
        return       
    usb_id = serialnumber_list[drive_list.index(list_difference[0])]
    drive_vera = chr(ord(list_difference[0][0])+1)
    password = base64.b64encode(usb_id.encode("utf-8"))
    drive_usb = list_difference[0]
    return 


def change_message(message):
    message_text.value = message
    app.update()


def clicked_the_button1():
    button1.hide()
    azzera_usb()
    
    change_message("Inserire USB-KEY")
    button2.show()
#   app.after(2000, message3)


def clicked_the_ok_button():
    print (listafile.value)

def clicked_the_button2():
    button2.hide()
    leggi_usb()
    if usb_id == "N/A":
        change_message("Togliere USB-KEY")
        button1.show()
    else:
        change_message("")
        idusb.value = usb_id
        driveusb.value = drive_usb
        ok1.show()
#   app.after(2000, message3)
 

def clicked_the_button3():
    ok1.hide()
    cmd = f'"C:\Program Files\VeraCrypt\VeraCrypt.exe" /v "{drive_usb}\\nomefile.vc" /l {drive_vera} /m ro /p {password} /q /s'
    print (cmd)
    messtato = "attendere."
    change_message(messtato)
    os.popen(cmd)
    
    while True:
        try:
            messtato = messtato+"."
            change_message(messtato)
            entries = os.listdir(drive_vera+":/")
            break
        except:
            messtato = messtato+"."
            change_message(messtato)
            
            time.sleep(1)
    indice = 0
    for i in range(len(entries)):
        if "RECYCLE.BIN" not in entries[i] and "System Volume Information" not in entries[i]:
            listafile.insert(indice, entries[i])
            indice = indice+1
    listafile.show()
    change_message("")
   
 
app = App(width=600)


title_box = Box(app, align="top", border=False, width="fill")
Text(title_box, text="Status")

status_box = Box(title_box, align="top", width="fill", border=False, layout="grid", height=70)
Text(status_box, text="", align="left", grid=[0, 0], height=1, width=50)
message_text = Text(status_box, text="togliere USB-KEY", align="left", grid=[0, 1], height=1,bg="white", width=50)
Text(status_box, text="", align="left", grid=[2, 1], height=1, width=1)
button1 = PushButton(status_box, clicked_the_button1, text="Next", align="right", grid=[3, 1], padx=1, pady=1)
button2 = PushButton(status_box, clicked_the_button2, text="Next", align="left", grid=[3, 1], padx=1, pady=1)
Text(status_box, text="", align="left", grid=[0, 2], height=1, width=50)
button2.hide()


content_box = Box(app, align="top", width="fill", border=False)
Text(content_box, text="Parametri USB-KEY", width="fill", bg="gray")
Text(content_box, text="", width="fill")
usb_box = Box(content_box, layout="grid", width="fill", align="top", border=False, height=70)
Text(usb_box, grid=[0, 1], text="ID", align="bottom", width=20)
idusb = Text(usb_box, grid=[1, 1], text="     ", width=10, bg="white")
Text(usb_box, grid=[2, 1], text=" ", align="left", width=10)
Text(usb_box, grid=[3, 1], text="Drive Utilizzato", align="left")
driveusb = Text(usb_box, grid=[4, 1], text="    ", width=5, bg="white")
Text(usb_box, grid=[5, 1], text=" ", align="left")
ok1 = PushButton(usb_box, clicked_the_button3, grid=[6, 1], text="Carica", align="right", width="fill",padx=1, pady=1)
ok1.hide()

contenuto_box = Box(app, align="top", width="fill", border=False)
listafile = ListBox(contenuto_box, width="fill", align="top")

buttons_box = Box(app, width="fill", align="bottom", border=False)
cancel = PushButton(buttons_box, text="Cancel", align="right",padx=1, pady=1)
ok = PushButton(buttons_box, clicked_the_ok_button, text="OK", align="right",padx=1, pady=1)


app.display()

    









    
    
