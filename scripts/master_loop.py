import yaml
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

def read_gates():
    with open('verify/gates.yaml', 'r') as f:
        return yaml.safe_load(f)

def get_preflight():
    with open("docs/evidence/preflight.json") as f:
        return json.load(f)

def check_missing_capabilities(gate, preflight):
    gid = gate["id"]
    # We aggressively block things if docker/ollama is missing
    # because they depend on API or generation.
    needs_docker = True
    
    # Gates that DON'T need docker/API:
    pure_static = ["G0.10", "G0.11", "G0.12", "G0.13", "G1.37", "G1.38", "G1.40", "G3.1", "G4.1", "G4.2", "G4.3", "G4.4", "G4.9", "G4.10", "G4.11", "G4.12"]
    if gid in pure_static:
        needs_docker = False
        
    needs_ollama = False
    if "ollama" in gate.get("title", "").lower() or "llm" in gate.get("title", "").lower() or "hit@5" in gate.get("title", "").lower() or "eval" in gate.get("title", "").lower() or "generation" in gate.get("title", "").lower():
        needs_ollama = True
        
    # Phase 3 Neo4j
    needs_neo4j = False
    if gid.startswith("G3."):
        needs_neo4j = True

    if needs_docker and not preflight.get("docker_running", False):
        return "Docker/Qdrant not running"
    if needs_neo4j and not preflight.get("neo4j_can_run", False):
        return "Neo4j cannot run"
    if needs_ollama and not preflight.get("has_llama3_1", False):
        return "Ollama/llama3.1 not running"
        
    if "gh run list" in gate.get("title", "") and not preflight.get("gh_authenticated", False):
        return "gh CLI not authenticated"

    return None

def mark_blocked(gate, reason, preflight):
    print(f"Marking {gate['id']} BLOCKED: {reason}")
    res = {
        "gate": gate["id"],
        "phase": gate["phase"],
        "type": gate["type"],
        "status": "BLOCKED",
        "measured": None,
        "rule": gate["rule"],
        "evidence_file": None,
        "evidence_sha256": None,
        "git_head": preflight.get("git_head", "unknown"),
        "utc": datetime.now(timezone.utc).isoformat(),
        "python": preflight.get("python", "unknown"),
        "ollama_models": preflight.get("ollama_models", []),
        "notes": f"BLOCKED: {reason}"
    }
    os.makedirs("docs/evidence/results", exist_ok=True)
    with open(f"docs/evidence/results/{gate['id']}.json", "w") as f:
        json.dump(res, f, indent=2)

def main():
    gates = read_gates()
    pf = get_preflight()
    
    # Load STATE
    with open("docs/STATE.json", "r") as f:
        state = json.load(f)
        
    halted = False
    
    for phase in range(5):
        if halted: break
        
        phase_gates = [g for g in gates if g["phase"] == phase]
        if not phase_gates: continue
        
        print(f"\n--- PHASE {phase} ---")
        
        for g in phase_gates:
            reason = check_missing_capabilities(g, pf)
            if reason:
                mark_blocked(g, reason, pf)
                state["gates_blocked"].append(g["id"])
                continue
                
            # Try running the gate
            print(f"Running gate {g['id']}...")
            res = subprocess.run([sys.executable, "verify/run_gate.py", g["id"]])
            
            # Read result
            res_file = f"docs/evidence/results/{g['id']}.json"
            if os.path.exists(res_file):
                with open(res_file) as rf:
                    rdata = json.load(rf)
                st = rdata.get("status")
                
                if st == "PASS":
                    state["gates_done"].append(g["id"])
                elif st == "FAIL" or st == "ERROR":
                    if g["type"] == "HARD":
                        print(f"HARD gate {g['id']} failed! Halting phase.")
                        state["gates_failed"].append(g["id"])
                        state["phase_status"][str(phase)] = "HALTED"
                        halted = True
                        break
                    else:
                        print(f"SOFT/REPORT gate {g['id']} failed. Adding to LIMITATIONS.")
                        os.makedirs("docs", exist_ok=True)
                        with open("docs/LIMITATIONS.md", "a") as lf:
                            lf.write(f"- LIM-{g['id']}: Gate {g['id']} measured value did not meet threshold.\n")
                            
        with open("docs/STATE.json", "w") as f:
            json.dump(state, f, indent=2)
            
        if not halted:
            state["phase_status"][str(phase)] = "DONE"
            print(f"Phase {phase} completed successfully.")
            # tag
            subprocess.run(["git", "tag", f"phase{phase}-done"])
            
    print("\nExecution loop finished.")
    subprocess.run([sys.executable, "scripts/make_results_table.py"])
    subprocess.run([sys.executable, "scripts/check_claims.py"])
    subprocess.run([sys.executable, "scripts/build_status_doc.py"])

if __name__ == "__main__":
    main()
