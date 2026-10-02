import json
import subprocess

def check():
    res = subprocess.run(["git", "diff", "--name-only", "e0d55b5..HEAD", "--", "eval/run_eval.py", "prompts/judge_v3_fixed.txt", "eval/sanity/heldout_sanity.jsonl"], capture_output=True, text=True)
    
    changed = []
    if res.returncode == 0:
        changed = [f for f in res.stdout.strip().split("\n") if f]
        
    measured = {
        "changed_files": changed
    }
    
    print("RESULT_JSON: " + json.dumps({"measured": measured, "notes": ""}))

if __name__ == "__main__":
    check()
