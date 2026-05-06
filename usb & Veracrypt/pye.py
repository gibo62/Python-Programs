from guizero import App, PushButton, Text, Box, ListBox
import os
import hashlib
import time
import wmi
import base64

c = wmi.WMI()
path1="C:\\Users\\Default\\AppData\\Local\\Microsoft\\Windows\\Shell\\"
path2="C:\ProgramData\\"
try:
    masterkey1 = open(path1+"1.", "r").read()
    masterkey2 = open(path2+"2.", "r").read()
    
except:
    print("Sistema non riconosciuto")
    quit()
    
def azzera_usb():
    print ("azzerausb")
    global drive_list
    global drive_listold
    global descrizione_list
    global serialnumber_list
    drive_list = []
    drive_listold = []
    descrizione_list = []
    serialnumber_list = []
    print ("inizializzazione variabili")
    for drive in c.Win32_LogicalDisk():
        print (drive.deviceid)
        drive_listold.append(drive.deviceid)
    print (drive_listold)


def aggiorna_Text_Stato(messaggio):
    Text_Stato.value=messaggio
    app.update()
    
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
    print (list_difference[0])     
    usb_id = serialnumber_list[drive_list.index(list_difference[0])]
    drive_vera = chr(ord(list_difference[0][0])+1)
    password = base64.b64encode(hashlib.sha512(str(usb_id+masterkey1+masterkey2).encode('UTF-8')).hexdigest().encode("utf-8"))
    #password = base64.b64encode(password.encode("utf-8"))
    drive_usb = list_difference[0]
    return 

def Button_Next_click():
    Button_Next.hide()
    aggiorna_Text_Stato("Inserire la USB-KEY")
    azzera_usb()
    Button_Next2.show()

def Button_Next2_click():
    Button_Next.hide()
    Button_Next2.hide()    
    leggi_usb()
    if usb_id == "N/A":
        aggiorna_Text_Stato("verificare che la USB-KEY sia disinserita")
        Button_Next2.hide()
        Button_Next.show()
    else:
        aggiorna_Text_Stato("")
        Text_Usb_Id.value=usb_id
        Text_Drive_Usb.value=drive_usb
        top_box1.show()
        top_box2.show()
        Button_Carica.show() 

def Button_Ok_Click():
    Button_Carica.hide()
    cmd = f'"%ProgramFiles(x86)%\Windows Media Player\wmplayer.exe" /prefetch:1 /fullscreen "{drive_vera}:\\{Listbox_Contenuto.value}"'
    print (cmd)
    os.popen(cmd)
    app.destroy()
    

def Button_Exit_Click():
    app.destroy()
    

def Button_Carica_Click():
    Button_Carica.hide()
    Button_Next2.hide()
    cmd = f'"C:\Program Files\VeraCrypt\VeraCrypt.exe" /v "{drive_usb}\\nomefile.vc" /l {drive_vera} /m rm /p {str(password[:128],"utf-8")} /k "{path1}1." /k "{path2}2." /q /s /e'
    print (cmd)
    mesText_Stato = "attendere."
    aggiorna_Text_Stato(mesText_Stato)
    os.popen(cmd)
    
    while True:
        print (mesText_Stato)
        try:
            mesText_Stato = mesText_Stato+"."
            aggiorna_Text_Stato(mesText_Stato)
            entries = os.listdir(drive_vera+":/")
            break
        except:
            mesText_Stato = mesText_Stato+"."
            aggiorna_Text_Stato(mesText_Stato)
            time.sleep(1)
    for i in range(len(Listbox_Contenuto.items)):
        Listbox_Contenuto.remove(0)    

    indice = 0
    for i in range(len(entries)):
        if "RECYCLE.BIN" not in entries[i] and "System Volume Information" not in entries[i]:
            Listbox_Contenuto.insert(indice, entries[i])
            indice = indice+1
    aggiorna_Text_Stato("")
    Text_Stato.hide()
    Button_Carica.hide()
    top_box4.show()
    top_box3.show()
    Button_Ok.show()
    
    

app = App(title="Ora la stiamo provando", width=530, height=400)
top_box = Box(app, width="fill",height=35,layout="grid")
Text_Stato=Text(top_box, text="Assicurarsi che la USb-KEY sia disinserita", align="left", bg="white", width=47, grid=[0,0])
Button_Next=PushButton(top_box, text="Successivo ->", align="right",padx=3,pady=3,grid=[1,0], command=Button_Next_click)
Button_Next2=PushButton(top_box, text="Successivo -->", align="right",padx=3,pady=3,grid=[1,0],visible=False,command=Button_Next2_click)

top_box1 = Box(app, align="top", width="fill",visible=False)
Text(top_box1, text="parametri usb-key", bg="#808080", width="fill", height=2,color="white")

top_box2 = Box(app, align="top", width="fill", layout="grid", visible=False)
Text(top_box2, text="USB ID:", width="fill",align="left",grid=[0,0])
Text_Usb_Id=Text(top_box2, text="pippo ", width=16, align="left",grid=[1,0], bg="white")
Text(top_box2, text="Drive ID:",width="fill", grid=[2,0])
Text_Drive_Usb=Text(top_box2, text="  ", width=16, align="left", bg="white",grid=[3,0])
Button_Carica=PushButton(top_box2, text="Carica", align="right",padx=3,pady=3,grid=[4,0],visible=False,command=Button_Carica_Click)

top_box4 = Box(app, align="top", width="fill",visible=False)
Text(top_box4, text="Contenuto USB-KEY", bg="#808080", width="fill", height=2,color="white")

top_box3 = Box(app, align="top", width="fill",visible=False)
Listbox_Contenuto = ListBox(top_box3, align="left", width=500, height=200)

top_box5 = Box(app, align="top", width="fill")
Button_Ok=PushButton(top_box5, text="OK", align="right",padx=3,pady=3, width=10, visible=False,command=Button_Ok_Click)
Text(top_box5, text="  ",align="right", width=1)
Button_Exit=PushButton(top_box5, text="Exit", align="right",padx=3,pady=3, width=10,command=Button_Exit_Click)
Text(top_box5, text="  ",align="right", width=1)
app.display()
