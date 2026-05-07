import subprocess

process = subprocess.run("dir C:\\", shell=True)
print (process)
