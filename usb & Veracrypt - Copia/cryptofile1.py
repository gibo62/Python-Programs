import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pyAesCrypt
import os
import threading

# Buffer size (64KB)
BUFFER_SIZE = 64 * 1024

class CryptoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CryptaFile AES256")
        self.root.geometry("500x350")
        
        self.file_path = ""
        
        # Interfaccia
        tk.Label(root, text="Crittografia File AES", font=("Arial", 16)).pack(pady=10)
        
        self.btn_select = tk.Button(root, text="Seleziona File", command=self.select_file)
        self.btn_select.pack(pady=5)
        
        self.lbl_file = tk.Label(root, text="Nessun file selezionato", fg="blue")
        self.lbl_file.pack(pady=5)
        
        tk.Label(root, text="Password:").pack(pady=5)
        self.entry_pass = tk.Entry(root, show="*", width=30)
        self.entry_pass.pack()
        
        # Barra avanzamento
        self.progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=15)
        
        frame_btns = tk.Frame(root)
        frame_btns.pack(pady=10)
        
        self.btn_enc = tk.Button(frame_btns, text="Crittografa", command=lambda: self.start_thread(self.encrypt), bg="#d1e7dd")
        self.btn_enc.pack(side=tk.LEFT, padx=10)
        
        self.btn_dec = tk.Button(frame_btns, text="Decrittografa", command=lambda: self.start_thread(self.decrypt), bg="#f8d7da")
        self.btn_dec.pack(side=tk.LEFT, padx=10)

    def select_file(self):
        self.file_path = filedialog.askopenfilename()
        if self.file_path:
            self.lbl_file.config(text=os.path.basename(self.file_path))

    def start_thread(self, target_function):
        # Esegue la funzione in un thread separato
        if not self.file_path or not self.entry_pass.get():
            messagebox.showwarning("Attenzione", "Seleziona un file e inserisci la password")
            return
        
        self.btn_enc.config(state=tk.DISABLED)
        self.btn_dec.config(state=tk.DISABLED)
        threading.Thread(target=target_function).start()

    def update_progress(self, current, total):
        # Calcola percentuale
        percentage = (current / total) * 100
        self.progress['value'] = percentage
        self.root.update_idletasks()

    def encrypt(self):
        try:
            password = self.entry_pass.get()
            output_file = self.file_path + ".aes"
            
            # Simulazione avanzamento basata sulla dimensione del file
            file_size = os.path.getsize(self.file_path)
            
            # pyAesCrypt.encryptFile non ha un callback di progresso nativo
            # Usiamo un metodo basato su stream per la barra (semplificato)
            pyAesCrypt.encryptFile(self.file_path, output_file, password, BUFFER_SIZE)
            
            self.progress['value'] = 100
            messagebox.showinfo("Successo", "File crittografato!")
            self.reset_ui()
        except Exception as e:
            messagebox.showerror("Errore", str(e))
            self.reset_ui()

    def decrypt(self):
        try:
            password = self.entry_pass.get()
            if not self.file_path.endswith(".aes"):
                raise ValueError("Il file deve avere estensione .aes")
            
            output_file = self.file_path.replace(".aes", "")
            pyAesCrypt.decryptFile(self.file_path, output_file, password, BUFFER_SIZE)
            
            self.progress['value'] = 100
            messagebox.showinfo("Successo", "File decrittografato!")
            self.reset_ui()
        except Exception as e:
            messagebox.showerror("Errore", "Password errata o file danneggiato")
            self.reset_ui()

    def reset_ui(self):
        self.progress['value'] = 0
        self.btn_enc.config(state=tk.NORMAL)
        self.btn_dec.config(state=tk.NORMAL)
        self.entry_pass.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = CryptoApp(root)
    root.mainloop()
