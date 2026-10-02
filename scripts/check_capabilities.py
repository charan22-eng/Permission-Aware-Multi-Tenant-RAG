import json
import os
import sys

def get_preflight():
    with open("docs/evidence/preflight.json") as f:
        return json.load(f)

def is_blocked(gate_id, preflight):
    # Determine if a gate is blocked by missing capabilities
    qdrant_needed = True # almost everything needs Qdrant
    ollama_needed = False
    neo4j_needed = False
    
    # Identify ollama needed
    if gate_id in ["G0.3", "G0.4", "G0.5", "G0.6", "G0.7", "G0.8", "G0.9", "G0.14"]:
        ollama_needed = True
    if gate_id.startswith("G1.") and int(gate_id[3:]) in [6, 29, 31, 32, 33, 34, 35, 36]:
        ollama_needed = True
    if gate_id.startswith("G2.") and int(gate_id[3:]) in [9, 10, 11, 12, 13, 14, 15, 16, 17, 19, 20]:
        ollama_needed = True
    if gate_id.startswith("G3."):
        if int(gate_id[3:]) in [3, 4, 5, 6, 11, 12, 13, 15, 17]:
            ollama_needed = True
        if int(gate_id[3:]) in [7, 8, 9, 10, 16]:
            neo4j_needed = True
            
    # If qdrant is not reachable
    if qdrant_needed and not preflight.get("docker_running", False):
        return True, "Docker/Qdrant not running"
        
    if ollama_needed and not preflight.get("network_reachability", {}).get("ollama", False) and not preflight.get("has_llama3_1"):
        return True, "Ollama not running"
        
    if neo4j_needed and not preflight.get("neo4j_can_run", False):
        return True, "Neo4j cannot run (Docker/Memory missing)"
        
    return False, ""

def main():
    pass

if __name__ == "__main__":
    main()
