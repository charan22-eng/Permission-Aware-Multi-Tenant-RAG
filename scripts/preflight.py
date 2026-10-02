import sys
import platform
import subprocess
import json
import shutil
import urllib.request
import os
from datetime import datetime, timezone

def run_cmd(args, check=False):
    try:
        res = subprocess.run(args, capture_output=True, text=True, check=check)
        return {"code": res.returncode, "stdout": res.stdout.strip(), "stderr": res.stderr.strip()}
    except FileNotFoundError:
        return {"code": -1, "stdout": "", "stderr": f"Command not found: {args[0]}"}
    except Exception as e:
        return {"code": -1, "stdout": "", "stderr": str(e)}

def preflight():
    results = {}
    
    # OS & Python
    results["os"] = f"{platform.system()} {platform.release()}"
    results["python"] = sys.version.split()[0]
    
    # Packages
    pkg_res = run_cmd([sys.executable, "-m", "pip", "freeze"])
    results["packages"] = pkg_res["stdout"].split("\n") if pkg_res["code"] == 0 else []
    
    # Git
    status_res = run_cmd(["git", "status", "--porcelain"])
    results["git_clean"] = (status_res["code"] == 0 and len(status_res["stdout"]) == 0)
    head_res = run_cmd(["git", "rev-parse", "HEAD"])
    results["git_head"] = head_res["stdout"] if head_res["code"] == 0 else "unknown"
    
    # Docker
    docker_res = run_cmd(["docker", "info"])
    results["docker_running"] = (docker_res["code"] == 0)
    
    # Qdrant reachable
    try:
        with urllib.request.urlopen("http://localhost:6333", timeout=2) as r:
            results["qdrant_reachable"] = (r.status == 200)
    except:
        results["qdrant_reachable"] = False
        
    # Neo4j capability (Need 1GB heap, let's say >= 4GB total RAM free or something, and Docker)
    mem = shutil.disk_usage("/") # Just checking disk instead of RAM for simplicity unless psutil is present
    try:
        import psutil
        ram_gb = psutil.virtual_memory().total / (1024**3)
        results["neo4j_can_run"] = results["docker_running"] and ram_gb >= 4.0
    except ImportError:
        run_cmd([sys.executable, "-m", "pip", "install", "psutil"])
        try:
            import psutil
            ram_gb = psutil.virtual_memory().total / (1024**3)
            results["neo4j_can_run"] = results["docker_running"] and ram_gb >= 4.0
        except:
            results["neo4j_can_run"] = results["docker_running"] # fallback
            
    # Ollama models
    ollama_list = run_cmd(["ollama", "list"])
    if ollama_list["code"] == 0:
        models = [line.split()[0] for line in ollama_list["stdout"].split("\n")[1:] if line]
        results["ollama_models"] = models
        
        has_small = any("qwen2.5:3b" in m or "llama3.2:3b" in m for m in models)
        if not has_small:
            print("Trying to pull qwen2.5:3b...")
            run_cmd(["ollama", "pull", "qwen2.5:3b"])
            ollama_list = run_cmd(["ollama", "list"])
            models = [line.split()[0] for line in ollama_list["stdout"].split("\n")[1:] if line]
            results["ollama_models"] = models
            
        results["has_llama3_1"] = any("llama3.1" in m for m in models)
        results["has_qwen2_5_7b"] = any("qwen2.5:7b" in m for m in models)
        results["has_small_model"] = any("qwen2.5:3b" in m or "llama3.2:3b" in m for m in models)
    else:
        results["ollama_models"] = []
        results["has_llama3_1"] = False
        results["has_qwen2_5_7b"] = False
        results["has_small_model"] = False

    # GPU info
    nvidia_res = run_cmd(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"])
    results["gpu_info"] = nvidia_res["stdout"] if nvidia_res["code"] == 0 else "None"
    
    # Free disk
    du = shutil.disk_usage("/")
    results["free_disk_gb"] = round(du.free / (1024**3), 2)
    
    # Network reachability
    networks = {"pypi": "https://pypi.org", "ollama": "https://registry.ollama.ai", "hf": "https://huggingface.co"}
    results["network_reachability"] = {}
    for k, url in networks.items():
        try:
            with urllib.request.urlopen(url, timeout=5) as r:
                results["network_reachability"][k] = (r.status == 200)
        except:
            results["network_reachability"][k] = False

    # gh CLI
    gh_res = run_cmd(["gh", "auth", "status"])
    results["gh_cli_present"] = (gh_res["code"] != -1)
    results["gh_authenticated"] = (gh_res["code"] == 0)
    
    # gitleaks
    gitleaks_res = run_cmd(["gitleaks", "version"])
    results["gitleaks_present"] = (gitleaks_res["code"] == 0)
    
    # Playwright / Chromium
    playwright_res = run_cmd([sys.executable, "-m", "playwright", "--version"])
    if playwright_res["code"] != 0:
        run_cmd([sys.executable, "-m", "pip", "install", "playwright"])
        run_cmd([sys.executable, "-m", "playwright", "install", "--with-deps", "chromium"])
        playwright_res = run_cmd([sys.executable, "-m", "playwright", "--version"])
    
    results["playwright_present"] = (playwright_res["code"] == 0)
    
    results["utc"] = datetime.now(timezone.utc).isoformat()
    
    os.makedirs("docs/evidence", exist_ok=True)
    with open("docs/evidence/preflight.json", "w") as f:
        json.dump(results, f, indent=2)
        
    print(f"Preflight completed. Results saved to docs/evidence/preflight.json")

if __name__ == "__main__":
    preflight()
