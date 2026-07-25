import subprocess
import sys
import time
import urllib.request

def run():
    cmd = [sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", "8501", "--server.headless", "true"]
    print("Starting Streamlit server:", " ".join(cmd))
    proc = subprocess.Popen(cmd)

    for i in range(15):
        time.sleep(1)
        try:
            resp = urllib.request.urlopen("http://localhost:8501")
            if resp.status == 200:
                print(f"\n✅ Streamlit server successfully STARTED on http://localhost:8501 (Status: {resp.status})!")
                break
        except Exception as e:
            print(f"Connecting to http://localhost:8501... ({i+1}/15)")

    # Keep background task holding process
    try:
        while proc.poll() is None:
            time.sleep(5)
    except KeyboardInterrupt:
        proc.terminate()

if __name__ == "__main__":
    run()
