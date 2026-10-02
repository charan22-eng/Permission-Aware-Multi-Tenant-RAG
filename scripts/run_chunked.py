import argparse
import sys
import os
import json
import time
import subprocess
import psutil
import urllib.request
import importlib

# 3.1 Chunked, resumable job runner

STATE_DIR = ".state"

def acquire_gpu_lock():
    os.makedirs(STATE_DIR, exist_ok=True)
    lock_file = os.path.join(STATE_DIR, "gpu.lock")
    my_pid = os.getpid()
    
    if os.path.exists(lock_file):
        try:
            with open(lock_file, "r") as f:
                lock_data = json.load(f)
            pid = lock_data.get("pid")
            if pid and psutil.pid_exists(pid):
                print(f"GPU lock held by active PID {pid}.")
                return False
            else:
                print(f"Stale lock from PID {pid} found. Taking over.")
        except json.JSONDecodeError:
            print("Corrupt lock file. Taking over.")
            
    with open(lock_file, "w") as f:
        json.dump({"pid": my_pid, "start_time": time.time()}, f)
    return True

def release_gpu_lock():
    lock_file = os.path.join(STATE_DIR, "gpu.lock")
    if os.path.exists(lock_file):
        os.remove(lock_file)

def check_port_8001():
    for conn in psutil.net_connections():
        if conn.laddr.port == 8001 and conn.status == "LISTEN":
            print(f"Port 8001 is already in use by PID {conn.pid}.")
            return False
    return True

def wait_for_health():
    for _ in range(30):
        try:
            with urllib.request.urlopen("http://127.0.0.1:8001/health", timeout=1) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    if "project" in data and "corpus_version" in data:
                        return True
        except:
            pass
        time.sleep(1)
    return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--job", required=True)
    parser.add_argument("--max-seconds", type=int, default=480)
    args = parser.parse_args()

    if not acquire_gpu_lock():
        sys.exit(1)

    server_process = None
    try:
        if not check_port_8001():
            print("Port guard failed.")
            sys.exit(1)

        print("Starting uvicorn server on port 8001...")
        env = os.environ.copy()
        env["OLLAMA_MAX_LOADED_MODELS"] = "1"
        
        server_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--port", "8001"],
            env=env
        )

        if not wait_for_health():
            print("Server failed to reach healthy state.")
            sys.exit(1)
            
        print(f"Loading job: {args.job}")
        sys.path.insert(0, os.path.abspath("."))
        
        # Load the module dynamically
        try:
            job_module = importlib.import_module(f"eval.jobs.{args.job}")
        except ModuleNotFoundError:
            try:
                job_module = importlib.import_module(f"jobs.{args.job}")
            except ModuleNotFoundError:
                job_module = importlib.import_module(args.job)

        done = job_module.run_chunk(max_seconds=args.max_seconds)
        
        if done:
            print("Job complete.")
            sys.exit(0)
        else:
            print("Job chunk finished, more work remains.")
            sys.exit(3)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        if server_process:
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
        release_gpu_lock()

if __name__ == "__main__":
    main()
