import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pyAesCrypt
import os
import threading
import wmi
import subprocess # Per eseguire VLC

BUFFER_SIZE = 64 * 1024
# Percorso tipico di VLC su Windows
VLC_PATH = r"C:\Program Files\VideoLAN\VLC\vlc.exe"

class USBCryptVLC:
    def __init__(self, root):
        self.root = root
        self.root.title("USB Crypto & Play")
        self.root.geometry("500x320")
        
        self.file_path = ""
        
        tk.Label(root, text="Crittografia USB + Auto-VLC", font=("Arial", 16)).pack(pady=10)
        
        self.btn_select = tk.Button(root, text="Seleziona File", command=self.select_file)
        self.btn_select.pack(pady=5)
        
        self.lbl_file = tk.Label(root, text="Nessun file selezionato", fg="blue")
        self.lbl_file.pack(pady=5)
        
        self.lbl_status = tk.Label(root, text="Pronto", fg="gray")
        self.lbl_status.pack(pady=5)
        
        self.progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=15)
        
        frame_btns = tk.Frame(root)
        frame_btns.pack(pady=10)
        
        self.btn_enc = tk.Button(frame_btns, text="Crittografa", command=lambda: self.start_action("enc"), bg="#d1e7dd")
        self.btn_enc.pack(side=tk.LEFT, padx=10)
        
        self.btn_dec = tk.Button(frame_btns, text="Decritta e Apri VLC", command=lambda: self.start_action("dec"), bg="#cfe2ff")
        self.btn_dec.pack(side=tk.LEFT, padx=10)

    def get_usb_serial(self):
        try:
            c = wmi.WMI()
            for disk in c.Win32_DiskDrive(InterfaceType="USB"):
                return disk.SerialNumber.strip()
        except: return None
        return None

    def select_file(self):
        self.file_path = filedialog.askopenfilename()
        if self.file_path:
            self.lbl_file.config(text=os.path.basename(self.file_path))

    def start_action(self, mode):
        usb_id = self.get_usb_serial()
        if not self.file_path:
            messagebox.showwarning("Errore", "Seleziona un file")
            return
        if not usb_id:
            messagebox.showerror("Errore", "Chiavetta USB non rilevata")
            return
        
        self.btn_enc.config(state=tk.DISABLED)
        self.btn_dec.config(state=tk.DISABLED)
        
        if mode == "enc":
            threading.Thread(target=self.encrypt, args=(usb_id,)).start()
        else:
            threading.Thread(target=self.decrypt, args=(usb_id,)).start()

    def encrypt(self, password):
        try:
            self.lbl_status.config(text="Crittografia in corso...", fg="orange")
            output_file = self.file_path + ".aes"
            pyAesCrypt.encryptFile(self.file_path, output_file, password, BUFFER_SIZE)
            self.progress['value'] = 100
            messagebox.showinfo("OK", "File crittografato!")
        except Exception as e:
            messagebox.showerror("Errore", str(e))
        finally:
            self.reset_ui()

    def decrypt(self, password):
        try:
            if not self.file_path.endswith(".aes"):
                messagebox.showerror("Errore", "Il file deve essere .aes")
                return
            
            self.lbl_status.config(text="Decrittografia in corso...", fg="orange")
            output_file = self.file_path.replace(".aes", "")
            
            pyAesCrypt.decryptFile(self.file_path, output_file, password, BUFFER_SIZE)
            self.progress['value'] = 100
            
            # Apertura con VLC
            if os.path.exists(VLC_PATH):
                self.lbl_status.config(text="Apertura VLC...", fg="green")
                subprocess.Popen([VLC_PATH, output_file])
            else:
                # Se VLC non è nel percorso standard, prova l'apertura di sistema
                os.startfile(output_file)
                
            messagebox.showinfo("Successo", "Decrittografato e avviato!")
        except Exception:
            messagebox.showerror("Errore", "Chiave USB non valida per questo file")
        finally:
            self.reset_ui()

    def reset_ui(self):
        self.progress['value'] = 0
        self.lbl_status.config(text="Pronto", fg="gray")
        self.btn_enc.config(state=tk.NORMAL)
        self.btn_dec.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = USBCryptVLC(root)
    root.mainloop()
