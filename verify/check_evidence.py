import sys
import os
import subprocess
import hashlib

def get_first_evidence_commit():
    res = subprocess.run(["git", "log", "--format=%H", "--", "docs/evidence"], capture_output=True, text=True)
    if res.returncode != 0 or not res.stdout.strip():
        return None
    commits = res.stdout.strip().split("\n")
    return commits[-1] # The oldest commit touching docs/evidence

def check_git_history():
    first_commit = get_first_evidence_commit()
    if not first_commit:
        return True # No evidence committed yet
        
    res = subprocess.run(["git", "diff", "--name-status", f"{first_commit}..HEAD", "--", "docs/evidence"], capture_output=True, text=True)
    if res.returncode != 0:
        return False
        
    for line in res.stdout.strip().split("\n"):
        if not line: continue
        status = line[0]
        if status in ('M', 'D'):
            print(f"Evidence file modified or deleted in git history: {line}")
            return False
    return True

def check_manifest_and_sizes():
    manifest_path = "docs/evidence/MANIFEST.txt"
    if not os.path.exists(manifest_path):
        return True
        
    with open(manifest_path, "r") as f:
        lines = f.read().strip().split("\n")
        
    for line in lines:
        if not line: continue
        parts = line.split("\t")
        if len(parts) >= 3:
            expected_hash = parts[0]
            # size is parts[1]
            filepath = parts[2]
            
            if not os.path.exists(filepath):
                print(f"Evidence file missing: {filepath}")
                return False
                
            size = os.path.getsize(filepath)
            if size == 0:
                print(f"Zero-byte evidence file: {filepath}")
                return False
                
            with open(filepath, "rb") as ef:
                actual_hash = hashlib.sha256(ef.read()).hexdigest()
                
            if actual_hash != expected_hash:
                print(f"Hash mismatch for {filepath}. Expected {expected_hash}, got {actual_hash}")
                return False
                
    return True

def main():
    if not check_git_history():
        sys.exit(1)
        
    if not check_manifest_and_sizes():
        sys.exit(1)
        
    print("Evidence check passed.")
    sys.exit(0)

if __name__ == "__main__":
    main()
