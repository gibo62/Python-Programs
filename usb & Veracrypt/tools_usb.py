from guizero import App, PushButton, Text, Box, ListBox, ButtonGroup, TextBox
import os
import hashlib
import time
import wmi
import base64
from cryptography.fernet import Fernet
import subprocess


c = wmi.WMI()
path1="C:\\Users\\Default\\AppData\\Local\\Microsoft\\Windows\\Shell\\"
path2="C:\ProgramData\\"
try:
    masterkey1 = open(path1+"1.", "r").read()
    masterkey2 = open(path2+"2.", "r").read()
    
except:
    print_and_press("Sistema non riconosciuto")
    quit()

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
    
def azzera_usb():
    #print ("azzerausb")
    global drive_list
    global drive_listold
    global descrizione_list
    global serialnumber_list
    drive_list = []
    drive_listold = []
    descrizione_list = []
    serialnumber_list = []
    #print ("inizializzazione variabili")
    for drive in c.Win32_LogicalDisk():
        #print (drive.deviceid)
        drive_listold.append(drive.deviceid)
    #print (drive_listold)


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
        aggiorna_Text_Stato("verificare che la USB-KEY sia disinserita")
        return  
    drive_usb = list_difference[0]
    #print (list_difference[0])     
    usb_id = serialnumber_list[drive_list.index(list_difference[0])]
    if verify_usb(drive_usb) != usb_id:
        aggiorna_Text_Stato("USB-KEY NON RICONOSCIUTA!!!!! TOGLIERLA")
        usb_id="N/A"
        return
    drive_vera = chr(ord(list_difference[0][0])+1)
    password = base64.b64encode(hashlib.sha512(str(usb_id+masterkey1+masterkey2).encode('UTF-8')).hexdigest().encode("utf-8"))
    #password = base64.b64encode(password.encode("utf-8"))

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
        Button_Next2.hide()
        Button_Next.show()
    else:
        aggiorna_Text_Stato("")
        Text_Usb_Id.value=usb_id
        Text_Drive_Usb.value=drive_usb
        creausb_box1.show()
        box2.show()
        Button_Carica.show() 

def Button_Ok_Click():
    Button_Carica.hide()
    if Listbox_Contenuto.value != None:
        cmd = f'"%ProgramFiles(x86)%\Windows Media Player\wmplayer.exe" /prefetch:1 /fullscreen "{drive_vera}:\\{Listbox_Contenuto.value}"'
        #print (cmd)
        os.popen(cmd)
        app.destroy()
    else:
        aggiorna_Text_Stato("Effettuare una scelta!!")
        Text_Stato.show()
        
def Button_Ok_Scelta_Click():
    if choice.value_text == "Creazione USB-KEY":
        creazione_usb_key()
    elif choice.value_text == "Gestione USB-KEY":
        gestione_usb_key()
    elif choice.value_text == "Censimento PC":
        censimento_pc()

def creazione_usb_key():
    main_box.hide()
    insert_creausb_box1.hide()
    avanti_creausb_box1.show()
    titolo_creausb_box1.value="Creazione USB-KEY"
    creausb_main_box1.show()
    app.update()
    global drive_list
    global drive_listold
    global descrizione_list
    global serialnumber_list
    drive_list=[]
    drive_listold=[]
    descrizione_list=[]
    serialnumber_list=[]
    stato_creausb_box1.value="Assicurati che non vi siano USB-KEY collegate"
    app.update()

def gestione_usb_key():
    main_box.hide()
    insert_montausb_box1.hide()
    avanti_montausb_box1.show()
    titolo_montausb_box1.value="Gestione USB-KEY"
    montausb_main_box1.show()
    app.update()
    global drive_list
    global drive_listold
    global descrizione_list
    global serialnumber_list
    drive_list=[]
    drive_listold=[]
    descrizione_list=[]
    serialnumber_list=[]
    stato_montausb_box1.value="Assicurati che non vi siano USB-KEY collegate"
    app.update()

def avanti_creausb_box1_Click():
    for drive in c.Win32_LogicalDisk ():
        # prints all the drives details including name, type and size
        drive_listold.append(drive.deviceid)
    stato_creausb_box1.value="Inserisci la USB-KEY desiderata"
    avanti_creausb_box1.hide()
    insert_creausb_box1.show()
    app.update()

def avanti_montausb_box1_Click():
    for drive in c.Win32_LogicalDisk ():
        # prints all the drives details including name, type and size
        drive_listold.append(drive.deviceid)
    stato_montausb_box1.value="Inserisci la USB-KEY desiderata"
    avanti_montausb_box1.hide()
    insert_montausb_box1.show()
    app.update()


def insert_creausb_box1_Click():
    global usb_id
    global drive
    global list_difference
    for drive in c.Win32_LogicalDisk ():
        # prints all the drives details including name, type and size
        drive_list.append(drive.deviceid)
        descrizione_list.append(drive.description)
        serialnumber_list.append(drive.volumeserialnumber)
        print (drive_list)

    list_difference = []
    for element in drive_list:
        if element not in drive_listold:
            list_difference.append(element)
    print (len(list_difference))
    if len(list_difference) !=0:
        usb_id = serialnumber_list[drive_list.index(list_difference[0])]
        drive=chr(ord(list_difference[0][0])+1)
        creausb_box1.hide()
        creausb_box2.show()
    else:
        creazione_usb_key()

def insert_montausb_box1_Click():
    global usb_id
    global drive
    global list_difference
    for drive in c.Win32_LogicalDisk ():
        # prints all the drives details including name, type and size
        drive_list.append(drive.deviceid)
        descrizione_list.append(drive.description)
        serialnumber_list.append(drive.volumeserialnumber)
        print (drive_list)

    list_difference = []
    for element in drive_list:
        if element not in drive_listold:
            list_difference.append(element)
    print (len(list_difference))
    if len(list_difference) !=0:
        usb_id = serialnumber_list[drive_list.index(list_difference[0])]
        drive=chr(ord(list_difference[0][0])+1)
        montausb_box1.hide()
        identifica_montausb_box2.value="USB-KEY ID: "+usb_id
        drive_montausb_box2.value="Drive: "+list_difference[0]
        montausb_box3.show()
        print("qui")
        app.update()
    else:
        gestione_usb_key()
        
def format_creausb_box2_Click():
    #print (drive)
    #capacity=input("Capacità da creare? ")
    identifica_creausb_box2.value="USB-KEY ID: "+usb_id
    drive_creausb_box2.value="Drive: "+list_difference[0]
    creausb_box2.hide()
    capacity_creausb_box3.value=f'Capacità: {capacity_creausb_box2.value}{tipo_creausb_box2.value_text[0]}'
    creausb_box3.show()
    app.update()
    
def conferma_creausb_box2_Click():
    #print ("Attendere la crittografia della USB-KEY")
    crea_id(usb_id,list_difference[0])
    password = base64.b64encode(hashlib.sha512(str(usb_id+masterkey1+masterkey2).encode('UTF-8')).hexdigest().encode("utf-8"))
    cmd =f'"C:\Program Files\VeraCrypt\VeraCrypt Format.exe" /create "{list_difference[0]}\\nomefile.vc" /filesystem exfat /size "{capacity_creausb_box2.value}{tipo_creausb_box2.value_text[0]}" /password {str(password[:128],"utf-8")} /keyfile "{path1}1." /keyfile "{path2}2." /quick /fastcreatefile /silent'
    print (cmd)
    shellcmd = subprocess.Popen(cmd, shell=True)
    Conferma_creausb_box2.value="Creazione Spazio Crittografato in corso: Attendere"
    app.update()
    count=0
    while shellcmd.poll() == None:
        count+=1
        Conferma_creausb_box2.value=Conferma_creausb_box2.value=f'Creazione Spazio Crittografato in corso: Attendere: {count}'
        app.update()
        time.sleep(5)
    #print (shellcmd.returncode)
    if shellcmd.returncode != 0:
        Conferma_creausb_box2.value="Operazione non riuscita"
        app.update()
    else:   
        Conferma_creausb_box2.value="Operazione completata"
        app.update()

def conferma_montausb_box2_Click():
    #print ("Attendere la crittografia della USB-KEY")
    password = base64.b64encode(hashlib.sha512(str(usb_id+masterkey1+masterkey2).encode('UTF-8')).hexdigest().encode("utf-8"))
    cmd =f'"C:\Program Files\VeraCrypt\VeraCrypt Format.exe" /create "{list_difference[0]}\\nomefile.vc" /filesystem exfat /size "{capacity_creausb_box2.value}{tipo_creausb_box2.value_text[0]}" /password {str(password[:128],"utf-8")} /keyfile "{path1}1." /keyfile "{path2}2." /silent'
    cmd = f'"C:\Program Files\VeraCrypt\VeraCrypt.exe" /v "{list_difference[0]}\\nomefile.vc" /l {chr(ord(list_difference[0][0])+1)} /m rm /p {str(password[:128],"utf-8")} /k "{path1}1." /k "{path2}2." /q /s /e'
    print (cmd)
    shellcmd = subprocess.Popen(cmd, shell=True)
    Conferma_montausb_box2.value="Apertura Spazio Crittografato in corso: Attendere"
    app.update()
    while shellcmd.poll() == None:
        Conferma_montausb_box2.value=Conferma_montausb_box2.value+"."
        app.update()
        time.sleep(5)
    #print (shellcmd.returncode)
    if shellcmd.returncode != 0:
        Conferma_montausb_box2.value=f'Operazione non riuscita'
        app.update()
    else:   
        Conferma_montausb_box2.value=f'Operazione Completata: Drive: {chr(ord(list_difference[0][0])+1)}'
        Rilascia_montausb_box2.show()
        Rilascia_montausb_button.show()    
        app.update()
        
def rilascia_montausb_box2_Click():
    #print ("Attendere la crittografia della USB-KEY")
    password = base64.b64encode(hashlib.sha512(str(usb_id+masterkey1+masterkey2).encode('UTF-8')).hexdigest().encode("utf-8"))
    cmd =f'"C:\Program Files\VeraCrypt\VeraCrypt Format.exe" /create "{list_difference[0]}\\nomefile.vc" /filesystem exfat /size "{capacity_creausb_box2.value}{tipo_creausb_box2.value_text[0]}" /password {str(password[:128],"utf-8")} /keyfile "{path1}1." /keyfile "{path2}2." /silent'
    cmd = f'"C:\Program Files\VeraCrypt\VeraCrypt.exe" /d /q /s /e'
    print (cmd)
    shellcmd = subprocess.Popen(cmd, shell=True)
    Rilascia_montausb_box2.value="Rilascio Spazio Crittografato in corso: Attendere"
    app.update()
    while shellcmd.poll() == None:
        Rilascia_montausb_box2.value=Rilascia_montausb_box2.value+"."
        app.update()
        time.sleep(5)
    #print (shellcmd.returncode)
    if shellcmd.returncode != 0:
        Rilascia_montausb_box2.value=f'Operazione non riuscita'
        app.update()
    else:   
        Rilascia_montausb_box2.value=f'Operazione Completata'
        app.update()   
    

def censimento_pc():
    print ("censimento pc")


def Button_Exit_Click():
    creausb_main_box1.hide()
    creausb_box2.hide()
    creausb_box3.hide()
    montausb_main_box1.hide()
    montausb_box3.hide()
    main_box.show()
    

def Button_Carica_Click():
    Button_Carica.hide()
    Button_Next2.hide()
    cmd = f'"C:\Program Files\VeraCrypt\VeraCrypt.exe" /v "{drive_usb}\\nomefile.vc" /l {drive_vera} /m rm /p {str(password[:128],"utf-8")} /k "{path1}1." /k "{path2}2." /q /s /e'
    #print (cmd)
    mesText_Stato = "attendere."
    aggiorna_Text_Stato(mesText_Stato)
    shellcmd = subprocess.Popen(cmd, shell=True)
    while shellcmd.poll() == None:
        mesText_Stato = mesText_Stato+"."
        aggiorna_Text_Stato(mesText_Stato)
        time.sleep(1)
    if shellcmd.returncode != 0:
        aggiorna_Text_Stato("Operazione non conclusa!!")
        Text_Stato.show()
    else:   
        entries = os.listdir(drive_vera+":/")
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
        box4.show()
        box3.show()
        Button_Ok.show()
    
    

app = App(title="Strumenti Amministrativi", width=530, height=400)
main_box = Box(app, width="fill")
choice = ButtonGroup(main_box, options=["Creazione USB-KEY", "Gestione USB-KEY", "Censimento PC"], selected="Creazione USB-KEY")
Button_Ok=PushButton(main_box, text="OK", align="right",padx=3,pady=3, width=10, command=Button_Ok_Scelta_Click)
Text(main_box, text="  ",align="right", width=1)
Button_Exit=PushButton(main_box, text="Exit", align="right",padx=3,pady=3, width=10,command=Button_Exit_Click)
Text(main_box, text="  ",align="right", width=3)

creausb_main_box1 = Box(app, align="top", width="fill",visible=False)
titolo_creausb_box1=Text(creausb_main_box1, text="Creazione USB-KEY", bg="#808080", width="fill", height=2,color="white")
creausb_box1 = Box(creausb_main_box1, align="top", width="fill",layout="grid")
stato_creausb_box1=Text(creausb_box1, text="Creazione USB-KEY", width=50, height=2, grid=[0,0])
avanti_creausb_box1=PushButton(creausb_box1, text="Avanti ->", align="right",padx=3,pady=3,width=8,command=avanti_creausb_box1_Click, grid=[1,0])
insert_creausb_box1=PushButton(creausb_box1, text="Avanti -->", align="right",padx=3,pady=3,width=8, command=insert_creausb_box1_Click, visible=False, grid=[1,0])

creausb_box2 = Box(app, align="top", width="fill",visible=False, layout="grid")
Text(creausb_box2, text="Capacità da creare:", grid=[0,0])
capacity_creausb_box2=TextBox(creausb_box2, grid=[1,0])
tipo_creausb_box2=ButtonGroup(creausb_box2, options=["MegaByte","GigaByte"], selected="GigaByte",grid=[2,0],width=20,align="left")
Format_creausb_box2=PushButton(creausb_box2, text="Crea", align="right",padx=3,pady=3,command=format_creausb_box2_Click,grid=[3,0], width=8)

creausb_box3 = Box(app, align="top", width="fill",visible=False, layout="grid")
identifica_creausb_box2=Text(creausb_box3, text="", grid=[0,1])
drive_creausb_box2=Text(creausb_box3, text="", grid=[1,1])
capacity_creausb_box3=Text(creausb_box3, text="", grid=[2,1])
Conferma_creausb_box2=Text(creausb_box3, text="Vuoi procedere alla creazione della USb-KEY?", grid=[0,2])
Conferma_creausb_button=PushButton(creausb_box3, text="Crea", align="right",padx=3,pady=3,command=conferma_creausb_box2_Click,grid=[1,2], width=8)

montausb_main_box1 = Box(app, align="top", width="fill",visible=False)
titolo_montausb_box1=Text(montausb_main_box1, text="Gestione USB-KEY", bg="#808080", width="fill", height=2,color="white")
montausb_box1 = Box(montausb_main_box1, align="top", width="fill",layout="grid")
stato_montausb_box1=Text(montausb_box1, text="Gestione USB-KEY", width=50, height=2, grid=[0,0])
avanti_montausb_box1=PushButton(montausb_box1, text="Avanti ->", align="right",padx=3,pady=3,width=8,command=avanti_montausb_box1_Click, grid=[1,0])
insert_montausb_box1=PushButton(montausb_box1, text="Avanti -->", align="right",padx=3,pady=3,width=8, command=insert_montausb_box1_Click, visible=False, grid=[1,0])

montausb_box3 = Box(app, align="top", width="fill",visible=False, layout="grid")
identifica_montausb_box2=Text(montausb_box3, text="", grid=[0,0])
drive_montausb_box2=Text(montausb_box3, text="", grid=[1,0])
capacity_montausb_box3=Text(montausb_box3, text="", grid=[2,0])
Conferma_montausb_box2=Text(montausb_box3, text="Vuoi procedere alla apertura di USb-KEY?", grid=[0,1],width=50)
Conferma_montausb_button=PushButton(montausb_box3, text="Apri", align="right",padx=3,pady=3,command=conferma_montausb_box2_Click,grid=[1,1], width=8)
Rilascia_montausb_box2=Text(montausb_box3, text="Premere il tasto Rilascia prima di togliere la USB-KEY", grid=[0,2],width=50,visible=False)
Rilascia_montausb_button=PushButton(montausb_box3, text="Rilascia", align="right",padx=3,pady=3,command=rilascia_montausb_box2_Click,grid=[1,2], width=8,visible=False)

box2 = Box(app, align="top", width="fill", layout="grid", visible=False)
Text(box2, text="USB ID:", width="fill",align="left",grid=[0,0])
Text_Usb_Id=Text(box2, text="pippo ", width=16, align="left",grid=[1,0], bg="white")
Text(box2, text="Drive ID:",width="fill", grid=[2,0])
Text_Drive_Usb=Text(box2, text="  ", width=16, align="left", bg="white",grid=[3,0])
Button_Carica=PushButton(box2, text="Carica", align="right",padx=3,pady=3,grid=[4,0],visible=False,command=Button_Carica_Click)

box4 = Box(app, align="top", width="fill",visible=False)
Text(box4, text="Contenuto USB-KEY", bg="#808080", width="fill", height=2,color="white")

box3 = Box(app, align="top", width="fill",visible=False)
Listbox_Contenuto = ListBox(box3, align="left", width=500, height=200)

box5 = Box(app, align="top", width="fill")
Button_Ok=PushButton(box5, text="OK", align="right",padx=3,pady=3, width=10, visible=False,command=Button_Ok_Click)
Text(box5, text="  ",align="right", width=1)
Button_Exit=PushButton(box5, text="Exit", align="right",padx=3,pady=3, width=10,command=Button_Exit_Click)
Text(box5, text="  ",align="right", width=3)
app.display()
