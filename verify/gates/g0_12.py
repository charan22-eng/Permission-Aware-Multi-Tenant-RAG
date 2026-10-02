import json
import subprocess
import os

def check():
    res = subprocess.run(["python", "verify/check_evidence.py"], capture_output=True, text=True)
    
    zero_byte = 0
    modified_or_deleted = 0
    
    for line in res.stdout.split("\n"):
        if "Zero-byte" in line:
            zero_byte += 1
        if "modified or deleted" in line:
            modified_or_deleted += 1
            
    measured = {
        "zero_byte": zero_byte,
        "modified_or_deleted": modified_or_deleted
    }
    
    print("RESULT_JSON: " + json.dumps({"measured": measured, "notes": ""}))

if __name__ == "__main__":
    check()
