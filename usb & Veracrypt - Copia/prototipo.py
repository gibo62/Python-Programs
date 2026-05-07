from guizero import App, PushButton, Text, Box, ListBox
import time


   



def aggiorna_Text_Stato(messaggio):
    Text_Stato.value=messaggio
    app.update()
    
def Button_Next_click():
    Button_Next.hide()
    aggiorna_Text_Stato("Inserire la USB-KEY")
    Button_Next2.show()

def Button_Next2_click():
    Button_Next.hide()
    Button_Next2.hide()    
    aggiorna_Text_Stato("")
    Text_Usb_Id.value="usb-id"
    Text_Drive_Usb.value="E:"
    top_box1.show()
    top_box2.show()
    Button_Carica.show() 

def Button_Ok_Click():
    Button_Carica.hide()
    app.destroy()
    

def Button_Exit_Click():
    app.destroy()
    

def Button_Carica_Click():
    Button_Carica.hide()
    Button_Next2.hide()
    mesText_Stato = "attendere."
    aggiorna_Text_Stato(mesText_Stato)
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
Listbox_Contenuto = ListBox(top_box3, items=["primo", "secondo","terzo","quarto"], align="left", width=500, height=200)

top_box5 = Box(app, align="top", width="fill")
Button_Ok=PushButton(top_box5, text="OK", align="right",padx=3,pady=3, width=10, visible=False,command=Button_Ok_Click)
Text(top_box5, text="  ",align="right", width=1)
Button_Exit=PushButton(top_box5, text="Exit", align="right",padx=3,pady=3, width=10,command=Button_Exit_Click)
Text(top_box5, text="  ",align="right", width=1)
app.display()
