import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pyAesCrypt
import os
import threading
import wmi  # Libreria per ottenere l'ID della chiavetta su Windows

BUFFER_SIZE = 64 * 1024

class USBApp:
    def __init__(self, root):
        self.root = root
        self.root.title("USB Hardware Lock - AES256")
        self.root.geometry("500x300")
        
        self.file_path = ""
        self.usb_id = None
        
        tk.Label(root, text="Crittografia tramite ID USB", font=("Arial", 16)).pack(pady=10)
        
        self.btn_select = tk.Button(root, text="Seleziona File", command=self.select_file)
        self.btn_select.pack(pady=5)
        
        self.lbl_file = tk.Label(root, text="Nessun file selezionato", fg="blue")
        self.lbl_file.pack(pady=5)
        
        self.lbl_usb = tk.Label(root, text="Stato USB: In attesa...", fg="red")
        self.lbl_usb.pack(pady=10)
        
        self.progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=10)
        
        frame_btns = tk.Frame(root)
        frame_btns.pack(pady=10)
        
        self.btn_enc = tk.Button(frame_btns, text="Crittografa", command=lambda: self.process("enc"), bg="#d1e7dd")
        self.btn_enc.pack(side=tk.LEFT, padx=10)
        
        self.btn_dec = tk.Button(frame_btns, text="Decrittografa", command=lambda: self.process("dec"), bg="#f8d7da")
        self.btn_dec.pack(side=tk.LEFT, padx=10)

    def select_file(self):
        self.file_path = filedialog.askopenfilename()
        if self.file_path:
            self.lbl_file.config(text=os.path.basename(self.file_path))

    def get_usb_serial(self):
        """Recupera il numero di serie della prima chiavetta USB trovata."""
        try:
            c = wmi.WMI()
            # Cerca dischi rimovibili (DriveType 2)
            for disk in c.Win32_DiskDrive(InterfaceType="USB"):
                # Restituisce il SerialNumber hardware univoco
                return disk.SerialNumber.strip()
        except Exception:
            return None
        return None

    def process(self, mode):
        self.usb_id = self.get_usb_serial()
        
        if not self.file_path:
            messagebox.showwarning("Errore", "Seleziona prima un file!")
            return
        
        if not self.usb_id:
            self.lbl_usb.config(text="USB NON TROVATA!", fg="red")
            messagebox.showerror("Errore USB", "Inserisci la chiavetta USB che funge da chiave!")
            return
        
        self.lbl_usb.config(text=f"USB Rilevata: {self.usb_id[:15]}...", fg="green")
        
        # Disabilita bottoni e avvia thread
        self.btn_enc.config(state=tk.DISABLED)
        self.btn_dec.config(state=tk.DISABLED)
        
        if mode == "enc":
            threading.Thread(target=self.encrypt).start()
        else:
            threading.Thread(target=self.decrypt).start()

    def encrypt(self):
        try:
            output_file = self.file_path + ".aes"
            # L'ID USB viene usato come password
            pyAesCrypt.encryptFile(self.file_path, output_file, self.usb_id, BUFFER_SIZE)
            self.progress['value'] = 100
            messagebox.showinfo("Successo", "File crittografato usando l'ID USB!")
        except Exception as e:
            messagebox.showerror("Errore", f"Errore: {e}")
        finally:
            self.reset_ui()

    def decrypt(self):
        try:
            if not self.file_path.endswith(".aes"):
                raise ValueError("Seleziona un file .aes")
            
            output_file = self.file_path.replace(".aes", "")
            # L'ID USB deve coincidere con quello usato in crittografia
            pyAesCrypt.decryptFile(self.file_path, output_file, self.usb_id, BUFFER_SIZE)
            self.progress['value'] = 100
            messagebox.showinfo("Successo", "File decrittografato con successo!")
        except Exception:
            messagebox.showerror("Errore", "Chiavetta USB errata o file non valido.")
        finally:
            self.reset_ui()

    def reset_ui(self):
        self.progress['value'] = 0
        self.btn_enc.config(state=tk.NORMAL)
        self.btn_dec.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = USBApp(root)
    root.mainloop()
