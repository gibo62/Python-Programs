"""
comune.py - Funzioni condivise da Cripta_File (encryptor.py) e Avvia_Video_Sicuro (player.py).

PyInstaller include automaticamente questo modulo in entrambi gli eseguibili,
basta che stia nella stessa cartella dei due script.

Formato del file .aes (versione 2):
    MAGIC (6 byte) | lunghezza intestazione (2 byte, big-endian) | intestazione JSON | dati pyAesCrypt

L'intestazione contiene data di creazione e data di scadenza. È in chiaro (il player
deve leggerla prima di decifrare), ma entra nel calcolo della password: se qualcuno
la modifica (per esempio per allungare la scadenza) la password non corrisponde più
e il file non si decifra.

I file creati con la versione precedente (senza intestazione) restano leggibili.
"""

import ctypes
import datetime as dt
import email.utils
import glob
import inspect
import io
import json
import os
import struct
import tempfile
import urllib.error
import urllib.request

import pyAesCrypt

# ATTENZIONE: deve restare identico a quello della versione precedente,
# altrimenti i file .aes già distribuiti non si aprono più.
SEGRETO = "LcSFcf6tR4G^HW&uVwiBVe_Gn5HukvTm*@"

MAGIC = b"CFMv2\x00"
BUFFER_SIZE = 128 * 1024
NOME_FILE_STATO = ".cfm_stato"          # file nascosto sulla chiavetta (controllo orologio)
TOLLERANZA_OROLOGIO = dt.timedelta(hours=36)
SITI_ORA_ONLINE = ("https://www.google.com", "https://www.microsoft.com", "https://www.cloudflare.com")


class ErroreUSB(Exception):
    pass


class ErroreScadenza(Exception):
    pass


# ---------------------------------------------------------------------------
# Chiavette USB (WMI)
# Nota: WMI va usato dal thread principale (quello di Tkinter); dai thread
# secondari servirebbe pythoncom.CoInitialize().
# ---------------------------------------------------------------------------

def _wmi():
    import wmi
    return wmi.WMI()


def _disco_usb(disk):
    tipo = (disk.InterfaceType or "").upper()
    pnp = (disk.PNPDeviceID or "").upper()
    return tipo == "USB" or pnp.startswith("USBSTOR")


def _serial(disk):
    return (disk.SerialNumber or "").strip() or None


def lettera_unita(percorso):
    """'E:\\cartella\\file.aes' -> 'E:'"""
    return os.path.splitdrive(os.path.abspath(percorso))[0].upper()


def radice(lettera):
    """'E:' -> 'E:\\' (senza backslash Windows userebbe la cartella corrente dell'unità)."""
    return lettera.rstrip("\\/") + "\\"


def serial_usb_di_unita(lettera):
    """Serial del disco USB che contiene l'unità indicata ('E:'). None se l'unità non è su USB."""
    c = _wmi()
    for ld in c.Win32_LogicalDisk(DeviceID=lettera.upper()):
        for part in ld.associators("Win32_LogicalDiskToPartition"):
            for disk in part.associators("Win32_DiskDriveToDiskPartition"):
                if _disco_usb(disk):
                    return _serial(disk)
    return None


def elenco_unita_usb():
    """Lista di (lettera, serial, etichetta) per tutte le unità che stanno su dischi USB."""
    risultato = []
    c = _wmi()
    for disk in c.Win32_DiskDrive():
        if not _disco_usb(disk):
            continue
        serial = _serial(disk)
        for part in disk.associators("Win32_DiskDriveToDiskPartition"):
            for ld in part.associators("Win32_LogicalDiskToPartition"):
                risultato.append((ld.DeviceID.upper(), serial, ld.VolumeName or ""))
    risultato.sort()
    return risultato


# ---------------------------------------------------------------------------
# Intestazione e password
# ---------------------------------------------------------------------------

def oggi_utc():
    return dt.datetime.now(dt.timezone.utc).date()


def crea_intestazione(scadenza):
    """scadenza: datetime.date oppure None. Ritorna (byte da scrivere in testa al file, JSON grezzo)."""
    info = {
        "v": 2,
        "creato": oggi_utc().isoformat(),
        "scadenza": scadenza.isoformat() if scadenza else None,
    }
    grezzo = json.dumps(info, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return MAGIC + struct.pack(">H", len(grezzo)) + grezzo, grezzo


def leggi_intestazione(f):
    """
    Legge l'intestazione dal file aperto in 'rb'.
    Ritorna (info, grezzo) per i file v2, (None, None) per i file del vecchio formato
    (in quel caso il file viene riportato all'inizio).
    """
    inizio = f.read(len(MAGIC))
    if inizio != MAGIC:
        f.seek(0)
        return None, None
    dati = f.read(2)
    if len(dati) != 2:
        raise ValueError("Intestazione del file danneggiata.")
    (n,) = struct.unpack(">H", dati)
    grezzo = f.read(n)
    if len(grezzo) != n:
        raise ValueError("Intestazione del file danneggiata.")
    return json.loads(grezzo.decode("utf-8")), grezzo


def password(serial, intestazione_grezza=None):
    if intestazione_grezza is None:                       # vecchio formato
        return SEGRETO + serial
    return SEGRETO + serial + "|" + intestazione_grezza.decode("utf-8")


# ---------------------------------------------------------------------------
# Cifratura / decifratura con avanzamento
# ---------------------------------------------------------------------------

class LettoreConAvanzamento(io.RawIOBase):
    """Avvolge un file in lettura e segnala i byte letti (per la barra di avanzamento)."""

    def __init__(self, f, totale, callback):
        self.f = f
        self.totale = max(totale, 1)
        self.callback = callback
        self.letti = 0

    def readable(self):
        return True

    def readinto(self, b):
        n = self.f.readinto(b)
        if n:
            self.letti += n
            self.callback(min(self.letti / self.totale * 100, 100.0))
        return n


def decifra_stream(f_in, f_out, pwd, lunghezza):
    """Compatibile sia con pyAesCrypt < 6 (richiede inputLength) sia con le versioni recenti."""
    parametri = inspect.signature(pyAesCrypt.decryptStream).parameters
    if "inputLength" in parametri:
        pyAesCrypt.decryptStream(f_in, f_out, pwd, BUFFER_SIZE, lunghezza)
    else:
        pyAesCrypt.decryptStream(f_in, f_out, pwd, BUFFER_SIZE)


def cifra_file(sorgente, destinazione, serial, scadenza, callback=None):
    """
    Cifra 'sorgente' in 'destinazione' (.aes) per la chiavetta con il serial indicato.
    Scrive prima su un file .part e lo rinomina solo a fine lavoro: in caso di errore
    non resta nessun file incompleto.
    """
    temporaneo = destinazione + ".part"
    mostra(destinazione)                 # se esiste già ed è nascosto, va reso sovrascrivibile
    testa, grezzo = crea_intestazione(scadenza)
    pwd = password(serial, grezzo)
    try:
        with open(sorgente, "rb") as f_in, open(temporaneo, "wb") as f_out:
            f_out.write(testa)
            lettore = (LettoreConAvanzamento(f_in, os.path.getsize(sorgente), callback)
                       if callback else f_in)
            pyAesCrypt.encryptStream(lettore, f_out, pwd, BUFFER_SIZE)
        os.replace(temporaneo, destinazione)
    except BaseException:
        try:
            os.remove(temporaneo)
        except OSError:
            pass
        raise


class _Scarico:
    """Destinazione che scarta i dati: serve per verificare un file senza scriverlo su disco."""

    def write(self, b):
        return len(b)

    def flush(self):
        pass


def verifica_file(percorso, serial, callback=None):
    """Decifra l'intero file senza salvarlo. Solleva ValueError se la chiave o i dati non sono validi."""
    with open(percorso, "rb") as f:
        info, grezzo = leggi_intestazione(f)
        lunghezza = os.path.getsize(percorso) - f.tell()
        lettore = LettoreConAvanzamento(f, lunghezza, callback) if callback else f
        decifra_stream(lettore, _Scarico(), password(serial, grezzo), lunghezza)
    return info


# ---------------------------------------------------------------------------
# Scadenza e controllo dell'orologio
# ---------------------------------------------------------------------------

def ora_online(timeout=3):
    """Ora UTC presa dall'intestazione 'Date' di un sito noto. None se non c'è connessione."""
    for url in SITI_ORA_ONLINE:
        try:
            req = urllib.request.Request(url, method="HEAD")
            with urllib.request.urlopen(req, timeout=timeout) as r:
                data = r.headers.get("Date")
        except urllib.error.HTTPError as e:              # anche un 4xx/5xx porta la data
            data = e.headers.get("Date") if e.headers else None
        except Exception:
            continue
        if data:
            try:
                return email.utils.parsedate_to_datetime(data).astimezone(dt.timezone.utc)
            except Exception:
                continue
    return None


def _percorso_stato(lettera):
    return os.path.join(radice(lettera), NOME_FILE_STATO)


def _leggi_stato(lettera):
    try:
        with open(_percorso_stato(lettera), "r", encoding="utf-8") as f:
            return dt.datetime.fromisoformat(json.load(f)["ultimo"])
    except Exception:
        return None


def _scrivi_stato(lettera, quando):
    percorso = _percorso_stato(lettera)
    testo = json.dumps({"ultimo": quando.isoformat()})
    try:
        if os.path.exists(percorso):
            # Su Windows open(..., "w") fallisce sui file nascosti: si riscrive in "r+"
            with open(percorso, "r+", encoding="utf-8") as f:
                f.write(testo)
                f.truncate()
        else:
            with open(percorso, "w", encoding="utf-8") as f:
                f.write(testo)
            nascondi(percorso)
    except OSError:
        pass                                              # chiavetta protetta da scrittura: pazienza


def data_it(iso):
    return dt.date.fromisoformat(iso).strftime("%d/%m/%Y")


def verifica_validita(info, lettera, controllo_online=True, data_prova=None):
    """
    Solleva ErroreScadenza se il video è scaduto o se l'orologio del PC è stato portato indietro.
    Non fa nulla per i file senza scadenza.

    data_prova (datetime.date, facoltativa): simula una data FUTURA per provare la scadenza.
    Viene usata solo se successiva alla data reale (non può allungare la validità)
    e in modalità prova non viene aggiornato il file di stato sulla chiavetta.
    """
    if not info or not info.get("scadenza"):
        return

    scadenza = dt.date.fromisoformat(info["scadenza"])
    creato = dt.date.fromisoformat(info["creato"])
    ora_pc = dt.datetime.now(dt.timezone.utc)
    online = ora_online() if controllo_online else None

    if online is not None:
        ora = online                                       # fonte affidabile
    else:
        ora = ora_pc
        ultimo = _leggi_stato(lettera)
        if ultimo is not None and ora < ultimo - TOLLERANZA_OROLOGIO:
            raise ErroreScadenza(
                "La data del computer risulta precedente all'ultimo utilizzo della chiavetta.\n"
                "Correggere data e ora di Windows e riprovare.")
        if ora.date() < creato - dt.timedelta(days=1):
            raise ErroreScadenza(
                "La data del computer è precedente alla creazione del video.\n"
                "Correggere data e ora di Windows e riprovare.")

    in_prova = False
    if data_prova is not None and data_prova > ora.date():
        ora = dt.datetime.combine(data_prova, dt.time(12, 0), dt.timezone.utc)
        in_prova = True

    if ora.date() > scadenza:
        raise ErroreScadenza(f"Questo video è scaduto il {scadenza.strftime('%d/%m/%Y')}."
                             + ("\n\n(Prova con data simulata " + data_prova.strftime('%d/%m/%Y') + ")"
                                if in_prova else ""))
    if in_prova:
        return

    precedente = _leggi_stato(lettera)
    if online is None and precedente is not None:
        ora = max(ora, precedente)
    _scrivi_stato(lettera, ora)


# ---------------------------------------------------------------------------
# File temporanei
# ---------------------------------------------------------------------------

def nascondi(percorso):
    if os.name == "nt":
        try:
            ctypes.windll.kernel32.SetFileAttributesW(str(percorso), 0x02)  # FILE_ATTRIBUTE_HIDDEN
        except Exception:
            pass


def mostra(percorso):
    """Toglie gli attributi nascosto/sola lettura (Windows non sovrascrive i file nascosti)."""
    if os.name == "nt" and os.path.exists(percorso):
        try:
            ctypes.windll.kernel32.SetFileAttributesW(str(percorso), 0x80)  # FILE_ATTRIBUTE_NORMAL
        except Exception:
            pass


def cartella_temp():
    d = os.path.join(tempfile.gettempdir(), "cfm_cache")
    os.makedirs(d, exist_ok=True)
    nascondi(d)
    return d


def cancella_sicuro(percorso):
    """Sovrascrive con zeri e poi cancella (su SSD/flash è una misura di massima, non garantita)."""
    try:
        dimensione = os.path.getsize(percorso)
        zeri = bytes(BUFFER_SIZE)
        with open(percorso, "r+b") as f:
            rimanenti = dimensione
            while rimanenti > 0:
                n = min(rimanenti, BUFFER_SIZE)
                f.write(zeri[:n])
                rimanenti -= n
            f.flush()
            os.fsync(f.fileno())
    except OSError:
        pass
    try:
        os.remove(percorso)
    except OSError:
        pass


def pulisci_residui():
    """Cancella eventuali video decifrati rimasti da esecuzioni interrotte (crash, spegnimento)."""
    for p in glob.glob(os.path.join(cartella_temp(), "*")):
        cancella_sicuro(p)
