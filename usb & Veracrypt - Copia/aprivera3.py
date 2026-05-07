import tkinter as tk
import tkinter.font as tkFont
import os
import hashlib
import time
import wmi
import base64

masterkey="la chiave master è questa"
pathplayer='"%ProgramFiles(x86)%\Windows Media Player\wmplayer.exe" /prefetch:1 /fullscreen'
c = wmi.WMI()


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


def aggiorna_stato(messaggio):
    global GLabel_1
    GLabel_1 ["text"] = messaggio
    GLabel_1.place(x=30,y=20,width=473,height=30)


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
    password = base64.b64encode(hashlib.sha512(str(usb_id+masterkey).encode('UTF-8')).hexdigest().encode("utf-8"))
    #password = base64.b64encode(password.encode("utf-8"))
    drive_usb = list_difference[0]
    return 

def GButton_1_command():
    GButton_2.place(x=520,y=20,width=70,height=25)
    GButton_1.place_forget()
    aggiorna_stato("Inserire la USB-KEY")
    print ("sonoqui")
    azzera_usb()


def GButton_2_command():
    leggi_usb()
    if usb_id == "N/A":
        aggiorna_stato("verificare che la USB-KEY sia disinserita")
        GButton_2.place_forget()
        GButton_1.place(x=520,y=20,width=70,height=25)
    else:
        aggiorna_stato("")
        GLabel_1.place(x=30,y=20,width=473,height=30)
        GLabel_2["text"] = usb_id
        GLabel_2.place(x=110,y=70,width=70,height=25)
        GLabel_3["text"] = drive_usb
        GLabel_3.place(x=320,y=70,width=70,height=25)
        GButton_5.place(x=520,y=70,width=70,height=25)
        GButton_2.place_forget()
   

def GButton_3_command():
    GButton_2.place_forget()
    cmd = f'"%ProgramFiles(x86)%\Windows Media Player\wmplayer.exe" /prefetch:1 /fullscreen "{drive_vera}:\\{GListBox_955.get(GListBox_955.curselection())}"'
    print (cmd)
    os.popen(cmd)
    root.destroy()
    

def GButton_4_command():
    root.destroy()
    

def GButton_5_command():
    GButton_5.place_forget()
    GButton_2.place_forget()
    cmd = f'"C:\Program Files\VeraCrypt\VeraCrypt.exe" /v "{drive_usb}\\nomefile.vc" /l {drive_vera} /m rm /p {password} /q /s /e'
    print (cmd)
    messtato = "attendere."
    aggiorna_stato(messtato)
    GButton_2.pack()
    GButton_2.place_forget()
    os.popen(cmd)
    
    while True:
        print (messtato)
        try:
            messtato = messtato+"."
            aggiorna_stato(messtato)
            entries = os.listdir(drive_vera+":/")
            break
        except:
            messtato = messtato+"."
            aggiorna_stato(messtato)
            time.sleep(1)
    for i in range(GListBox_955.index("end")):
        GListBox_955.delete(0)    

    indice = 0
    for i in range(len(entries)):
        if "RECYCLE.BIN" not in entries[i] and "System Volume Information" not in entries[i]:
            GListBox_955.insert(indice, entries[i])
            indice = indice+1
    GListBox_955.place(x=30,y=110,width=533,height=217)
    aggiorna_stato("")
    GButton_3.place(x=410,y=350,width=70,height=25)
    GButton_4.place(x=490,y=350,width=70,height=25)
    GButton_5.place_forget()


root = tk.Tk()
#setting title
root.title("undefined")
#setting window si
width=600
height=500
screenwidth = root.winfo_screenwidth()
screenheight = root.winfo_screenheight()
alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
root.geometry(alignstr)
root.resizable(width=False, height=False)

GLabel_1=tk.Label(root)
ft = tkFont.Font(family='Times',size=10)
GLabel_1["font"] = ft
GLabel_1["fg"] = "#333333"
GLabel_1["bg"] = "white"
GLabel_1["justify"] = "left"
GLabel_1["text"] = "verificare che la USB-KEY sia disinserita"
GLabel_1.place(x=30,y=20,width=473,height=30)


GLabel_2=tk.Label(root)
GLabel_2["borderwidth"] = "1px"
ft = tkFont.Font(family='Times',size=10)
GLabel_2["font"] = ft
GLabel_2["fg"] = "#333333"
GLabel_2["bg"] = "white"
GLabel_2["justify"] = "left"
GLabel_2["text"] = ""
GLabel_2.place(x=110,y=70,width=70,height=25)
GLabel_2.place_forget()



GButton_1=tk.Button(root)
GButton_1["bg"] = "#f0f0f0"
ft = tkFont.Font(family='Times',size=10)
GButton_1["font"] = ft
GButton_1["fg"] = "#000000"
GButton_1["justify"] = "center"
GButton_1["text"] = "Avanti ->"
GButton_1.place(x=520,y=20,width=70,height=25)
GButton_1["command"] = GButton_1_command


GButton_2=tk.Button(root)
GButton_2["bg"] = "#f0f0f0"
ft = tkFont.Font(family='Times',size=10)
GButton_2["font"] = ft
GButton_2["fg"] = "#000000"
GButton_2["justify"] = "center"
GButton_2["text"] = "Avanti -->"
GButton_2.place(x=520,y=20,width=70,height=25)
GButton_2["command"] = GButton_2_command
GButton_2.place_forget()

GListBox_955=tk.Listbox(root)
GListBox_955["borderwidth"] = "1px"
ft = tkFont.Font(family='Times',size=10)
GListBox_955["font"] = ft
GListBox_955["fg"] = "#333333"
GListBox_955["justify"] = "left"
GListBox_955.place(x=30,y=110,width=533,height=217)
GListBox_955.place_forget()

GButton_3=tk.Button(root)
GButton_3["bg"] = "#f0f0f0"
ft = tkFont.Font(family='Times',size=10)
GButton_3["font"] = ft
GButton_3["fg"] = "#000000"
GButton_3["justify"] = "center"
GButton_3["text"] = "OK"
GButton_3.place(x=410,y=350,width=70,height=25)
GButton_3["command"] = GButton_3_command
GButton_3.place_forget()

GButton_4=tk.Button(root)
GButton_4["bg"] = "#f0f0f0"
ft = tkFont.Font(family='Times',size=10)
GButton_4["font"] = ft
GButton_4["fg"] = "#000000"
GButton_4["justify"] = "center"
GButton_4["text"] = "Exit"
GButton_4.place(x=490,y=350,width=70,height=25)
GButton_4["command"] = GButton_4_command


GButton_5=tk.Button(root)
GButton_5["bg"] = "#f0f0f0"
ft = tkFont.Font(family='Times',size=10)
GButton_5["font"] = ft
GButton_5["fg"] = "#000000"
GButton_5["justify"] = "center"
GButton_5["text"] = "Carica"
GButton_5.place(x=520,y=70,width=70,height=25)
GButton_5["command"] = GButton_5_command
GButton_5.place_forget()


GLabel_2=tk.Label(root)
GLabel_2["borderwidth"] = "1px"
ft = tkFont.Font(family='Times',size=10)
GLabel_2["font"] = ft
GLabel_2["fg"] = "#333333"
GLabel_2["bg"] = "white"
GLabel_2["justify"] = "left"
GLabel_2["text"] = ""
GLabel_2.place(x=110,y=70,width=70,height=25)
GLabel_2.place_forget()

GLabel_3=tk.Label(root)
GLabel_3["borderwidth"] = "1px"
ft = tkFont.Font(family='Times',size=10)
GLabel_3["font"] = ft
GLabel_3["fg"] = "#333333"
GLabel_3["bg"] = "white"
GLabel_3["justify"] = "left"
GLabel_3["text"] = ""
GLabel_3.place(x=320,y=70,width=70,height=25)
GLabel_3.place_forget()

GLabel_615=tk.Label(root)
ft = tkFont.Font(family='Times',size=10)
GLabel_615["font"] = ft
GLabel_615["fg"] = "#333333"
GLabel_615["justify"] = "right"
GLabel_615["text"] = "USB-KEY ID:"
GLabel_615.place(x=20,y=70,width=70,height=25)

GLabel_755=tk.Label(root)
ft = tkFont.Font(family='Times',size=10)
GLabel_755["font"] = ft
GLabel_755["fg"] = "#333333"
GLabel_755["justify"] = "right"
GLabel_755["text"] = "Drive:"
GLabel_755.place(x=230,y=70,width=100,height=25)



    
root.mainloop()
