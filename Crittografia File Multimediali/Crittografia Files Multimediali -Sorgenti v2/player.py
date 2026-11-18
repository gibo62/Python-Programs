"""
Avvia_Video_Sicuro - decifra e riproduce il video .aes presente sulla chiavetta USB.
"""

import datetime as dt
import errno
import glob
import os
import queue
import subprocess
import sys
import threading
import time
import tkinter as tk
import uuid
from tkinter import messagebox, ttk

import comune

# False (consigliato): il video viene decifrato in un file temporaneo nascosto, riprodotto in
#   loop e poi sovrascritto e cancellato. Funziona con qualsiasi formato.
# True: il video viene decifrato "al volo" e passato a VLC senza scrivere nulla su disco.
#   Più sicuro, ma niente loop e niente avanti/indietro; con gli MP4 funziona solo se
#   preparati con "faststart" (consigliati MKV o TS).
MODALITA_STREAMING = False

# Se c'è connessione internet, la data per la scadenza viene presa da un sito affidabile
# invece che dall'orologio del PC.
CONTROLLO_ORA_ONLINE = True


def leggi_data_prova():
    """
    Opzione di prova:  Avvia_Video_Sicuro.exe --data-prova GG/MM/AAAA
    Simula una data futura per verificare la scadenza (le date passate vengono ignorate).
    """
    args = sys.argv[1:]
    if "--data-prova" in args:
        i = args.index("--data-prova")
        try:
            return dt.datetime.strptime(args[i + 1], "%d/%m/%Y").date()
        except (IndexError, ValueError):
            messagebox.showerror("Errore", "Formato: --data-prova GG/MM/AAAA")
    return None


DATA_PROVA = None


def unita_del_programma():
    base = sys.executable if getattr(sys, "frozen", False) else os.path.abspath(__file__)
    return comune.lettera_unita(base)


class StealthPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("USB Stealth Player")
        self.root.geometry("500x300")
        self.coda = queue.Queue()

        tk.Label(root, text="Riproduzione Sicura da USB", font=("Arial", 12, "bold")).pack(pady=10)
        self.lbl_info = tk.Label(root, text="Ricerca file sulla USB...", fg="blue", wraplength=460)
        self.lbl_info.pack(pady=5)
        self.progress_val = tk.DoubleVar()
        ttk.Progressbar(root, length=400, variable=self.progress_val, maximum=100).pack(pady=20)
        self.status = tk.Label(root, text="In attesa...", fg="gray", wraplength=460)
        self.status.pack()

        self.root.after(100, self._leggi_coda)
        self.root.after(300, self.avvio)

    # ---- comunicazione thread -> GUI ----
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

    def _stato(self, testo, colore="gray"):
        self.status.config(text=testo, fg=colore)

    def _errore_e_chiudi(self, testo):
        messagebox.showerror("Errore", testo)
        self.root.destroy()

    # ---- logica (thread principale: WMI e finestre di dialogo) ----
    def avvio(self):
        comune.pulisci_residui()

        lettera = unita_del_programma()
        try:
            serial = comune.serial_usb_di_unita(lettera)
        except Exception:
            serial = None

        if not serial:
            # Il programma non è stato avviato da una chiavetta (es. prove in sviluppo):
            # si accetta solo se c'è una e una sola chiavetta USB inserita.
            try:
                usb = [u for u in comune.elenco_unita_usb() if u[1]]
            except Exception:
                usb = []
            if len(usb) != 1:
                self._errore_e_chiudi("Chiavetta USB non rilevata.\n"
                                      "Avviare il programma direttamente dalla chiavetta.")
                return
            lettera = usb[0][0]

        file_aes = sorted(glob.glob(os.path.join(comune.radice(lettera), "*.aes")))
        if not file_aes:
            self._errore_e_chiudi("Nessun video trovato sulla chiavetta.")
            return
        if len(file_aes) == 1:
            scelto = file_aes[0]
        else:
            self.lbl_info.config(text="Seleziona il video da riprodurre")
            scelto = self.scegli_da_elenco(file_aes)
            if not scelto:
                self.root.destroy()
                return

        # La chiave è legata alla chiavetta che contiene il file
        lettera_file = comune.lettera_unita(scelto)
        try:
            serial = comune.serial_usb_di_unita(lettera_file)
        except Exception:
            serial = None
        if not serial:
            self._errore_e_chiudi("Il file selezionato non si trova su una chiavetta USB valida.")
            return

        self.lbl_info.config(text=f"File: {os.path.basename(scelto)}")
        threading.Thread(target=self.process, args=(scelto, lettera_file, serial), daemon=True).start()

    def scegli_da_elenco(self, files):
        """
        Elenco dei video della chiavetta. Si usa al posto della finestra "Apri" di Windows
        perché i video sono file nascosti e quella finestra non li mostrerebbe.
        """
        scelta = {"file": None}
        win = tk.Toplevel(self.root)
        win.title("Scegli il video")
        win.transient(self.root)
        win.resizable(False, False)
        tk.Label(win, text="Seleziona il video da riprodurre:", font=("Arial", 10, "bold")).pack(padx=12, pady=(12, 6))
        lb = tk.Listbox(win, width=60, height=min(max(len(files), 3), 12), font=("Arial", 10))
        for f in files:
            lb.insert(tk.END, os.path.basename(f)[:-4])          # nome senza ".aes"
        lb.pack(padx=12)
        lb.selection_set(0)
        lb.focus_set()

        def conferma(_evento=None):
            sel = lb.curselection()
            if sel:
                scelta["file"] = files[sel[0]]
            win.destroy()

        lb.bind("<Double-Button-1>", conferma)
        lb.bind("<Return>", conferma)
        riga = tk.Frame(win)
        riga.pack(pady=12)
        tk.Button(riga, text="Riproduci", width=12, command=conferma).pack(side=tk.LEFT, padx=5)
        tk.Button(riga, text="Annulla", width=12, command=win.destroy).pack(side=tk.LEFT, padx=5)
        win.grab_set()
        self.root.wait_window(win)
        return scelta["file"]

    # ---- logica (thread di lavoro) ----
    def process(self, file_path, lettera, serial):
        temp_path = None
        try:
            self.ui(self._stato, "Verifica in corso...", "orange")
            with open(file_path, "rb") as f_in:
                info, grezzo = comune.leggi_intestazione(f_in)
                comune.verifica_validita(info, lettera, CONTROLLO_ORA_ONLINE, DATA_PROVA)
                pwd = comune.password(serial, grezzo)
                lunghezza = os.path.getsize(file_path) - f_in.tell()

                if info and info.get("scadenza"):
                    self.ui(self.lbl_info.config,
                            {"text": f"File: {os.path.basename(file_path)}  -  "
                                     f"valido fino al {comune.data_it(info['scadenza'])}"})

                if MODALITA_STREAMING:
                    self.riproduci_streaming(f_in, pwd, lunghezza, lettera)
                else:
                    temp_path = os.path.join(comune.cartella_temp(), uuid.uuid4().hex)
                    self.riproduci_da_temp(f_in, pwd, lunghezza, lettera, temp_path)

        except comune.ErroreScadenza as e:
            self.ui(messagebox.showerror, "Video non disponibile", str(e))
        except ValueError as e:
            # pyAesCrypt solleva ValueError per password errata / file alterato
            self.ui(messagebox.showerror, "Errore",
                    "Chiavetta non valida o file corrotto.\n\n(" + str(e) + ")")
        except OSError as e:
            if e.errno == errno.ENOSPC:
                testo = "Spazio insufficiente sul disco del computer per decifrare il video."
            else:
                testo = f"Errore di lettura/scrittura:\n{e}"
            self.ui(messagebox.showerror, "Errore", testo)
        except Exception as e:
            self.ui(messagebox.showerror, "Errore", f"Errore imprevisto:\n{e}")
        finally:
            if temp_path:
                comune.cancella_sicuro(temp_path)
            self.ui(self._stato, "Chiusura programma", "green")
            time.sleep(1.5)
            self.ui(self.root.destroy)

    def _avanzamento(self):
        ultimo = [-1.0]

        def callback(val):
            if val - ultimo[0] >= 0.5 or val >= 100:
                ultimo[0] = val
                self.ui(self.progress_val.set, val)
                self.ui(self._stato, f"Decrittografia in corso: {val:.0f}%", "orange")
        return callback

    def riproduci_da_temp(self, f_in, pwd, lunghezza, lettera, temp_path):
        vlc_path = os.path.join(comune.radice(lettera), "VLCPortable", "VLCPortable.exe")
        if not os.path.exists(vlc_path):
            raise FileNotFoundError(f"VLCPortable non trovato in {vlc_path}")

        lettore = comune.LettoreConAvanzamento(f_in, lunghezza, self._avanzamento())
        with open(temp_path, "wb") as f_out:
            comune.decifra_stream(lettore, f_out, pwd, lunghezza)
        comune.nascondi(temp_path)

        self.ui(self.progress_val.set, 100)
        self.ui(self._stato, "In riproduzione...", "green")
        subprocess.run([vlc_path, temp_path, "--loop", "--fullscreen", "--no-video-title-show",
                        "--no-qt-privacy-ask"])

    def riproduci_streaming(self, f_in, pwd, lunghezza, lettera):
        vlc_exe = os.path.join(comune.radice(lettera), "VLCPortable", "App", "vlc", "vlc.exe")
        if not os.path.exists(vlc_exe):
            raise FileNotFoundError(f"VLC non trovato in {vlc_exe}")

        self.ui(self._stato, "In riproduzione...", "green")
        proc = subprocess.Popen([vlc_exe, "-", "--fullscreen", "--no-video-title-show",
                                 "--play-and-exit", "--no-qt-privacy-ask"],
                                stdin=subprocess.PIPE)
        try:
            comune.decifra_stream(f_in, proc.stdin, pwd, lunghezza)
        except (BrokenPipeError, OSError) as e:
            # VLC chiuso dall'utente prima della fine: non è un errore
            if not isinstance(e, BrokenPipeError) and e.errno not in (errno.EPIPE, errno.EINVAL):
                raise
        finally:
            try:
                proc.stdin.close()
            except OSError:
                pass
            proc.wait()


if __name__ == "__main__":
    root = tk.Tk()
    DATA_PROVA = leggi_data_prova()
    if DATA_PROVA:
        root.title(f"USB Stealth Player  -  PROVA con data {DATA_PROVA.strftime('%d/%m/%Y')}")
    StealthPlayer(root)
    root.mainloop()
