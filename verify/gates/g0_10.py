import json
import subprocess
import os

def check():
    hashes_match = False
    tag_exists = False
    
    res = subprocess.run(["python", "verify/check_frozen.py"], capture_output=True, text=True)
    if "All frozen files match" in res.stdout or "eval/FROZEN.md does not exist" in res.stdout:
        hashes_match = True
        
    tag_res = subprocess.run(["git", "tag", "-l", "eval-v1"], capture_output=True, text=True)
    if "eval-v1" in tag_res.stdout:
        tag_exists = True
        
    measured = {
        "hashes_match": hashes_match,
        "tag_exists": tag_exists
    }
    
    print("RESULT_JSON: " + json.dumps({"measured": measured, "notes": ""}))

if __name__ == "__main__":
    check()
