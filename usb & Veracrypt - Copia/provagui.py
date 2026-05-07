from guizero import App, Box, Text, TextBox, PushButton, ListBox
app = App()

title_box = Box(app, width="fill", align="top", border=True)
Text(title_box, text="title")

status_box = Box(app, align="top", width="fill", border=True)
Text(status_box, text="Contenuto", align="left", width="fill")
succ = PushButton(status_box, text="Next", align="right")

content_box = Box(app, align="top", width="fill", border=True)
Text(content_box, text="Parametri USB-KEY", width="fill")
usb_box = Box(content_box, layout="grid", width="fill", align="top", border=True)
Text(usb_box, grid=[0,1], text="ID", align="left")
TextBox(usb_box, grid=[1,1], text="data", width="fill")
Text(usb_box, grid=[2,1], text="Drive Utilizzato", align="left")
TextBox(usb_box, grid=[3,1], text="D:", width="fill")
ok1 = PushButton(usb_box, grid=[5,1], text="Carica", align="right",width="fill")

contenuto_box = Box(app, align="top", width="fill", border=True)
listafile=ListBox(contenuto_box,width="fill", align="top")

buttons_box = Box(app, width="fill", align="bottom", border=True)
cancel = PushButton(buttons_box, text="Cancel", align="right")
ok = PushButton(buttons_box, text="OK", align="right")



#form_box = Box(content_box, layout="grid", width="fill", align="left", border=True)
#Text(form_box, grid=[0,0], text="form", align="right")
#Text(form_box, grid=[0,1], text="label", align="left")
#TextBox(form_box, grid=[1,1], text="data", width="fill")

app.display()
