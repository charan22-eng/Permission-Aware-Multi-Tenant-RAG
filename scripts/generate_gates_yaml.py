import yaml
import hashlib
import os

def parse_gates():
    with open('docs/AGENT_MASTER_PROMPT.md', 'r') as f:
        lines = f.readlines()

    gates = []
    in_table = False
    for line in lines:
        if '| ID | T | Check' in line:
            in_table = True
            continue
        if in_table and line.strip().startswith('|---'):
            continue
        if in_table and not line.strip().startswith('|'):
            in_table = False
            continue
            
        if in_table and line.strip().startswith('| G'):
            parts = [p.strip() for p in line.split('|')[1:-1]]
            if len(parts) >= 4:
                gate_id = parts[0]
                phase = int(gate_id[1])
                g_type = {'H': 'HARD', 'S': 'SOFT', 'R': 'REPORT'}.get(parts[1], parts[1])
                title = parts[2]
                rule = parts[3]
                
                gate = {
                    'id': gate_id,
                    'phase': phase,
                    'type': g_type,
                    'title': title,
                    'command': f'python verify/gates/{gate_id.lower().replace(".", "_")}.py',
                    'rule': rule,
                    'evidence_dir': f'docs/evidence/phase{phase}'
                }
                gates.append(gate)
            
    os.makedirs('verify', exist_ok=True)
    with open('verify/gates.yaml', 'w') as f:
        yaml.dump(gates, f, sort_keys=False)
        
    with open('verify/gates.yaml', 'rb') as f:
        h = hashlib.sha256(f.read()).hexdigest()
        
    os.makedirs('docs/evidence', exist_ok=True)
    with open('docs/evidence/gates_yaml.sha256', 'w') as f:
        f.write(h)
        
    print(f"Generated {len(gates)} gates in verify/gates.yaml")

if __name__ == '__main__':
    parse_gates()
