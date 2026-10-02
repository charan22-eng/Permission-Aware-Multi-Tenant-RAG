import json
import os

def check():
    items_found = 0
    if os.path.exists("README.md"):
        with open("README.md", "r") as f:
            content = f.read()
            if "Q0 and Q2" in content: items_found += 1
            if "numeric veto" in content: items_found += 1
            if "tuned on a small set" in content: items_found += 1
            if "one-fact-per-chunk" in content: items_found += 1
            if "spelled-out numbers" in content: items_found += 1
            
    measured = {
        "items_found": items_found
    }
    print("RESULT_JSON: " + json.dumps({"measured": measured, "notes": ""}))

if __name__ == "__main__":
    check()
