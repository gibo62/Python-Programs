import vlc
import time

# 1. Crea un'istanza di VLC
instance = vlc.Instance()

# 2. Crea un lettore multimediale (MediaPlayer)
player = instance.media_player_new()

# 3. Carica il file (sostituisci con il percorso del tuo file)
# Esempio: "C:/Video/mio_video.mp4" o "/home/user/musica.mp3"
media = instance.media_new("C:/Users/ospite/Nextcloud2/Video/Malabo/20260428Gilberto/Missione a Malabo.mp4")
player.set_media(media)

# 4. Avvia la riproduzione
player.play()

# 5. Attendi qualche secondo per far avviare il video (necessario se lo script finisce subito)
#time.sleep(10)

# 6. Ferma e libera le risorse
#player.stop()
