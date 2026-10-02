import os
import shutil
import tempfile
import subprocess
import sys

MUTATIONS = {
    # We will add mutants here as their code exists
    # "M1": {"file": "app/retrieval.py", "search": "tenant_id == token.tenant_id", "replace": "True", "target": "tests/ci/test_layer1.py"},
}

def apply_mutation(repo_dir, mutant):
    filepath = os.path.join(repo_dir, mutant["file"])
    if not os.path.exists(filepath):
        return False
    with open(filepath, "r") as f:
        content = f.read()
    if mutant["search"] not in content:
        return False
    content = content.replace(mutant["search"], mutant["replace"])
    with open(filepath, "w") as f:
        f.write(content)
    return True

def run_mutations():
    if not MUTATIONS:
        print("No mutations defined yet.")
        return 0, 0
        
    temp_dir = tempfile.mkdtemp(prefix="rag_mut_")
    
    # Copy repo (simplistic ignore)
    def ignore_func(d, files):
        return [f for f in files if f in ('.git', 'docs', 'data', 'eval', 'venv', '__pycache__')]
        
    shutil.copytree(".", temp_dir, dirs_exist_ok=True, ignore=ignore_func)
    
    mutants = len(MUTATIONS)
    behaved_as_expected = 0
    
    for m_id, mutant in MUTATIONS.items():
        # apply
        if apply_mutation(temp_dir, mutant):
            # run test
            res = subprocess.run([sys.executable, "-m", "pytest", mutant["target"]], cwd=temp_dir, capture_output=True, text=True)
            if res.returncode != 0:
                # Failed as expected!
                behaved_as_expected += 1
            else:
                print(f"Mutation {m_id} FAILED to break {mutant['target']}")
        else:
            print(f"Could not apply mutation {m_id}")
            
    shutil.rmtree(temp_dir, ignore_errors=True)
    return mutants, behaved_as_expected

if __name__ == "__main__":
    m, b = run_mutations()
    print(f"Mutants: {m}, Behaved as expected: {b}")
