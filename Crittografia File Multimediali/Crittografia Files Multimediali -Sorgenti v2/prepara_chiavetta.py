"""
Prepara_Chiavetta - crea in un solo passaggio una chiavetta pronta da distribuire:

  1. formatta la chiavetta (facoltativo)
  2. copia Avvia_Video_Sicuro.exe e la cartella VLCPortable
  3. cifra uno o più video per quella chiavetta, con scadenza facoltativa
  4. verifica che i file cifrati si decifrino correttamente

Per la formattazione il programma deve essere avviato come amministratore
(la configurazione Prepara_Chiavetta.json lo chiede automaticamente).
"""

import ctypes
import datetime as dt
import os
import queue
import re
import shutil
import subprocess
import sys
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import comune

NOME_PLAYER = "Avvia_Video_Sicuro.exe"
NOME_VLC = "VLCPortable"
CREATE_NO_WINDOW = 0x08000000


def cartella_programma():
    base = sys.executable if getattr(sys, "frozen", False) else os.path.abspath(__file__)
    return os.path.dirname(base)


def is_admin():
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def dimensione_cartella(percorso):
    totale = 0
    for cartella, _, files in os.walk(percorso):
        for f in files:
            try:
                totale += os.path.getsize(os.path.join(cartella, f))
            except OSError:
                pass
    return totale


def formato_gb(n):
    return f"{n / 1024 ** 3:.1f} GB"


def formato_dim(n):
    return f"{n / 1024 ** 3:.2f} GB" if n >= 1024 ** 3 else f"{n / 1024 ** 2:.0f} MB"


def durata(secondi):
    secondi = int(secondi)
    if secondi < 60:
        return f"{secondi} s"
    m, s = divmod(secondi, 60)
    return f"{m} min {s:02d} s"


class PreparaChiavetta:
    def __init__(self, root):
        self.root = root
        self.root.title("Prepara Chiavetta Video")
        self.root.geometry("580x720")
        self.root.minsize(580, 640)
        self.lavorando = False
        self.root.protocol("WM_DELETE_WINDOW", self.chiudi)

        self.coda = queue.Queue()
        self.unita = []
        self.video = []
        app = cartella_programma()


        # --- Chiavetta ---
        box = tk.LabelFrame(root, text="1. Chiavetta USB", padx=8, pady=5)
        box.pack(fill="x", padx=12, pady=4)
        self.cmb_usb = ttk.Combobox(box, state="readonly", width=55)
        self.cmb_usb.grid(row=0, column=0)
        tk.Button(box, text="Aggiorna", command=self.aggiorna_usb).grid(row=0, column=1, padx=5)

        # --- Video ---
        box = tk.LabelFrame(root, text="2. Video da inserire", padx=8, pady=5)
        box.pack(fill="x", padx=12, pady=4)
        tk.Button(box, text="Scegli video...", command=self.scegli_video).grid(row=0, column=0, sticky="w")
        self.lbl_video = tk.Label(box, text="Nessun video selezionato", fg="blue",
                                  wraplength=520, justify="left")
        self.lbl_video.grid(row=1, column=0, sticky="w", pady=3)

        # --- Scadenza ---
        box = tk.LabelFrame(root, text="3. Scadenza (facoltativa)", padx=8, pady=5)
        box.pack(fill="x", padx=12, pady=4)
        self.usa_scadenza = tk.BooleanVar(value=False)
        tk.Checkbutton(box, text="Il video smette di funzionare dopo il giorno:",
                       variable=self.usa_scadenza, command=self._abilita).grid(row=0, column=0, sticky="w")
        self.txt_data = tk.Entry(box, width=12, justify="center")
        self.txt_data.insert(0, (dt.date.today() + dt.timedelta(days=30)).strftime("%d/%m/%Y"))
        self.txt_data.grid(row=0, column=1, padx=5)

        # --- Opzioni ---
        box = tk.LabelFrame(root, text="4. Opzioni", padx=8, pady=5)
        box.pack(fill="x", padx=12, pady=4)
        self.formatta = tk.BooleanVar(value=True)
        tk.Checkbutton(box, text="Formatta la chiavetta (CANCELLA TUTTO il contenuto)",
                       variable=self.formatta, command=self._abilita).grid(row=0, column=0, columnspan=4, sticky="w")
        tk.Label(box, text="File system:").grid(row=1, column=0, sticky="e")
        self.cmb_fs = ttk.Combobox(box, state="readonly", width=8, values=["exFAT", "NTFS", "FAT32"])
        self.cmb_fs.current(0)
        self.cmb_fs.grid(row=1, column=1, sticky="w", padx=4)
        tk.Label(box, text="Nome chiavetta:").grid(row=1, column=2, sticky="e")
        self.txt_etichetta = tk.Entry(box, width=13)
        self.txt_etichetta.insert(0, "VIDEO")
        self.txt_etichetta.grid(row=1, column=3, sticky="w", padx=4)
        self.nascondi_vlc = tk.BooleanVar(value=True)
        tk.Checkbutton(box, text="Lascia visibile solo il player (nasconde VLCPortable e i video)",
                       variable=self.nascondi_vlc).grid(row=2, column=0, columnspan=4, sticky="w")
        self.verifica = tk.BooleanVar(value=True)
        tk.Checkbutton(box, text="Verifica i video cifrati alla fine (più lento, consigliato)",
                       variable=self.verifica).grid(row=3, column=0, columnspan=4, sticky="w")

        # --- Sorgenti ---
        box = tk.LabelFrame(root, text="File da copiare", padx=8, pady=5)
        box.pack(fill="x", padx=12, pady=4)
        self.txt_player = self._riga_percorso(box, 0, "Player:", os.path.join(app, NOME_PLAYER), cartella=False)
        self.txt_vlc = self._riga_percorso(box, 1, "VLCPortable:", os.path.join(app, NOME_VLC), cartella=True)

        self.btn = tk.Button(root, text="PREPARA CHIAVETTA", bg="#d1e7dd", height=2, width=30,
                             font=("Arial", 10, "bold"), command=self.start)
        self.btn.pack(pady=6)

        # --- Avanzamento ---
        box = tk.LabelFrame(root, text="Avanzamento", padx=8, pady=5)
        box.pack(fill="both", expand=True, padx=12, pady=(0, 10))
        self.lbl_passo = tk.Label(box, text="Pronto.", font=("Arial", 11, "bold"), fg="#1f4e79", anchor="w")
        self.lbl_passo.pack(fill="x")
        self.progress_val = tk.DoubleVar()
        self.pb = ttk.Progressbar(box, variable=self.progress_val, maximum=100)
        self.pb.pack(fill="x", pady=4)
        self.status = tk.Label(box, text="", fg="#444", anchor="w")
        self.status.pack(fill="x")
        self.log = tk.Text(box, height=6, state=tk.DISABLED, bg="#f7f7f7", font=("Consolas", 9))
        self.log.pack(fill="both", expand=True, pady=(4, 0))

        self._abilita()
        self.root.after(100, self._leggi_coda)
        self.aggiorna_usb()

    # ---------------- utilità GUI ----------------
    def _riga_percorso(self, box, riga, etichetta, valore, cartella):
        tk.Label(box, text=etichetta).grid(row=riga, column=0, sticky="e")
        e = tk.Entry(box, width=52)
        e.insert(0, valore)
        e.grid(row=riga, column=1, padx=4, pady=2)

        def sfoglia():
            # Apre la finestra nella posizione attualmente proposta
            attuale = os.path.normpath(e.get().strip() or cartella_programma())
            if cartella:
                iniziale = attuale if os.path.isdir(attuale) else os.path.dirname(attuale)
                if not os.path.isdir(iniziale):
                    iniziale = cartella_programma()
                p = filedialog.askdirectory(initialdir=iniziale, mustexist=True,
                                            title="Scegli la cartella VLCPortable")
            else:
                iniziale = os.path.dirname(attuale)
                if not os.path.isdir(iniziale):
                    iniziale = cartella_programma()
                p = filedialog.askopenfilename(initialdir=iniziale,
                                               initialfile=os.path.basename(attuale),
                                               title="Scegli Avvia_Video_Sicuro.exe",
                                               filetypes=[("Programma", "*.exe")])
            if p:
                e.delete(0, tk.END)
                e.insert(0, os.path.normpath(p))
        tk.Button(box, text="...", command=sfoglia).grid(row=riga, column=2)
        return e

    def _abilita(self):
        self.txt_data.config(state=tk.NORMAL if self.usa_scadenza.get() else tk.DISABLED)
        stato = "readonly" if self.formatta.get() else "disabled"
        self.cmb_fs.config(state=stato)
        self.txt_etichetta.config(state=tk.NORMAL if self.formatta.get() else tk.DISABLED)

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

    def _stato(self, testo, valore=None):
        self.status.config(text=testo)
        if valore is not None:
            self.progress_val.set(valore)

    def _passo(self, testo, indeterminato=False, colore="#1f4e79"):
        """Titolo grande della fase in corso. indeterminato=True: barra animata (durata ignota)."""
        self.lbl_passo.config(text=testo, fg=colore)
        self.status.config(text="")
        self.pb.stop()
        if indeterminato:
            self.pb.config(mode="indeterminate")
            self.pb.start(15)
        else:
            self.pb.config(mode="determinate")
            self.progress_val.set(0)

    def _scrivi_log(self, riga):
        self.log.config(state=tk.NORMAL)
        self.log.insert(tk.END, riga + "\n")
        self.log.see(tk.END)
        self.log.config(state=tk.DISABLED)

    def _pulisci_log(self):
        self.log.config(state=tk.NORMAL)
        self.log.delete("1.0", tk.END)
        self.log.config(state=tk.DISABLED)

    def _in_corso(self, attivo):
        self.lavorando = attivo
        self.btn.config(state=tk.DISABLED if attivo else tk.NORMAL,
                        text="PREPARAZIONE IN CORSO..." if attivo else "PREPARA CHIAVETTA",
                        bg="#ffe8a3" if attivo else "#d1e7dd")
        self.root.config(cursor="watch" if attivo else "")
        if not attivo:
            self.pb.stop()
            self.pb.config(mode="determinate")

    def chiudi(self):
        if self.lavorando and not messagebox.askyesno(
                "Preparazione in corso",
                "La preparazione non è finita: se chiudi ora la chiavetta resterà incompleta.\n\n"
                "Chiudere comunque?", icon="warning", default="no"):
            return
        self.root.destroy()

    def _callback(self, totale_byte):
        """Callback di avanzamento: percentuale, MB e tempo rimanente stimato."""
        inizio = time.monotonic()
        ultimo = [-1.0]

        def cb(val):
            if val - ultimo[0] >= 0.5 or val >= 100:
                ultimo[0] = val
                trascorso = time.monotonic() - inizio
                testo = f"{val:.0f}%   -   {formato_dim(totale_byte * val / 100)} di {formato_dim(totale_byte)}"
                if 2 < val < 100 and trascorso > 3:
                    testo += f"   -   circa {durata(trascorso * (100 - val) / val)} rimanenti"
                self.ui(self._stato, testo, val)
        return cb

    # ---------------- selezioni ----------------
    def aggiorna_usb(self):
        try:
            self.unita = comune.elenco_unita_usb()
        except Exception as e:
            self.unita = []
            messagebox.showerror("Errore", f"Impossibile leggere le unità USB:\n{e}")
        voci = []
        for lettera, serial, etichetta in self.unita:
            try:
                dim = formato_gb(shutil.disk_usage(comune.radice(lettera)).total)
            except OSError:
                dim = "?"
            voci.append(f"{lettera}\\  {etichetta or '(senza nome)'}  -  {dim}"
                        + ("" if serial else "  - NUMERO DI SERIE ASSENTE"))
        self.cmb_usb["values"] = voci
        if voci:
            self.cmb_usb.current(0)
        else:
            self.cmb_usb.set("Nessuna chiavetta USB trovata")

    def scegli_video(self):
        files = filedialog.askopenfilenames(title="Scegli uno o più video")
        if files:
            self.video = list(files)
            totale = sum(os.path.getsize(f) for f in self.video)
            self.lbl_video.config(text=f"{len(self.video)} video ({formato_dim(totale)}): "
                                       + ", ".join(os.path.basename(f) for f in self.video))

    def _leggi_scadenza(self):
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

    # ---------------- controlli e avvio ----------------
    def start(self):
        i = self.cmb_usb.current()
        if i < 0 or i >= len(self.unita):
            messagebox.showerror("Errore", "Nessuna chiavetta selezionata. Inseriscila e premi 'Aggiorna'.")
            return
        lettera, _, etichetta_attuale = self.unita[i]
        if not self.video:
            messagebox.showerror("Errore", "Scegli almeno un video.")
            return

        player = self.txt_player.get().strip()
        vlc = self.txt_vlc.get().strip()
        if not os.path.isfile(player):
            messagebox.showerror("Errore", f"Player non trovato:\n{player}")
            return
        if not os.path.isfile(os.path.join(vlc, "VLCPortable.exe")):
            messagebox.showerror("Errore", f"Cartella VLCPortable non valida:\n{vlc}")
            return

        ok, scadenza = self._leggi_scadenza()
        if not ok:
            return

        try:
            serial = comune.serial_usb_di_unita(lettera)
        except Exception:
            serial = None
        if not serial:
            messagebox.showerror("Errore", f"L'unità {lettera} non è una chiavetta USB valida "
                                           "oppure non espone un numero di serie.")
            return

        # Nessun file sorgente può stare sulla chiavetta da preparare
        sorgenti = [player, vlc] + self.video + [cartella_programma()]
        if any(comune.lettera_unita(p) == lettera for p in sorgenti):
            messagebox.showerror("Errore", "Il programma, il player, VLCPortable e i video devono stare "
                                           "sul computer, non sulla chiavetta da preparare.")
            return

        radice = comune.radice(lettera)
        formatta = self.formatta.get()
        fs = self.cmb_fs.get()

        # Spazio
        necessario = (os.path.getsize(player) + dimensione_cartella(vlc)
                      + sum(os.path.getsize(v) for v in self.video) + 10 * 1024 * 1024)
        uso = shutil.disk_usage(radice)
        disponibile = uso.total if formatta else uso.free
        if necessario > disponibile:
            messagebox.showerror("Errore", f"Spazio insufficiente: servono {formato_gb(necessario)}, "
                                           f"disponibili {formato_gb(disponibile)}.")
            return
        if formatta and fs == "FAT32" and any(os.path.getsize(v) >= 4 * 1024 ** 3 for v in self.video):
            messagebox.showerror("Errore", "FAT32 non supporta file oltre i 4 GB. Scegli exFAT o NTFS.")
            return

        if formatta:
            if not is_admin():
                messagebox.showerror("Errore", "Per formattare la chiavetta il programma deve essere "
                                               "avviato come amministratore\n(tasto destro > "
                                               "Esegui come amministratore).")
                return
            etichetta = re.sub(r"[^A-Za-z0-9 _-]", "", self.txt_etichetta.get())[:11] or "VIDEO"
            if not messagebox.askyesno(
                    "ATTENZIONE - Formattazione",
                    f"Verrà formattata l'unità {lettera}  "
                    f"\"{etichetta_attuale or 'senza nome'}\"  ({formato_gb(uso.total)}).\n\n"
                    "TUTTO il contenuto verrà cancellato definitivamente.\n\nProcedere?",
                    icon="warning", default="no"):
                return
        else:
            etichetta = None

        self._pulisci_log()
        self._scrivi_log(f"Avvio preparazione della chiavetta {lettera} - {time.strftime('%H:%M:%S')}")
        self._in_corso(True)
        threading.Thread(target=self.lavora, daemon=True,
                         args=(lettera, serial, scadenza, player, vlc, list(self.video), etichetta, fs,
                               self.nascondi_vlc.get(), self.verifica.get())).start()

    # ---------------- lavoro (thread secondario) ----------------
    def lavora(self, lettera, serial, scadenza, player, vlc, video, etichetta, fs, nascondi, verifica):
        radice = comune.radice(lettera)
        passi = (1 if etichetta is not None else 0) + 2 + len(video) * (2 if verifica else 1)
        contatore = [0]
        inizio_totale = time.monotonic()

        def passo(titolo, indeterminato=False):
            contatore[0] += 1
            self.ui(self._passo, f"Passo {contatore[0]} di {passi}:  {titolo}", indeterminato)
            return time.monotonic()

        def fatto(testo, inizio):
            self.ui(self._scrivi_log, f"\u2714 {testo}  ({durata(time.monotonic() - inizio)})")

        try:
            if etichetta is not None:
                t = passo(f"formattazione di {lettera} in {fs}", indeterminato=True)
                self.ui(self._stato, "Può richiedere fino a un minuto. Non togliere la chiavetta.")
                self.formatta_unita(lettera, fs, etichetta)
                fatto(f"Chiavetta formattata ({fs}, nome \"{etichetta}\")", t)

            t = passo("copia del player")
            comune.mostra(os.path.join(radice, NOME_PLAYER))
            shutil.copy2(player, os.path.join(radice, NOME_PLAYER))
            self.ui(self._stato, "100%", 100)
            fatto("Player copiato", t)

            t = passo("copia di VLCPortable (molti file piccoli)")
            self.copia_vlc(vlc, os.path.join(radice, NOME_VLC))
            if nascondi:
                comune.nascondi(os.path.join(radice, NOME_VLC))
            fatto("VLCPortable copiato" + (" e nascosto" if nascondi else ""), t)

            percorsi = []
            for v in video:
                nome = os.path.basename(v)
                dest = os.path.join(radice, nome + ".aes")
                t = passo(f"cifratura di {nome}")
                comune.cifra_file(v, dest, serial, scadenza, self._callback(os.path.getsize(v)))
                if nascondi:
                    comune.nascondi(dest)
                percorsi.append(dest)
                fatto(f"Cifrato: {nome}" + (" (nascosto)" if nascondi else ""), t)

            if verifica:
                for pth in percorsi:
                    nome = os.path.basename(pth)
                    t = passo(f"verifica di {nome}")
                    comune.verifica_file(pth, serial, self._callback(os.path.getsize(pth)))
                    fatto(f"Verificato: {nome}", t)

            tot = durata(time.monotonic() - inizio_totale)
            self.ui(self._passo, "\u2714 Chiavetta pronta", False, "#1e7e34")
            self.ui(self._stato, f"Tempo totale: {tot}", 100)
            self.ui(self._scrivi_log, "Completato. Ora puoi rimuovere la chiavetta "
                                      "(meglio con 'Rimozione sicura dell'hardware').")
            msg = f"Chiavetta {lettera} pronta in {tot}.\n\nVideo: {len(percorsi)}\n"
            msg += (f"Scadenza: {scadenza.strftime('%d/%m/%Y')}" if scadenza else "Nessuna scadenza")
            msg += "\n\nPer prepararne un'altra: inserisci la chiavetta successiva e premi 'Aggiorna'."
            self.ui(messagebox.showinfo, "Completato", msg)
        except Exception as e:
            if isinstance(e, ValueError):
                testo = f"Verifica fallita: il video cifrato non è leggibile. ({e})"
            else:
                testo = str(e)
            self.ui(self._passo, "\u2718 Errore: preparazione non completata", False, "#b02a37")
            self.ui(self._scrivi_log, "\u2718 " + testo)
            self.ui(messagebox.showerror, "Errore", testo)
        finally:
            self.ui(self._in_corso, False)
            self.ui(self.aggiorna_usb)

    def formatta_unita(self, lettera, fs, etichetta):
        comando = (f"Format-Volume -DriveLetter {lettera[0]} -FileSystem {fs} "
                   f"-NewFileSystemLabel '{etichetta}' -Force -Confirm:$false | Out-Null")
        r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", comando],
                           capture_output=True, text=True, creationflags=CREATE_NO_WINDOW)
        if r.returncode != 0:
            raise RuntimeError("Formattazione non riuscita:\n" + (r.stderr or r.stdout).strip()[:600])
        # Attende che l'unità torni disponibile
        radice = comune.radice(lettera)
        for _ in range(60):
            if os.path.exists(radice):
                try:
                    os.listdir(radice)
                    return
                except OSError:
                    pass
            time.sleep(0.5)
        raise RuntimeError(f"Dopo la formattazione l'unità {lettera} non è tornata disponibile.")

    def copia_vlc(self, sorgente, destinazione):
        totale = max(dimensione_cartella(sorgente), 1)
        copiati = 0
        cb = self._callback(totale)
        for cartella, _, files in os.walk(sorgente):
            rel = os.path.relpath(cartella, sorgente)
            dest_cartella = os.path.normpath(os.path.join(destinazione, rel))
            os.makedirs(dest_cartella, exist_ok=True)
            for f in files:
                origine = os.path.join(cartella, f)
                shutil.copy2(origine, os.path.join(dest_cartella, f))
                copiati += os.path.getsize(origine)
                cb(copiati / totale * 100)


if __name__ == "__main__":
    root = tk.Tk()
    PreparaChiavetta(root)
    root.mainloop()
