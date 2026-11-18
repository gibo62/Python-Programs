"""
Cripta_File - cifra un file multimediale per una specifica chiavetta USB,
con data di scadenza facoltativa.
"""

import datetime as dt
import os
import queue
import shutil
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import comune


class EncryptorPro:
    def __init__(self, root):
        self.root = root
        self.root.title("Crittografia File Multimediali")
        self.root.geometry("480x470")
        self.root.resizable(False, False)

        self.file_path = ""
        self.unita = []                      # [(lettera, serial, etichetta)]
        self.coda = queue.Queue()            # messaggi dal thread di lavoro alla GUI

        tk.Label(root, text="Crittografia File Multimediali", font=("Arial", 11, "bold")).pack(pady=10)

        # 1. File
        tk.Button(root, text="1. Seleziona File", width=28, command=self.select_file).pack()
        self.lbl_file = tk.Label(root, text="...", fg="blue", wraplength=430)
        self.lbl_file.pack(pady=5)

        # 2. Chiavetta di destinazione
        tk.Label(root, text="2. Chiavetta USB di destinazione").pack()
        riga = tk.Frame(root)
        riga.pack(pady=3)
        self.cmb_usb = ttk.Combobox(riga, state="readonly", width=38)
        self.cmb_usb.pack(side=tk.LEFT)
        tk.Button(riga, text="Aggiorna", command=self.aggiorna_usb).pack(side=tk.LEFT, padx=5)

        # 3. Scadenza
        box = tk.LabelFrame(root, text="3. Scadenza (facoltativa)", padx=10, pady=5)
        box.pack(pady=10)
        self.usa_scadenza = tk.BooleanVar(value=False)
        tk.Checkbutton(box, text="Il video smette di funzionare dopo il giorno:",
                       variable=self.usa_scadenza, command=self._abilita_data).grid(row=0, column=0, sticky="w")
        self.txt_data = tk.Entry(box, width=12, justify="center")
        self.txt_data.insert(0, (dt.date.today() + dt.timedelta(days=30)).strftime("%d/%m/%Y"))
        self.txt_data.grid(row=0, column=1, padx=5)
        tk.Label(box, text="formato GG/MM/AAAA - il video funziona fino a quel giorno compreso",
                 fg="gray").grid(row=1, column=0, columnspan=2, sticky="w")
        self._abilita_data()

        # Avanzamento
        self.progress_val = tk.DoubleVar()
        ttk.Progressbar(root, length=380, variable=self.progress_val, maximum=100).pack(pady=10)
        self.lbl_pct = tk.Label(root, text="")
        self.lbl_pct.pack()

        self.btn_run = tk.Button(root, text="AVVIA CRITTOGRAFIA", bg="#d1e7dd", height=2, width=22,
                                 command=self.start)
        self.btn_run.pack(pady=12)

        self.root.after(100, self._leggi_coda)
        self.aggiorna_usb()

    # ---- comunicazione thread -> GUI (Tkinter non è thread-safe) ----
    def ui(self, funzione, *args):
        self.coda.put((funzione, args))

    def _leggi_coda(self):
        try:
            while True:
                funzione, args = self.coda.get_nowait()
                funzione(*args)
        except queue.Empty:
            pass
        self.root.after(100, self._leggi_coda)

    def _imposta_avanzamento(self, val):
        self.progress_val.set(val)
        self.lbl_pct.config(text=f"Avanzamento crittografia: {val:.1f}%")

    # ---- interfaccia ----
    def _abilita_data(self):
        self.txt_data.config(state=tk.NORMAL if self.usa_scadenza.get() else tk.DISABLED)

    def aggiorna_usb(self):
        try:
            self.unita = comune.elenco_unita_usb()
        except Exception as e:
            self.unita = []
            messagebox.showerror("Errore", f"Impossibile leggere le unità USB:\n{e}")
        voci = [f"{l}\\  {etichetta or '(senza nome)'}" + ("" if s else "  - NUMERO DI SERIE ASSENTE")
                for l, s, etichetta in self.unita]
        self.cmb_usb["values"] = voci
        if voci:
            self.cmb_usb.current(0)
        else:
            self.cmb_usb.set("Nessuna chiavetta USB trovata")

    def select_file(self):
        f = filedialog.askopenfilename(title="Seleziona il file da cifrare")
        if f:
            self.file_path = f
            self.lbl_file.config(text=os.path.basename(f))

    def _leggi_scadenza(self):
        """Ritorna (ok, data_o_None)."""
        if not self.usa_scadenza.get():
            return True, None
        try:
            data = dt.datetime.strptime(self.txt_data.get().strip(), "%d/%m/%Y").date()
        except ValueError:
            messagebox.showerror("Errore", "Data di scadenza non valida. Usare il formato GG/MM/AAAA.")
            return False, None
        if data < dt.date.today():
            messagebox.showerror("Errore", "La data di scadenza è già passata.")
            return False, None
        return True, data

    def start(self):
        if not self.file_path:
            messagebox.showerror("Errore", "Seleziona il file da cifrare.")
            return
        indice = self.cmb_usb.current()
        if indice < 0 or indice >= len(self.unita):
            messagebox.showerror("Errore", "Chiavetta USB non rilevata. Inseriscila e premi 'Aggiorna'.")
            return
        lettera, _, _ = self.unita[indice]

        # Il serial si rilegge adesso dall'unità scelta (la chiavetta potrebbe essere cambiata)
        try:
            serial = comune.serial_usb_di_unita(lettera)
        except Exception:
            serial = None
        if not serial:
            messagebox.showerror("Errore", f"L'unità {lettera} non è una chiavetta USB valida "
                                           "oppure non espone un numero di serie.")
            return

        ok, scadenza = self._leggi_scadenza()
        if not ok:
            return

        destinazione = comune.radice(lettera)
        out_path = os.path.join(destinazione, os.path.basename(self.file_path) + ".aes")

        dimensione = os.path.getsize(self.file_path)
        if shutil.disk_usage(destinazione).free < dimensione + 1024 * 1024:
            messagebox.showerror("Errore", "Spazio insufficiente sulla chiavetta.")
            return
        if os.path.exists(out_path) and not messagebox.askyesno(
                "Conferma", f"{os.path.basename(out_path)} esiste già sulla chiavetta. Sovrascriverlo?"):
            return

        mancanti = [n for n in ("Avvia_Video_Sicuro.exe", "VLCPortable")
                    if not os.path.exists(os.path.join(destinazione, n))]
        if mancanti and not messagebox.askyesno(
                "Attenzione", "Sulla chiavetta mancano: " + ", ".join(mancanti) +
                "\nSenza questi il video non potrà essere riprodotto. Continuare comunque?"):
            return

        self.btn_run.config(state=tk.DISABLED)
        threading.Thread(target=self.run_logic, args=(serial, scadenza, out_path, dimensione),
                         daemon=True).start()

    def run_logic(self, serial, scadenza, out_path, dimensione):
        ultimo = [-1.0]

        def avanzamento(val):
            if val - ultimo[0] >= 0.5 or val >= 100:        # aggiorna la GUI ogni mezzo punto
                ultimo[0] = val
                self.ui(self._imposta_avanzamento, val)

        try:
            comune.cifra_file(self.file_path, out_path, serial, scadenza, avanzamento)
            msg = "File crittografato correttamente."
            msg += f"\nScadenza: {scadenza.strftime('%d/%m/%Y')}" if scadenza else "\nNessuna scadenza."
            self.ui(messagebox.showinfo, "Completato", msg)
        except Exception as e:
            self.ui(messagebox.showerror, "Errore", str(e))
        finally:
            self.ui(self.btn_run.config, {"state": tk.NORMAL})
            self.ui(self._imposta_avanzamento, 0)


if __name__ == "__main__":
    root = tk.Tk()
    EncryptorPro(root)
    root.mainloop()
