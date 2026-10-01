import json
import re
import time
import sys
import csv
from openai import OpenAI
import httpx
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PROMPT_PATH = REPO_ROOT / "prompts" / "judge_v3_fixed.txt"
QUESTIONS_PATH = REPO_ROOT / "eval" / "questions.jsonl"
RESULTS_PATH = REPO_ROOT / "eval" / "results_1.csv"
SANITY_ROWS_PATH = REPO_ROOT / "eval" / "sanity" / "sanity_rows.csv"

llm = OpenAI(
    api_key='ollama', 
    base_url='http://localhost:11434/v1',
    timeout=60.0,
    http_client=httpx.Client(timeout=60.0)
)

with open(PROMPT_PATH, 'r', encoding='utf-8') as f:
    PROMPT_FIXED = f.read()

def extract_key_facts(text: str):
    text_no_pct = text.replace('%', ' percent')
    text_no_uuid = re.sub(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}', '', text_no_pct)
    nums = re.findall(r'\b\d+\b', text_no_uuid)
    caps = re.findall(r'\b[A-Z][a-zA-Z]*\b', text)
    stopwords = {'The', 'A', 'An', 'Is', 'Are', 'In', 'On', 'At', 'To', 'From', 'It', 'This', 'That', 'If', 'And', 'Or', 'They', 'We', 'You', 'I'}
    caps = [c for c in caps if c not in stopwords]
    return set(nums), set(caps)

def deterministic_key_fact_check(question: str, ground_truth: str, answer: str):
    if ground_truth == "": return 1, 1
    gt_nums, gt_caps = extract_key_facts(ground_truth)
    q_nums, q_caps = extract_key_facts(question)
    
    required_caps = gt_caps - q_caps
    ans_norm = answer.replace('%', ' percent').lower()
    ans_norm_no_punc = re.sub(r'[^\w\s]', '', ans_norm)
    cap_pass = 1
    for f in required_caps:
        f_norm = f.lower()
        if f_norm not in ans_norm and f_norm not in ans_norm_no_punc:
            cap_pass = 0
            break
            
    ans_nums, _ = extract_key_facts(answer)
    allowed_nums = gt_nums.union(q_nums)
    num_pass = 1
    for n in ans_nums:
        if n not in allowed_nums:
            num_pass = 0
            break
    return num_pass, cap_pass

def clean_answer(ans: str) -> str:
    ans = re.sub(r'\[[0-9a-fA-F\-]{36}\]', '', ans)
    ans = re.sub(r'According to Chunk ID: [0-9a-fA-F\-]{36},?', '', ans)
    return ans.strip()

def run_judge(model, prompt, q, gt, ans):
    p = prompt.replace('{q}', q).replace('{ref}', gt).replace('{ans}', ans)
    for attempt in range(2):
        start_t = time.time()
        try:
            resp = llm.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": p}],
                temperature=0.0,
                seed=42,
                max_tokens=10,
                extra_body={"options": {"num_ctx": 2048}}
            )
            elapsed = time.time() - start_t
            txt = resp.choices[0].message.content.strip()
            print(f"[{model}] call took {elapsed:.2f}s (Tokens: {resp.usage.completion_tokens})", flush=True)
            if '1' in txt: return 1
            if '0' in txt: return 0
            return 0
        except Exception as e:
            elapsed = time.time() - start_t
            print(f"[{model}] LLM Error after {elapsed:.2f}s: {e}", flush=True)
            if "timeout" in str(e).lower():
                return -1 # Timeout error code
            time.sleep(1)
    return -1

# Load questions
questions = []
with open(QUESTIONS_PATH, "r") as f:
    for line in f:
        if line.strip():
            questions.append(json.loads(line))
            
# Create corruptions (first 10 num, next 10 name, next 10 reword)
test_cases = []

# Num
test_cases.append((0, "Apex Innovations was founded in 2011 by CEO Alice Smith.", "NumSwap"))
test_cases.append((1, "The headquarters is located at 456 Innovation Drive, Silicon Valley, CA.", "NumSwap"))
test_cases.append((5, "The company offers a 401(k) match up to 10% of the employee's salary.", "NumSwap"))
test_cases.append((7, "Employees can expense up to $600 per year for professional development courses.", "NumSwap"))
test_cases.append((17, "Apex Innovations acquired MedTech Solutions in 2019.", "NumSwap"))
test_cases.append((21, "The employee referral bonus is $3000 for successful hires.", "NumSwap"))
test_cases.append((22, "The company provides a monthly stipend of $100 for remote workers to cover internet and phone bills.", "NumSwap"))
test_cases.append((28, "Apex Innovations surpassed $200 million in ARR in 2022.", "NumSwap"))
test_cases.append((29, "The Board of Directors consists of 9 members.", "NumSwap"))
test_cases.append((30, "Employees are eligible for a sabbatical after 7 years of continuous service.", "NumSwap"))

# Name
test_cases.append((2, "Apex Innovations specializes in AI-driven enterprise solutions for the finance industry.", "NameSwap"))
test_cases.append((18, "The CTO of Apex Innovations is Charlie Brown, who joined the company in 2015.", "NameSwap"))
test_cases.append((24, "The company dress code is formal.", "NameSwap"))
test_cases.append((25, "The primary communication tool used internally is Microsoft Teams.", "NameSwap"))
test_cases.append((26, "The company intranet is named 'ConnectHub'.", "NameSwap"))
test_cases.append((33, "The Chief Marketing Officer is Jessica Wong.", "NameSwap"))
test_cases.append((38, "The regional offices are located in London, Tokyo, and Paris.", "NameSwap"))
test_cases.append((39, "The company mascot is a dog named 'Rover'.", "NameSwap"))
test_cases.append((45, "The standard project management software used across engineering teams is Asana.", "NameSwap"))
test_cases.append((49, "The VP of Sales is David Lee.", "NameSwap"))

# Reword
test_cases.append((0, "Alice Smith founded the company back in 2010.", "Reword"))
test_cases.append((1, "They are headquartered at 123 Innovation Drive, Silicon Valley, CA.", "Reword"))
test_cases.append((3, "HealthAI is their flagship product, which they launched in 2015.", "Reword"))
test_cases.append((4, "You get 20 days of paid time off per year.", "Reword"))
test_cases.append((5, "Working hours are Monday to Friday, 9 AM to 5 PM.", "Reword"))
test_cases.append((6, "You can work from home 2 days a week.", "Reword"))
test_cases.append((7, "They match up to 5 percent of your salary for 401(k).", "Reword"))
test_cases.append((8, "Reviews happen yearly in November.", "Reword"))
test_cases.append((9, "Inclusion, Integrity, and Innovation are the core values.", "Reword"))
test_cases.append((10, "They give you $500 a year for professional development.", "Reword"))

import pandas as pd
df = pd.read_csv(RESULTS_PATH)
real_answers = []
for idx, row in df.iterrows():
    if row['source_chunk_id'] == 'unanswerable' or "Error" in row['answer']:
        continue
    q_text = row['question']
    gt = row['ground_truth']
    ans = row['answer']
    real_answers.append((q_text, gt, ans, "RealAnswer"))
    
# Gather all evaluations needed
eval_cases = []
for tc in test_cases:
    idx, raw_ans, ctype = tc
    q = questions[idx]['question']
    gt = questions[idx]['reference_answer']
    ans = clean_answer(raw_ans)
    eval_cases.append({'ctype': ctype, 'q': q, 'gt': gt, 'ans': ans, 'idx': idx})
    
real_eval_cases = []
for tc in real_answers:
    q, gt, raw_ans, ctype = tc
    ans = clean_answer(raw_ans)
    if "founded in 2010" in q or "healthcare" in q:
        continue
    real_eval_cases.append({'ctype': ctype, 'q': q, 'gt': gt, 'ans': ans})

if __name__ == '__main__':
    all_cases = eval_cases + real_eval_cases

    if '--dry-run' in sys.argv:
        print(f"Dry run. Loaded {len(all_cases)} items.")
        print(f"Paths: PROMPT={PROMPT_PATH}, QUESTIONS={QUESTIONS_PATH}, RESULTS={RESULTS_PATH}, SANITY_ROWS={SANITY_ROWS_PATH}")
        sys.exit(0)

    print(f"Evaluating {len(all_cases)} items...")
    with open(SANITY_ROWS_PATH, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["ctype", "question", "answer", "llama_f", "qwen_f", "det_num", "comb", "prompt_file"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        print("Running llama-judge evaluations...", flush=True)
        for c in all_cases:
            c['lf'] = run_judge('llama-judge', PROMPT_FIXED, c['q'], c['gt'], c['ans'])

        print("Running qwen-judge evaluations...", flush=True)
        for c in all_cases:
            c['qf'] = run_judge('qwen-judge', PROMPT_FIXED, c['q'], c['gt'], c['ans'])
            
            num_pass, cap_pass = deterministic_key_fact_check(c['q'], c['gt'], c['ans'])
            c['det'] = num_pass
            c['comb'] = 1 if c['lf']==1 and c['qf']==1 and c['det']==1 else 0
            
            writer.writerow({
                "ctype": c['ctype'],
                "question": c['q'],
                "answer": c['ans'],
                "llama_f": c['lf'],
                "qwen_f": c['qf'],
                "det_num": c['det'],
                "comb": c['comb'],
                "prompt_file": "judge_v3_fixed.txt"
            })
            csvfile.flush()

    results = all_cases[:len(eval_cases)]
    real_results = all_cases[len(eval_cases):]

    num_swaps = [r for r in results if r['ctype'] == 'NumSwap']
    name_swaps = [r for r in results if r['ctype'] == 'NameSwap']
    rewords = [r for r in results if r['ctype'] == 'Reword']

    def catch_rate(subset, key):
        return sum(1 for r in subset if r[key] == 0) / len(subset) if subset else 0

    def pass_rate(subset, key):
        return sum(1 for r in subset if r[key] == 1) / len(subset) if subset else 0

    print("\n--- Catch Rates (Score 0) & False Fails (Score 0 on valid) ---")
    print(f"NumSwaps (10) Catch:      LlamaF: {catch_rate(num_swaps, 'lf'):.2f} | QwenF: {catch_rate(num_swaps, 'qf'):.2f} | Det: {catch_rate(num_swaps, 'det'):.2f} | Combined: {catch_rate(num_swaps, 'comb'):.2f}")
    print(f"NameSwaps (10) Catch:     LlamaF: {catch_rate(name_swaps, 'lf'):.2f} | QwenF: {catch_rate(name_swaps, 'qf'):.2f} | Det: {catch_rate(name_swaps, 'det'):.2f} | Combined: {catch_rate(name_swaps, 'comb'):.2f}")
    print(f"Rewords (10) False Fail:  LlamaF: {1-pass_rate(rewords, 'lf'):.2f} | QwenF: {1-pass_rate(rewords, 'qf'):.2f} | Det: {1-pass_rate(rewords, 'det'):.2f} | Combined: {1-pass_rate(rewords, 'comb'):.2f}")
    print(f"Real Ans ({len(real_results)}) False Fail: LlamaF: {1-pass_rate(real_results, 'lf'):.2f} | QwenF: {1-pass_rate(real_results, 'qf'):.2f} | Det: {1-pass_rate(real_results, 'det'):.2f} | Combined: {1-pass_rate(real_results, 'comb'):.2f}")

    print("\n--- Regional Offices Corruption ---")
    for tc in test_cases:
        idx, raw_ans, ctype = tc
        if "regional offices" in questions[idx]['question'].lower():
            print(f"Ref: {questions[idx]['reference_answer']}")
            print(f"Ans: {raw_ans}")
            print("Is it truly wrong? Yes, the reference says London, Tokyo, and Sydney, but the generated corruption swaps Sydney for Paris.")
