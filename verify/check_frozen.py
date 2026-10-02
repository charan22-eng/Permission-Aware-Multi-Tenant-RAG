import sys
import os
import subprocess
import re

def get_git_hash(filepath):
    res = subprocess.run(["git", "hash-object", filepath], capture_output=True, text=True)
    if res.returncode == 0:
        return res.stdout.strip()
    return None

def main():
    if not os.path.exists("eval/FROZEN.md"):
        print("eval/FROZEN.md does not exist.")
        sys.exit(0) # Not frozen yet
        
    with open("eval/FROZEN.md", "r") as f:
        content = f.read()
        
    # Expect lines like:
    # eval/run_eval.py: abcdef123456...
    # or similar parseable format.
    # We will look for anything that looks like a path and a 40-char hash
    mismatches = []
    
    # Simple regex to find path: hash
    matches = re.findall(r'([a-zA-Z0-9_./-]+):\s*([a-f0-9]{40})', content)
    if not matches:
        # Maybe the format was different, try another way or just exit
        pass
        
    for filepath, expected_hash in matches:
        if not os.path.exists(filepath):
            print(f"Missing frozen file: {filepath}")
            mismatches.append(filepath)
            continue
            
        actual_hash = get_git_hash(filepath)
        if actual_hash != expected_hash:
            print(f"Hash mismatch for {filepath}. Expected {expected_hash}, got {actual_hash}")
            mismatches.append(filepath)
            
    if mismatches:
        print("FROZEN CHECK FAILED.")
        sys.exit(1)
        
    print("All frozen files match.")
    sys.exit(0)

if __name__ == "__main__":
    main()
