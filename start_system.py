import subprocess
import sys
import os
import signal
import time

def start_system():
    """
    MIRRA System Launcher
    Concurrent execution of Backend (FastAPI) and Frontend (Next.js)
    """
    cwd = os.getcwd()
    frontend_dir = os.path.join(cwd, "frontend")
    
    print("🚀 MIRRA System Launch Sequence Initiated...")
    
    # 1. Start Backend
    print("[1/2] Starting Backend (Uvicorn)...")
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.app.main:app", "--reload", "--port", "8000"],
        cwd=cwd
    )
    
    # 2. Start Frontend
    print("[2/2] Starting Frontend (Next.js)...")
    # Use 'npm.cmd' on Windows, 'npm' on Unix
    npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
    frontend_process = subprocess.Popen(
        [npm_cmd, "run", "dev"],
        cwd=frontend_dir
    )
    
    print("\n✨ SYSTEM ONLINE ✨")
    print("------------------------------------------------")
    print("📡 Backend API: http://localhost:8000")
    print("👁️ Frontend UI: http://localhost:3000")
    print("------------------------------------------------")
    print("Press Ctrl+C to shutdown.")
    
    try:
        while True:
            time.sleep(1)
            # Check if processes are still alive
            if backend_process.poll() is not None:
                print("Backend stopped unexpectedly.")
                break
            if frontend_process.poll() is not None:
                print("Frontend stopped unexpectedly.")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Shutting down MIRRA services...")
    finally:
        # Graceful Shutdown
        backend_process.terminate()
        frontend_process.terminate()
        backend_process.wait()
        frontend_process.wait()
        print("Goodbye.")

if __name__ == "__main__":
    start_system()
