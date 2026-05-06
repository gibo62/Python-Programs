import json
data = json.load(open("e:\mkey.json"))
for i in data["Case"]:
    print (f'Casa: {i["id"]} Nome: {i["nome"]}')
casa= input ("Seleziona Casa: ")             
for i in data["Case"]:
    if casa == i["id"]:
        print (f'Hai selezionato Casa: {i["nome"]}')
        print (i["key1"])
        print (i["key2"])
