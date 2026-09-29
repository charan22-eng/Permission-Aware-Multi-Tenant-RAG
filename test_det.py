import re

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

gt = "The company offers a 401(k) match up to 5% of the employee's salary."
ans_corrupted = "The company offers a 10% 401(k) match."

print("Facts:", extract_key_facts(gt))
print("Verdict:", deterministic_key_fact_check(gt, ans_corrupted))
