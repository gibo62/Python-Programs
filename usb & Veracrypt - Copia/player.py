import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pyAesCrypt
import os
import wmi
import subprocess
import threading
import tempfile
import uuid
import time

BUFFER_SIZE = 64 * 1024

class StealthPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("USB Secure Player")
        self.root.geometry("400x250")
        
        tk.Label(root, text="Riproduzione Sicura da USB", font=("Arial", 10, "bold")).pack(pady=10)
        self.btn_file = tk.Button(root, text="Seleziona File .aes", command=self.select_file)
        self.btn_file.pack(pady=10)
        
        self.progress = ttk.Progressbar(root, length=300, mode="determinate")
        self.progress.pack(pady=20)
        
        self.status = tk.Label(root, text="Pronto", fg="gray")
        self.status.pack()

    def find_usb_data(self):
        try:
            c = wmi.WMI()
            for disk in c.Win32_DiskDrive(InterfaceType="USB"):
                serial = disk.SerialNumber.strip()
                for part in disk.associators("Win32_DiskDriveToDiskPartition"):
                    for log in part.associators("Win32_LogicalDiskToPartition"):
                        return serial, log.DeviceID
        except: return None, None
        return None, None

    def select_file(self):
        f = filedialog.askopenfilename(filetypes=[("AES files", "*.aes")])
        if f:
            serial, drive_letter = self.find_usb_data()
            if not serial:
                messagebox.showerror("Errore", "Chiavetta USB non rilevata")
                return
            threading.Thread(target=self.process, args=(f, serial, drive_letter)).start()

    def process(self, file_path, pwd, drive):
        # Percorso offuscato in Temp con nome casuale
        temp_path = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
        # Percorso specifico richiesto: VLCPortable\VLCPortable.exe
        vlc_path = os.path.join(drive, "VLCPortable", "VLCPortable.exe")

        try:
            self.status.config(text="Decrittografia stealth...", fg="orange")
            pyAesCrypt.decryptFile(file_path, temp_path, pwd, BUFFER_SIZE)
            self.progress['value'] = 100
            
            if os.path.exists(vlc_path):
                self.status.config(text="In riproduzione...", fg="green")
                # Avvia VLCPortable e aspetta la chiusura
                subprocess.run([vlc_path, temp_path, "--play-and-exit", "vlc://quit"], check=True)
            else:
                messagebox.showerror("Errore", f"VLC non trovato in: {vlc_path}")
        except Exception as e:
            messagebox.showerror("Errore", "Chiave USB non valida o file corrotto")
        finally:
            if os.path.exists(temp_path):
                time.sleep(1.5) # Tempo per rilascio file
                try: os.remove(temp_path)
                except: pass
            self.status.config(text="Sessione terminata. File temporaneo rimosso.", fg="gray")
            self.progress['value'] = 0

if __name__ == "__main__":
    root = tk.Tk()
    StealthPlayer(root)
    root.mainloop()
