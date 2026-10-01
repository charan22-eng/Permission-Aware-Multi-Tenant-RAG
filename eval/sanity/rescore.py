import pandas as pd
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RESULTS_PATH = REPO_ROOT / "eval" / "results_1.csv"

def extract_key_facts(text: str):
    text_no_pct = text.replace('%', ' percent')
    text_no_uuid = re.sub(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}', '', text_no_pct)
    nums = re.findall(r'\b\d+\b', text_no_uuid)
    return set(nums)

def clean_answer(ans: str) -> str:
    ans = re.sub(r'\[[0-9a-fA-F\-]{36}\]', '', ans)
    ans = re.sub(r'According to Chunk ID: [0-9a-fA-F\-]{36},?', '', ans)
    return ans.strip()

def deterministic_key_fact_check(question: str, ground_truth: str, answer: str):
    if ground_truth == "": return 1
    gt_nums = extract_key_facts(ground_truth)
    q_nums = extract_key_facts(question)
    ans_nums = extract_key_facts(answer)
    allowed_nums = gt_nums.union(q_nums)
    num_pass = 1
    for n in ans_nums:
        if n not in allowed_nums:
            num_pass = 0
            break
    return num_pass

df = pd.read_csv(RESULTS_PATH)

if '--dry-run' in sys.argv:
    print(f"Dry run. Path: {RESULTS_PATH}. Row count: {len(df)}")
    sys.exit(0)

old_combined = 0
new_combined = 0
differing_rows = []

for idx, row in df.iterrows():
    if row['source_chunk_id'] == 'unanswerable' or "Error: Rate limit exhausted" in row['answer']:
        continue
    
    q = row['question']
    gt = row['ground_truth']
    raw_ans = row['answer']
    ans = clean_answer(raw_ans)
    
    lo = row['llama_correctness']
    qo = row['qwen_correctness']
    old_det = row['det_correctness'] if 'det_correctness' in row else row['det_numeric_pass'] # in results_1, it was det_correctness which failed heavily
    old_comb = 1 if lo == 1 and qo == 1 and old_det == 1 else 0
    old_combined += old_comb
    
    new_det = deterministic_key_fact_check(q, gt, ans)
    new_comb = 1 if lo == 1 and qo == 1 and new_det == 1 else 0
    new_combined += new_comb
    
    if old_comb != new_comb:
        differing_rows.append((idx, q, raw_ans, old_comb, new_comb))
        
total_answerable = len([r for _, r in df.iterrows() if r['source_chunk_id'] != 'unanswerable'])
print(f"Old Combined Correctness: {old_combined}/{total_answerable} ({(old_combined/total_answerable)*100:.1f}%)")
print(f"New Combined Correctness: {new_combined}/{total_answerable} ({(new_combined/total_answerable)*100:.1f}%)")
print("\nDiffering Rows:")
for diff in differing_rows:
    print(f"Row {diff[0]}: Q: {diff[1][:40]}... Old: {diff[3]}, New: {diff[4]}")
