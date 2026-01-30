import subprocess
import sys
import os
import time
import signal

def run_system():
    """
    MIRRA System Runner
    Simultaneously starts:
    1. Backend (Uvicorn) on Port 8000
    2. Frontend (Next.js) on Port 3000
    
    Handles Ctrl+C for graceful shutdown of both services.
    """
    cwd = os.getcwd()
    frontend_dir = os.path.join(cwd, "frontend")
    
    print(">> MIRRA System Launching...")
    print("------------------------------------------------")
    
    # 1. Start Backend
    print(">> Starting Backend (Port 8000)...")
    backend_cmd = [sys.executable, "-m", "uvicorn", "backend.app.main:app", "--reload", "--port", "8000"]
    backend_process = subprocess.Popen(backend_cmd, cwd=cwd)
    
    # 2. Start Frontend
    print(">> Starting Frontend (Port 4000)...")
    npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
    frontend_cmd = [npm_cmd, "run", "dev"]
    frontend_process = subprocess.Popen(frontend_cmd, cwd=frontend_dir)
    
    print("\n>> SYSTEM ACTIVE")
    print("------------------------------------------------")
    print("Backend API: http://localhost:8000")
    print("Frontend UI: http://localhost:4000")
    print("------------------------------------------------")
    print("(Press Ctrl+C to stop all services)")

    try:
        while True:
            time.sleep(1)
            # Check if processes are still alive
            if backend_process.poll() is not None:
                print("!! Backend process ended unexpectedly.")
                break
            if frontend_process.poll() is not None:
                print("!! Frontend process ended unexpectedly.")
                break
    except KeyboardInterrupt:
        print("\n>> Stopping sequence initiated...")
    finally:
        # Graceful Shutdown
        print("Terminating Backend...")
        if backend_process.poll() is None:
            backend_process.terminate() 
        
        print("Terminating Frontend...")
        if frontend_process.poll() is None:
            # On Windows, terminating the npm shell might need extra handling, but terminate() is standard first attempt
            frontend_process.terminate()
        
        backend_process.wait()
        frontend_process.wait()
        print("Goodbye.")

if __name__ == "__main__":
    run_system()
