import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pyAesCrypt
import os
import threading
import wmi
import subprocess

BUFFER_SIZE = 64 * 1024
# Percorso standard di VLC
#VLC_PATH = r"C:\Program Files\VideoLAN\VLC\vlc.exe"
VLC_PATH = r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe"
class SecurePlayApp:
    def __init__(self, root):
        self.root = root
        self.root.title("USB Secure Player")
        self.root.geometry("500x320")
        
        self.file_path = ""
        
        tk.Label(root, text="USB Crypto: Decritta, Riproduci e Elimina", font=("Arial", 12, "bold")).pack(pady=10)
        
        self.btn_select = tk.Button(root, text="1. Seleziona File", command=self.select_file)
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
        
        self.btn_dec = tk.Button(frame_btns, text="Riproduci (Auto-Delete)", command=lambda: self.start_action("dec"), bg="#cfe2ff")
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
            messagebox.showerror("Errore", "Chiavetta USB non trovata!")
            return
        
        self.btn_enc.config(state=tk.DISABLED)
        self.btn_dec.config(state=tk.DISABLED)
        
        if mode == "enc":
            threading.Thread(target=self.encrypt, args=(usb_id,)).start()
        else:
            threading.Thread(target=self.decrypt_and_play, args=(usb_id,)).start()

    def encrypt(self, password):
        try:
            self.lbl_status.config(text="Crittografia in corso...", fg="orange")
            output_file = self.file_path + ".aes"
            pyAesCrypt.encryptFile(self.file_path, output_file, password, BUFFER_SIZE)
            self.progress['value'] = 100
            messagebox.showinfo("Successo", f"File salvato come:\n{os.path.basename(output_file)}")
        except Exception as e:
            messagebox.showerror("Errore", str(e))
        finally:
            self.reset_ui()

    def decrypt_and_play(self, password):
        temp_file = ""
        try:
            if not self.file_path.endswith(".aes"):
                messagebox.showerror("Errore", "Seleziona un file .aes")
                return
            
            self.lbl_status.config(text="Decrittografia...", fg="orange")
            temp_file = self.file_path.replace(".aes", "")
            
            # 1. Decrittazione
            pyAesCrypt.decryptFile(self.file_path, temp_file, password, BUFFER_SIZE)
            self.progress['value'] = 100
            
            # 2. Avvio VLC e attesa chiusura
            if os.path.exists(VLC_PATH):
                self.lbl_status.config(text="Riproduzione in corso (Attesa chiusura)...", fg="green")
                # subprocess.run blocca l'esecuzione del thread finché VLC non viene chiuso
                subprocess.run([VLC_PATH, temp_file, "vlc://quit"], check=True)
                a=input()
            else:
                messagebox.showwarning("VLC non trovato", "VLC non trovato in Program Files. Uso player di sistema.")
                os.startfile(temp_file)
                # Nota: os.startfile non aspetta la chiusura, la cancellazione potrebbe fallire se il file è in uso
            
        except Exception as e:
            messagebox.showerror("Errore", "Chiave USB errata o errore di sistema.")
        finally:
            # 3. Eliminazione sicura del file decrittato
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                    self.lbl_status.config(text="File temporaneo eliminato.", fg="blue")
                except Exception as e:
                    print(f"Impossibile eliminare il file: {e}")
            
            self.reset_ui()

    def reset_ui(self):
        self.progress['value'] = 0
        self.lbl_status.config(text="Pronto", fg="gray")
        self.btn_enc.config(state=tk.NORMAL)
        self.btn_dec.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = SecurePlayApp(root)
    root.mainloop()
