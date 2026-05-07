import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pyAesCrypt
import os
import threading
import wmi
import subprocess
import time
import tempfile
import uuid

BUFFER_SIZE = 64 * 1024

class HiddenSecurePlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure Stealth Player")
        self.root.geometry("500x320")
        
        self.file_path = ""
        self.usb_drive_letter = ""
        
        tk.Label(root, text="Decrittazione Stealth e Play", font=("Arial", 12, "bold")).pack(pady=10)
        
        self.btn_select = tk.Button(root, text="Seleziona File .aes", command=self.select_file)
        self.btn_select.pack(pady=5)
        
        self.lbl_file = tk.Label(root, text="Nessun file selezionato", fg="blue")
        self.lbl_file.pack(pady=5)
        
        self.lbl_status = tk.Label(root, text="In attesa USB...", fg="gray")
        self.lbl_status.pack(pady=5)
        
        self.progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=15)
        
        frame_btns = tk.Frame(root)
        frame_btns.pack(pady=10)
        
        self.btn_enc = tk.Button(frame_btns, text="Crittografa", command=lambda: self.start_action("enc"), bg="#d1e7dd")
        self.btn_enc.pack(side=tk.LEFT, padx=10)
        
        self.btn_dec = tk.Button(frame_btns, text="Play Stealth", command=lambda: self.start_action("dec"), bg="#cfe2ff")
        self.btn_dec.pack(side=tk.LEFT, padx=10)

    def get_usb_info(self):
        try:
            c = wmi.WMI()
            for disk in c.Win32_DiskDrive(InterfaceType="USB"):
                serial = disk.SerialNumber.strip()
                for partition in disk.associators("Win32_DiskDriveToDiskPartition"):
                    for logical_disk in partition.associators("Win32_LogicalDiskToPartition"):
                        return serial, logical_disk.DeviceID
        except: return None, None
        return None, None

    def select_file(self):
        self.file_path = filedialog.askopenfilename()
        if self.file_path:
            self.lbl_file.config(text=os.path.basename(self.file_path))

    def start_action(self, mode):
        usb_id, drive_letter = self.get_usb_info()
        if not self.file_path or not usb_id:
            messagebox.showerror("Errore", "Verifica file e USB")
            return
        
        self.usb_drive_letter = drive_letter
        self.btn_enc.config(state=tk.DISABLED)
        self.btn_dec.config(state=tk.DISABLED)
        
        if mode == "enc":
            threading.Thread(target=self.encrypt, args=(usb_id,)).start()
        else:
            threading.Thread(target=self.decrypt_stealth, args=(usb_id,)).start()

    def encrypt(self, password):
        try:
            self.lbl_status.config(text="Crittografia...", fg="orange")
            pyAesCrypt.encryptFile(self.file_path, self.file_path + ".aes", password, BUFFER_SIZE)
            self.progress['value'] = 100
            messagebox.showinfo("OK", "File protetto.")
        except Exception as e:
            messagebox.showerror("Errore", str(e))
        finally: self.reset_ui()

    def decrypt_stealth(self, password):
        # Genera un percorso nascosto in Temp con nome casuale senza estensione
        temp_name = str(uuid.uuid4())
        temp_path = os.path.join(tempfile.gettempdir(), temp_name)
        
        try:
            self.lbl_status.config(text="Preparazione sicura...", fg="orange")
            
            # Decrittazione nello stream per sicurezza
            with open(self.file_path, "rb") as fIn:
                with open(temp_path, "wb") as fOut:
                    pyAesCrypt.decryptStream(fIn, fOut, password, BUFFER_SIZE)
            
            self.progress['value'] = 100
            
            # VLC dalla USB
            vlc_exe = os.path.join(self.usb_drive_letter, "VLCPortable","VLCPortable.exe")
            
            if os.path.exists(vlc_exe):
                self.lbl_status.config(text="Riproduzione stealth...", fg="green")
                # --play-and-exit: chiude VLC alla fine
                # --no-video-title-show: nasconde il nome del file casuale a video
                subprocess.run([vlc_exe, temp_path, "--play-and-exit", "--no-video-title-show", "vlc://quit"], check=True)
            else:
                messagebox.showerror("Errore", "VLC non trovato sulla USB")
                
        except Exception:
            messagebox.showerror("Errore", "Accesso negato o chiave USB errata")
        finally:
            if os.path.exists(temp_path):
                time.sleep(1)
                try:
                    os.remove(temp_path)
                except: pass
            self.reset_ui()

    def reset_ui(self):
        self.progress['value'] = 0
        self.lbl_status.config(text="Pronto", fg="gray")
        self.btn_enc.config(state=tk.NORMAL)
        self.btn_dec.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = HiddenSecurePlayer(root)
    root.mainloop()

