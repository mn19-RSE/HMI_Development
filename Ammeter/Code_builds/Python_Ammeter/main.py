import subprocess

subprocess.Popen(["python3", "Ammeter/Code_builds/Python_Ammeter/total_system.py"])
subprocess.Popen(["python3", "Ammeter/Code_builds/Python_Ammeter/webserver.py"])

# keep main alive
while True:
    pass