import json
import csv
from run_final_sanity import run_judge, deterministic_key_fact_check, PROMPT_FIXED

heldout_cases = []
with open("eval/heldout_sanity.jsonl", "r") as f:
    for line in f:
        if line.strip():
            heldout_cases.append(json.loads(line))

print("Running llama-judge...", flush=True)
for c in heldout_cases:
    c['lf'] = run_judge('llama-judge', PROMPT_FIXED, c['question'], c['reference_answer'], c['generated_answer'])

print("Running qwen-judge...", flush=True)
for c in heldout_cases:
    c['qf'] = run_judge('qwen-judge', PROMPT_FIXED, c['question'], c['reference_answer'], c['generated_answer'])

results = []
for c in heldout_cases:
    q = c['question']
    gt = c['reference_answer']
    ans = c['generated_answer']
    ctype = c['corruption_type']
    
    det, _ = deterministic_key_fact_check(q, gt, ans)
    comb = 1 if c['lf']==1 and c['qf']==1 and det==1 else 0
    results.append({'ctype': ctype, 'lf': c['lf'], 'qf': c['qf'], 'det': det, 'comb': comb})

def metrics(ctype_filter):
    subset = [r for r in results if r['ctype'] == ctype_filter]
    if not subset: return {}
    return {
        'lf_catch': sum(1 for r in subset if r['lf'] == 0) / len(subset),
        'qf_catch': sum(1 for r in subset if r['qf'] == 0) / len(subset),
        'det_catch': sum(1 for r in subset if r['det'] == 0) / len(subset),
        'comb_catch': sum(1 for r in subset if r['comb'] == 0) / len(subset)
    }

print("--- Held-out Sanity Metrics ---")
for ctype in set(r['ctype'] for r in results):
    m = metrics(ctype)
    # If it's a reword or valid answer, we care about false-fail (catch rate = false fail)
    print(f"{ctype}: LlamaF {m['lf_catch']:.2f}, QwenF {m['qf_catch']:.2f}, Det {m['det_catch']:.2f}, Combined {m['comb_catch']:.2f}")
