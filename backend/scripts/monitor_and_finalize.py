
import time
import os
import sys
import subprocess
import shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(BASE_DIR, 'data', 'v4_run.log')
FINALIZE_SCRIPT = os.path.join(BASE_DIR, 'scripts', 'v3', 'finalize.py')

def monitor():
    print("👀 Monitoring Reincarnation Process...")
    print(f"📄 Log File: {LOG_FILE}")
    
    if not os.path.exists(LOG_FILE):
        print("❌ Log file not found yet. Waiting...")
        time.sleep(5)

    last_size = 0
    finalized = False
    
    while not finalized:
        try:
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, 'r', encoding='utf-8', errors='ignore') as f:
                    # Read new lines
                    f.seek(last_size)
                    new_lines = f.readlines()
                    last_size = f.tell()
                    
                    for line in new_lines:
                        # Print plain text, remove timestamp sometimes? No, raw is fine.
                        print(line.strip())
                        if "[SUCCESS] V4 Batch Complete" in line: # V4 completion marker
                            print("\n✅ Generation Complete detected!")
                            finalized = True
                            break
            else:
                print(".", end="", flush=True)
            
            time.sleep(2)
        except KeyboardInterrupt:
            print("\n🛑 Monitor stopped by user.")
            return

    # Trigger Finalize
    if finalized:
        print("\n🚀 Triggering Finalization Script...")
        subprocess.run([sys.executable, FINALIZE_SCRIPT])

if __name__ == "__main__":
    monitor()
