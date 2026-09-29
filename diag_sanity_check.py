import json
import re
from openai import OpenAI
import time

llm = OpenAI(api_key='ollama', base_url='http://localhost:11434/v1')

PROMPT_OLD = """You are an expert evaluator. Evaluate the student's answer against the reference answer.
Question: {q}
Reference Answer: {gt}
Student Answer: {ans}

Is the student's answer correct and factually consistent with the reference answer?
Respond with ONLY "1" if correct, or "0" if incorrect."""

PROMPT_NEW = """You are an expert evaluator. Evaluate the student's answer against the reference answer.
Question: {q}
Reference Answer: {gt}
Student Answer: {ans}

Is the student's answer correct and factually consistent with the reference answer? Ignore phrasing, sentence fragments, and citation formats. Focus ONLY on whether the key facts match.
Respond with ONLY "1" if correct, or "0" if incorrect."""

PROMPT_FIXED = """You are an expert evaluator. Evaluate the student's answer against the reference answer.
Question: {q}
Reference Answer: {gt}
Student Answer: {ans}

Is the student's answer correct and factually consistent with the reference answer? Ignore phrasing, sentence fragments, and citation formats. 
CRITICAL RULE: Numbers, dates, names, units, and quantities must match the reference exactly. A differing value (e.g., 5% vs 10%) is INCORRECT even if the topic matches.
Respond with ONLY "1" if correct, or "0" if incorrect."""

def extract_key_facts(text: str):
    text_no_pct = text.replace('%', ' percent')
    nums = re.findall(r'\b\d+\b', text_no_pct)
    caps = re.findall(r'\b[A-Z][a-zA-Z]*\b', text)
    stopwords = {'The', 'A', 'An', 'Is', 'Are', 'In', 'On', 'At', 'To', 'From', 'It', 'This', 'That', 'If', 'And', 'Or', 'They', 'We', 'You', 'I'}
    caps = [c for c in caps if c not in stopwords]
    return set(nums + caps)

def deterministic_key_fact_check(ground_truth: str, answer: str) -> int:
    facts = extract_key_facts(ground_truth)
    ans_norm = answer.replace('%', ' percent').lower()
    ans_norm_no_punc = re.sub(r'[^\w\s]', '', ans_norm)
    for f in facts:
        f_norm = f.lower()
        if f_norm not in ans_norm and f_norm not in ans_norm_no_punc:
            return 0
    return 1

def run_judge(model, prompt, q, gt, ans):
    p = prompt.format(q=q, gt=gt, ans=ans)
    res = llm.chat.completions.create(model=model, messages=[{'role': 'user', 'content': p}], temperature=0.0, seed=42)
    val = res.choices[0].message.content.strip()
    return 1 if '1' in val else 0

corruptions_num = {
    0: ("Apex Innovations was founded in 2011 by CEO Alice Smith.", "2010 -> 2011"),
    1: ("The headquarters is located at 456 Innovation Drive, Silicon Valley, CA.", "123 -> 456"),
    4: ("Employees receive 25 days of paid time off per year.", "20 -> 25"),
    7: ("The company offers a 401(k) match up to 10% of the employee's salary.", "5% -> 10%"),
    10: ("Employees can expense up to $600 per year for professional development courses.", "$500 -> $600"),
    12: ("The maternity leave policy includes 14 weeks of fully paid leave.", "12 -> 14"),
    13: ("The paternity leave policy includes 6 weeks of fully paid leave.", "4 -> 6"),
    17: ("Apex Innovations acquired MedTech Solutions in 2019.", "2018 -> 2019"),
    21: ("The employee referral bonus is $3000 for successful hires.", "2000 -> 3000"),
    22: ("The company provides a monthly stipend of $100 for home internet.", "50 -> 100")
}
corruptions_name = {
    0: ("Apex Innovations was founded in 2010 by CEO Bob Smith.", "Alice -> Bob"),
    1: ("The headquarters is located at 123 Innovation Drive, New York, NY.", "Silicon Valley -> New York"),
    2: ("Apex Innovations specializes in AI-driven enterprise solutions for the finance industry.", "healthcare -> finance"),
    3: ("The flagship product is MedAI, launched in 2015.", "HealthAI -> MedAI"),
    14: ("The primary data center is located in Dallas, Texas.", "Ashburn -> Dallas"),
    15: ("The company uses Azure for cloud hosting and services.", "AWS -> Azure"),
    17: ("Apex Innovations acquired HealthTech Inc in 2018.", "MedTech -> HealthTech"),
    18: ("The CTO is Alice Jones, who joined in 2012.", "Bob -> Alice"),
    19: ("The annual company retreat takes place in Aspen every summer.", "Lake Tahoe -> Aspen"),
    24: ("The company dress code is formal.", "business casual -> formal")
}

questions = []
with open('eval/questions.jsonl', 'r') as f:
    for i, line in enumerate(f):
        if i >= 30: break
        questions.append(json.loads(line))

test_cases = []
for i in range(30):
    test_cases.append((questions[i], questions[i]['reference_answer'], "Original"))

for idx, (ans, desc) in corruptions_num.items():
    test_cases.append((questions[idx], ans, f"Num Corrupt: {desc}"))

for idx, (ans, desc) in corruptions_name.items():
    test_cases.append((questions[idx], ans, f"Name Corrupt: {desc}"))

results = []
print("Evaluating 50 test cases...")
for item in test_cases:
    q = item[0]['question']
    gt = item[0]['reference_answer']
    ans = item[1]
    ctype = item[2]
    
    o_llama = run_judge('llama3.1', PROMPT_OLD, q, gt, ans)
    o_qwen = run_judge('qwen2.5:7b', PROMPT_OLD, q, gt, ans)
    n_llama = run_judge('llama3.1', PROMPT_NEW, q, gt, ans)
    n_qwen = run_judge('qwen2.5:7b', PROMPT_NEW, q, gt, ans)
    f_llama = run_judge('llama3.1', PROMPT_FIXED, q, gt, ans)
    f_qwen = run_judge('qwen2.5:7b', PROMPT_FIXED, q, gt, ans)
    det = deterministic_key_fact_check(q, gt, ans)
    
    results.append({
        'q': q, 'gt': gt, 'ans': ans, 'ctype': ctype,
        'o_l': o_llama, 'o_q': o_qwen, 'n_l': n_llama, 'n_q': n_qwen,
        'f_l': f_llama, 'f_q': f_qwen, 'det': det
    })

print("\n--- PASSED CORRUPTED ANSWERS (ANY JUDGE OR DET) ---")
for r in results:
    if "Corrupt" in r['ctype']:
        if r['f_l'] == 1 or r['f_q'] == 1 or r['det'] == 1:
            print(f"\nType: {r['ctype']}")
            print(f"Question: {r['q']}")
            print(f"Reference: {r['gt']}")
            print(f"Corrupted: {r['ans']}")
            print(f"Fixed Llama: {r['f_l']}, Fixed Qwen: {r['f_q']}, Det: {r['det']}")
            print(f"Old Llama: {r['o_l']}, Old Qwen: {r['o_q']}")
            print(f"New Llama: {r['n_l']}, New Qwen: {r['n_q']}")
