import subprocess
import sys
import time

cmd = [sys.executable, "-m", "streamlit", "run", "app.py", "--server.headless", "true"]
print("Executing:", " ".join(cmd))
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

for i in range(25):
    line = proc.stdout.readline()
    if line:
        print(f"[Streamlit Log] {line.strip()}")
    time.sleep(0.2)
