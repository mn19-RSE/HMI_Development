import subprocess

subprocess.Popen(["python3", "total_system.py"])
subprocess.Popen(["python3", "webserver.py"])

# keep main alive
while True:
    pass