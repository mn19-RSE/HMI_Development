import subprocess

subprocess.Popen(["python3", "HMI_Development/Ammeter/Code_builds/Python_Ammeter/total_system.py"])
subprocess.Popen(["python3", "HMI_Development/Ammeter/Code_builds/Python_Ammeter/webserver.py"])

# keep main alive
while True:
    pass