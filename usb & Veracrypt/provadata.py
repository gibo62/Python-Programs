from datetime import datetime
import time

start=datetime(2023, 9, 1, 10, 21, 45)
delta = (datetime.now() - start).total.seconds()
#diff=int(delta.total_seconds())
diff_ore=int(diff/3600)
diff_minuti=int((diff-diff_ore*3600)/60)
diff_secondi=int((diff-diff_ore*3600-diff_minuti*60))
print("Tempo di elaborazione (hh:mm:ss): {:02}:{:02}:{:02}".format(diff_ore,diff_minuti,diff_secondi))
     
       
