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
import glob

BUFFER_SIZE = 64 * 1024

class StealthPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("USB Stealth Player")
        self.root.geometry("500x300")
        
        self.usb_serial = ""
        self.usb_drive = ""
        
        tk.Label(root, text="Riproduzione Sicura da USB", font=("Arial", 12, "bold")).pack(pady=10)
        
        self.lbl_info = tk.Label(root, text="Ricerca file sulla USB...", fg="blue")
        self.lbl_info.pack(pady=5)
        
        self.progress_val = tk.DoubleVar()
        self.progress = ttk.Progressbar(root, length=400, variable=self.progress_val, maximum=100)
        self.progress.pack(pady=20)
        
        self.status = tk.Label(root, text="In attesa...", fg="gray")
        self.status.pack()

        # Avvio automatico della logica di scansione
        self.root.after(500, self.auto_scan_or_choose)

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

    def auto_scan_or_choose(self):
        serial, drive = self.find_usb_data()
        if not serial:
            messagebox.showerror("Errore", "Chiavetta USB non rilevata!")
            self.root.destroy()
            return
        
        self.usb_serial = "LcSFcf6tR4G^HW&uVwiBVe_Gn5HukvTm*@"+serial
        self.usb_drive = drive
        # Cerca i file .aes nella root della chiavetta
        aes_files = glob.glob(os.path.join(drive, "*.aes"))

        if len(aes_files) == 1:
            # Un solo file trovato: procedi automaticamente
            selected_file = aes_files[0]
            self.lbl_info.config(text=f"File trovato: {os.path.basename(selected_file)}")
            threading.Thread(target=self.process, args=(selected_file,)).start()
        else:
            # Più file o nessun file: chiedi all'utente
            self.lbl_info.config(text="Seleziona il file da riprodurre")
            self.manual_select()

    def manual_select(self):
        f = filedialog.askopenfilename(
            initialdir=self.usb_drive,
            title="Seleziona file crittografato",
            filetypes=[("AES files", "*.aes")]
        )
        if f:
            threading.Thread(target=self.process, args=(f,)).start()
        else:
            self.status.config(text="Nessun file selezionato.")

    def process(self, file_path):
        temp_path = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
        vlc_path = os.path.join(self.usb_drive, "VLCPortable", "VLCPortable.exe")

        try:
            self.status.config(text="Decrittografia in corso, attendere...", fg="orange")
            # Decrittazione (puoi usare la versione Pro con wrapper se desideri la barra millimetrica anche qui)
            pyAesCrypt.decryptFile(file_path, temp_path, self.usb_serial, BUFFER_SIZE)
            self.progress_val.set(100)
            
            if os.path.exists(vlc_path):
                self.status.config(text="In riproduzione...", fg="green")
                subprocess.run([vlc_path, temp_path, "--loop", "--fullscreen","--no-video-title-show"], check=True)
            else:
                messagebox.showerror("Errore", f"VLCPortable non trovato in {vlc_path}")
        except Exception:
            messagebox.showerror("Errore", "Chiave USB non valida o file corrotto.")
        finally:
            if os.path.exists(temp_path):
                try: os.remove(temp_path)
                except: pass
             # CHIUSURA TOTALE DEL PROGRAMMA
            self.status.config(text="Chiusura programma", fg="green")
            time.sleep(1.5)
            self.root.after(100, self.root.destroy)

if __name__ == "__main__":
    root = tk.Tk()
    StealthPlayer(root)
    root.mainloop()
