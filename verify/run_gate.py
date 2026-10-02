import argparse
import json
import yaml
import subprocess
import sys
import os
import time
import hashlib
from datetime import datetime, timezone

def read_gates():
    with open('verify/gates.yaml', 'r') as f:
        return yaml.safe_load(f)

def run_check_frozen():
    if not os.path.exists("eval/FROZEN.md"):
        return True
    res = subprocess.run([sys.executable, "verify/check_frozen.py"], capture_output=True, text=True)
    return res.returncode == 0

def get_git_head():
    try:
        res = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except:
        return "unknown"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("gate_id")
    args = parser.parse_args()
    
    gates = read_gates()
    gate = next((g for g in gates if g["id"] == args.gate_id), None)
    
    if not gate:
        print(f"Gate {args.gate_id} not found in verify/gates.yaml")
        sys.exit(1)
        
    phase = gate["phase"]
    evidence_dir = f"docs/evidence/phase{phase}"
    os.makedirs(evidence_dir, exist_ok=True)
    
    utc_now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    evidence_file = f"{evidence_dir}/{args.gate_id}__{utc_now}.txt"
    results_file = f"docs/evidence/results/{args.gate_id}.json"
    os.makedirs("docs/evidence/results", exist_ok=True)
    
    frozen_ok = run_check_frozen()
    
    command = gate["command"]
    cmd_args = command.split()
    
    print(f"Running {command}...")
    res = subprocess.run(cmd_args, capture_output=True, text=True)
    
    with open(evidence_file, "w") as f:
        f.write("COMMAND: " + command + "\n")
        f.write("STDOUT:\n" + res.stdout + "\n")
        f.write("STDERR:\n" + res.stderr + "\n")
        f.write("EXIT_CODE: " + str(res.returncode) + "\n")
        
    with open(evidence_file, "rb") as f:
        evidence_sha256 = hashlib.sha256(f.read()).hexdigest()
        
    with open("docs/evidence/MANIFEST.txt", "a") as f:
        size = os.path.getsize(evidence_file)
        f.write(f"{evidence_sha256}\t{size}\t{evidence_file}\n")
        
    # parse RESULT_JSON
    measured = None
    notes = ""
    status = "ERROR"
    
    if res.returncode == 0:
        for line in res.stdout.split("\n"):
            if line.startswith("RESULT_JSON:"):
                try:
                    data = json.loads(line.replace("RESULT_JSON:", "").strip())
                    measured = data.get("measured", {})
                    notes = data.get("notes", "")
                    
                    if not frozen_ok:
                        status = "FAIL"
                        notes = "FROZEN-CHANGED"
                    else:
                        rule = gate["rule"]
                        if rule == "produced" or rule.startswith("produced or BLOCKED"):
                            status = "PASS"
                        elif rule == "true":
                            status = "PASS" if all(measured.values()) else "FAIL"
                        elif rule == "all true":
                            status = "PASS" if all(measured.values()) else "FAIL"
                        elif rule == "both true":
                            status = "PASS" if all(measured.values()) else "FAIL"
                        else:
                            try:
                                passed = eval(rule, {"measured": measured}, {})
                                status = "PASS" if passed else "FAIL"
                            except Exception as e:
                                notes = f"Rule eval error: {e}"
                                status = "ERROR"
                except json.JSONDecodeError:
                    status = "ERROR"
                    notes = "Could not parse RESULT_JSON"
                break
    else:
        status = "ERROR"
        notes = "Command crashed or exited non-zero"
        
    # Read preflight.json if exists for ollama models and python
    python_ver = sys.version.split()[0]
    ollama_models = []
    if os.path.exists("docs/evidence/preflight.json"):
        with open("docs/evidence/preflight.json", "r") as f:
            pf = json.load(f)
            python_ver = pf.get("python", python_ver)
            ollama_models = pf.get("ollama_models", [])
            
    result_doc = {
        "gate": args.gate_id,
        "phase": phase,
        "type": gate["type"],
        "status": status,
        "measured": measured,
        "rule": gate["rule"],
        "evidence_file": evidence_file,
        "evidence_sha256": evidence_sha256,
        "git_head": get_git_head(),
        "utc": datetime.now(timezone.utc).isoformat(),
        "python": python_ver,
        "ollama_models": ollama_models,
        "notes": notes
    }
    
    with open(results_file, "w") as f:
        json.dump(result_doc, f, indent=2)
        
    print(f"Gate {args.gate_id} completed with status {status}")

if __name__ == "__main__":
    main()
