from cryptography.fernet import Fernet
import base64
key="KTrVM5KjLb3jfoi9sTymXD4NUojaLpWhYwo2kT43GuD="
key=bytes(key,'utf-8')
print (key, len (key))
cipher_suite = Fernet(key)
#cipher_text = cipher_suite.encrypt(bytes(testo,'utf-8'))
#plain_text = cipher_suite.decrypt(cipher_text)
#print (cipher_text)
#plain_text = cipher_suite.decrypt(cipher_text)
#print(plain_text)
#print (str(cipher_text,'utf-8'))
          
f = open(f'E:\\volume.id',"r")
cipher_text=bytes(f.read(),'utf-8')
f.close()
plain_text = cipher_suite.decrypt(cipher_text)
print (plain_text)
