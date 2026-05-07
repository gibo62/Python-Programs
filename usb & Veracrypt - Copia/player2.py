import vlc
import time

player = vlc.MediaPlayer("C:/Users/ospite/Nextcloud2/Video/Malabo/20260428Gilberto/Missione a Malabo.mp4")
player.play()

# Attendi che il video inizi per avere info corrette
time.sleep(2)

# Imposta il volume (0-100)
player.audio_set_volume(50)

# Metti in pausa dopo 5 secondi
time.sleep(5)
player.pause()
print("In pausa...")

# Riprendi dopo 2 secondi
time.sleep(2)
player.play()
print("Riproduzione ripresa.")

# Controlla se sta riproducendo
if player.is_playing():
    print("Il video è in riproduzione.")

time.sleep(5)
player.stop()
