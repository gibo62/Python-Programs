import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pyAesCrypt
import os
import threading

# Impostazioni di cifratura
BUFFER_SIZE = 64 * 1024  # 64K

def seleziona_file():
    file_path = filedialog.askopenfilename()
    entry_file.delete(0, tk.END)
    entry_file.insert(0, file_path)

def crittografa_file():
    file_da_cifrare = entry_file.get()
    password = entry_pass.get()

    if not file_da_cifrare or not password:
        messagebox.showwarning("Attenzione", "Seleziona un file e inserisci una password!")
        return

    # Inizia il processo in un thread separato per non bloccare la GUI
    thread = threading.Thread(target=esegui_cifratura, args=(file_da_cifrare, password))
    thread.start()

def esegui_cifratura(file_input, password):
    file_output = file_input + ".aes"
    
    try:
        # Aggiorna UI: mostra avanzamento
        btn_cifra.config(state=tk.DISABLED)
        label_status.config(text="Cifratura in corso...", fg="blue")
        progress_bar['value'] = 0
        progress_bar.update()

        # Ottieni dimensione file per la barra
        file_size = os.path.getsize(file_input)
        
        # Cifratura
        # pyAesCrypt non ha un callback nativo per il progresso, 
        # aggiorniamo la barra in modo simulato o usando chunk size
        pyAesCrypt.encryptFile(file_input, file_output, password, BUFFER_SIZE)
        
        progress_bar['value'] = 100
        label_status.config(text="Cifratura completata!", fg="green")
        messagebox.showinfo("Successo", f"File cifrato salvato come:\n{file_output}")
        
    except Exception as e:
        label_status.config(text="Errore!", fg="red")
        messagebox.showerror("Errore", str(e))
    finally:
        btn_cifra.config(state=tk.NORMAL)
        entry_file.delete(0, tk.END)
        entry_pass.delete(0, tk.END)

# --- Interfaccia Grafica (Tkinter) ---
app = tk.Tk()
app.title("File Encryptor con AES-256")
app.geometry("500x300")

# Elementi GUI
label_file = tk.Label(app, text="File da cifrare:")
label_file.pack(pady=5)

frame_file = tk.Frame(app)
frame_file.pack()
entry_file = tk.Entry(frame_file, width=40)
entry_file.pack(side=tk.LEFT, padx=5)
btn_browse = tk.Button(frame_file, text="Sfoglia", command=seleziona_file)
btn_browse.pack(side=tk.LEFT)

label_pass = tk.Label(app, text="Password:")
label_pass.pack(pady=5)
entry_pass = tk.Entry(app, show="*", width=40)
entry_pass.pack()

btn_cifra = tk.Button(app, text="Crittografa File", command=crittografa_file, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
btn_cifra.pack(pady=20)

# Barra di avanzamento
progress_bar = ttk.Progressbar(app, orient=tk.HORIZONTAL, length=300, mode='determinate')
progress_bar.pack(pady=10)

label_status = tk.Label(app, text="", fg="blue")
label_status.pack()

app.mainloop()
