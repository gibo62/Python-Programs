import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pyAesCrypt
import os
import wmi
import threading
import io

BUFFER_SIZE = 128 * 1024  # 128KB per bilanciare velocità e fluidità barra

class ProgressWrapper(io.RawIOBase):
    """ Classe che 'spia' i byte letti per aggiornare la barra """
    def __init__(self, file_obj, total_size, update_callback):
        self.file_obj = file_obj
        self.total_size = total_size
        self.update_callback = update_callback
        self.bytes_read = 0

    def readinto(self, b):
        n = self.file_obj.readinto(b)
        if n:
            self.bytes_read += n
            # Calcola percentuale e invia alla GUI
            percentage = (self.bytes_read / self.total_size) * 100
            self.update_callback(percentage)
        return n

    def readable(self): return True

class EncryptorPro:
    def __init__(self, root):
        self.root = root
        self.root.title("AES Pro Encryptor (Real-Time)")
        self.root.geometry("450x380")
        
        self.file_path = ""
        self.dest_dir = ""
        
        # UI
        tk.Label(root, text="Crittografia File Multimediali", font=("Arial", 10, "bold")).pack(pady=10)
        
        tk.Button(root, text="1. Seleziona File", command=self.select_file).pack()
        self.lbl_file = tk.Label(root, text="...", fg="blue", wraplength=400)
        self.lbl_file.pack(pady=5)
        
        tk.Button(root, text="2. Seleziona Destinazione", command=self.select_dest).pack()
        self.lbl_dest = tk.Label(root, text="...", fg="green", wraplength=400)
        self.lbl_dest.pack(pady=5)
        
        # Progress Bar Reale
        self.progress_val = tk.DoubleVar()
        self.progress = ttk.Progressbar(root, length=350, variable=self.progress_val, maximum=100)
        self.progress.pack(pady=20)
        
        self.lbl_pct = tk.Label(root, text="0.0%")
        self.lbl_pct.pack()
        
        self.btn_run = tk.Button(root, text="AVVIA CRITTOGRAFIA", bg="#d1e7dd", height=2, width=20, command=self.start)
        self.btn_run.pack(pady=15)

    def update_bar(self, val):
        # Viene chiamato dal thread di crittografia per aggiornare la GUI
        self.progress_val.set(val)
        self.lbl_pct.config(text=f"Percentuale di Avanzamento Crittografia File: {val:.1f}%")
        self.root.update_idletasks()

    def get_usb_serial(self):
        try: return wmi.WMI().Win32_DiskDrive(InterfaceType="USB")[0].SerialNumber.strip()
        except: return None

    def select_file(self):
        self.file_path = filedialog.askopenfilename()
        if self.file_path:
            self.lbl_file.config(text=os.path.basename(self.file_path))
            if not self.dest_dir:
                self.dest_dir = os.path.dirname(self.file_path)
                self.lbl_dest.config(text=self.dest_dir)

    def select_dest(self):
        path = filedialog.askdirectory()
        if path:
            self.dest_dir = path
            self.lbl_dest.config(text=path)

    def start(self):
        usb_id = self.get_usb_serial()
        cryptokey="LcSFcf6tR4G^HW&uVwiBVe_Gn5HukvTm*@"+usb_id
        print (cryptokey)
        if not self.file_path or not self.dest_dir:
            messagebox.showerror("Errore", "Seleziona file e destinazione")
            return
        if not usb_id:
            messagebox.showerror("Errore", "Chiavetta USB non rilevata")
            return
        
        self.btn_run.config(state=tk.DISABLED)
        threading.Thread(target=self.run_logic, args=(cryptokey,)).start()

    def run_logic(self, pwd):
        try:
            file_size = os.path.getsize(self.file_path)
            out_path = os.path.join(self.dest_dir, os.path.basename(self.file_path) + ".aes")
            
            with open(self.file_path, "rb") as fIn:
                # Applichiamo il wrapper allo stream di input
                wrapped_fIn = ProgressWrapper(fIn, file_size, self.update_bar)
                
                with open(out_path, "wb") as fOut:
                    # pyAesCrypt ora legge attraverso il nostro wrapper
                    pyAesCrypt.encryptStream(wrapped_fIn, fOut, pwd, BUFFER_SIZE)
            
            messagebox.showinfo("Completato", "File crittografato al 100%!")
        except Exception as e:
            messagebox.showerror("Errore", str(e))
        finally:
            self.btn_run.config(state=tk.NORMAL)
            self.update_bar(0)

if __name__ == "__main__":
    root = tk.Tk()
    EncryptorPro(root)
    root.mainloop()
