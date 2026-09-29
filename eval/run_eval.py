import json
import requests
import pandas as pd
import os
import math
import re
from openai import OpenAI
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_URL = os.getenv("API_URL", "http://localhost:8000/query")
EVAL_DATA_PATH = "eval/questions.jsonl"
RESULTS_PATH = "eval/results.csv"

llm_judge = OpenAI(
    api_key="ollama",
    base_url="http://localhost:11434/v1"
)

def wilson_score_interval(p, n, z=1.96):
    if n == 0:
        return 0.0, 0.0
    denominator = 1 + z**2/n
    centre_adjusted_probability = p + z**2 / (2*n)
    adjusted_standard_deviation = math.sqrt((p*(1 - p) + z**2 / (4*n)) / n)
    lower_bound = (centre_adjusted_probability - z*adjusted_standard_deviation) / denominator
    upper_bound = (centre_adjusted_probability + z*adjusted_standard_deviation) / denominator
    return max(0, lower_bound), min(1, upper_bound)

def clean_answer(ans: str) -> str:
    # Remove all [uuid] markers
    ans = re.sub(r'\[[0-9a-fA-F\-]{36}\]', '', ans)
    # Remove "According to Chunk ID: ..."
    ans = re.sub(r'According to Chunk ID: [0-9a-fA-F\-]{36},?', '', ans)
    return ans.strip()

def extract_key_facts(text: str):
    text_no_pct = text.replace('%', ' percent')
    nums = re.findall(r'\b\d+\b', text_no_pct)
    caps = re.findall(r'\b[A-Z][a-zA-Z]*\b', text)
    stopwords = {'The', 'A', 'An', 'Is', 'Are', 'In', 'On', 'At', 'To', 'From', 'It', 'This', 'That', 'If', 'And', 'Or', 'They', 'We', 'You', 'I'}
    caps = [c for c in caps if c not in stopwords]
    return set(nums + caps)

def deterministic_key_fact_check(question: str, ground_truth: str, answer: str) -> int:
    if ground_truth == "": return 1
    facts = extract_key_facts(ground_truth)
    q_facts = extract_key_facts(question)
    # Remove facts that are already in the question (prevents false positives for short answers)
    facts = facts - q_facts
    
    ans_norm = answer.replace('%', ' percent').lower()
    ans_norm_no_punc = re.sub(r'[^\w\s]', '', ans_norm)
    for f in facts:
        f_norm = f.lower()
        if f_norm not in ans_norm and f_norm not in ans_norm_no_punc:
            return 0
    return 1

def evaluate_correctness(model_name: str, question: str, ground_truth: str, answer: str) -> int:
    if "Error: Rate limit exhausted" in answer or not answer.strip():
        return 0
        
    answer = clean_answer(answer)
    prompt = f"""You are an expert evaluator. Evaluate the student's answer against the reference answer.
Question: {question}
Reference Answer: {ground_truth}
Student Answer: {answer}

Is the student's answer correct and factually consistent with the reference answer? Ignore phrasing, sentence fragments, and citation formats. 
CRITICAL RULE: Numbers, dates, names, units, and quantities must match the reference exactly. A differing value (e.g., 5% vs 10%) is INCORRECT even if the topic matches.
Respond with ONLY "1" if correct, or "0" if incorrect."""
    
    try:
        response = llm_judge.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            seed=42
        )
        result = response.choices[0].message.content.strip()
        if "1" in result:
            return 1
        return 0
    except Exception as e:
        print(f"Eval LLM error for {model_name}: {e}")
        return 0

def run_evaluation():
    questions = []
    ground_truths = []
    source_chunk_ids = []
    
    with open(EVAL_DATA_PATH, "r") as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                questions.append(data["question"])
                ground_truths.append(data["reference_answer"])
                source_chunk_ids.append(data["source_chunk_id"])
                
    answers = []
    retrieved_citations_list = []
    fallback_count = 0
    
    print(f"1. Generating {len(questions)} answers through API...")
    for i, q in enumerate(questions):
        try:
            resp = requests.post(API_URL, json={"query": q, "k": 10})
            resp.raise_for_status()
            res_json = resp.json()
            ans = res_json["answer"]
            citations = res_json["eval_chunk_ids"]
        except Exception as e:
            print(f"Error on question {i}: {e}")
            ans = "Error: Rate limit exhausted or API unavailable."
            citations = []
            
        answers.append(ans)
        retrieved_citations_list.append(citations)
        if "Error: Rate limit exhausted" in ans:
            fallback_count += 1
            
    # Calculate retrieval hit rates
    hit_rates_5 = []
    hit_rates_10 = []
    mrr_10 = []
    
    abstentions = []
    
    for i in range(len(questions)):
        ans_lower = answers[i].lower().replace("’", "'")
        abstention_phrases = [
            "don't know", "do not know", "cannot answer", "not mentioned", 
            "not provided", "not specified", "no information", "couldn't find", 
            "does not contain"
        ]
        
        is_abs = 1 if any(p in ans_lower for p in abstention_phrases) else 0
        abstentions.append(is_abs)
        
        if "Error: Rate limit exhausted" in answers[i]:
            hit_rates_5.append(None)
            hit_rates_10.append(None)
            mrr_10.append(None)
            abstentions[i] = None # ignore errors for abstention rate
        elif source_chunk_ids[i] == "unanswerable":
            hit_rates_5.append(None)
            hit_rates_10.append(None)
            mrr_10.append(None)
        else:
            cits = retrieved_citations_list[i]
            target = source_chunk_ids[i]
            hit_5 = 1 if target in cits[:5] else 0
            hit_10 = 1 if target in cits[:10] else 0
            
            try:
                rank = cits.index(target) + 1
                mrr = 1.0 / rank
            except ValueError:
                mrr = 0.0
                
            hit_rates_5.append(hit_5)
            hit_rates_10.append(hit_10)
            mrr_10.append(mrr)
            
    print("2. Running Judge A (llama3.1)...")
    llama_scores = []
    for i in range(len(questions)):
        if "Error: Rate limit exhausted" in answers[i] or source_chunk_ids[i] == "unanswerable":
            llama_scores.append(None)
        else:
            llama_scores.append(evaluate_correctness("llama3.1", questions[i], ground_truths[i], answers[i]))
            
    print("3. Running Judge B (qwen2.5:7b)...")
    qwen_scores = []
    for i in range(len(questions)):
        if "Error: Rate limit exhausted" in answers[i] or source_chunk_ids[i] == "unanswerable":
            qwen_scores.append(None)
        else:
            qwen_scores.append(evaluate_correctness("qwen2.5:7b", questions[i], ground_truths[i], answers[i]))
            
    print("4. Calculating abstention for unanswerable questions...")
    abstentions = []
    for i in range(len(questions)):
        ans_lower = answers[i].lower().replace("’", "'")
        abstention_phrases = [
            "don't know", "do not know", "cannot answer", "not mentioned", 
            "not provided", "not specified", "no information", "couldn't find", 
            "does not contain"
        ]
        is_abs = 1 if any(p in ans_lower for p in abstention_phrases) else 0
        
        if "Error: Rate limit exhausted" in answers[i]:
            abstentions.append(None)
        else:
            abstentions.append(is_abs)
            
    print("5. Calculating deterministic key fact check...")
    det_scores = []
    combined_scores = []
    for i in range(len(questions)):
        if "Error: Rate limit exhausted" in answers[i] or source_chunk_ids[i] == "unanswerable":
            det_scores.append(None)
            combined_scores.append(None)
        else:
            d = deterministic_key_fact_check(questions[i], ground_truths[i], answers[i])
            det_scores.append(d)
            if llama_scores[i] == 1 and qwen_scores[i] == 1 and d == 1:
                combined_scores.append(1)
            else:
                combined_scores.append(0)
            
    print("Preparing evaluation results...")
    
    metadata_generator = "llama3.1"
    metadata_embedding = "all-MiniLM-L6-v2"
    metadata_chunking = "2000/200"
    metadata_corpus_version = 1
    
    data_dict = {
        "question": questions,
        "answer": answers,
        "ground_truth": ground_truths,
        "hit_rate_5": hit_rates_5,
        "hit_rate_10": hit_rates_10,
        "mrr_10": mrr_10,
        "llama_correctness": llama_scores,
        "qwen_correctness": qwen_scores,
        "det_correctness": det_scores,
        "combined_correctness": combined_scores,
        "is_abstention": abstentions,
        "source_chunk_id": source_chunk_ids,
        "retrieved_chunk_ids": [",".join(c) for c in retrieved_citations_list],
        "generator_model": [metadata_generator] * len(questions),
        "embedding_model": [metadata_embedding] * len(questions),
        "chunk_size_overlap": [metadata_chunking] * len(questions),
        "corpus_version": [metadata_corpus_version] * len(questions),
        "judge_prompt": ["Fixed (exact match numbers/names)"] * len(questions)
    }
    
    df = pd.DataFrame(data_dict)
    df.to_csv(RESULTS_PATH, index=False)
    
    valid_hits_5 = [h for h in hit_rates_5 if h is not None]
    valid_hits_10 = [h for h in hit_rates_10 if h is not None]
    valid_mrr_10 = [m for m in mrr_10 if m is not None]
    
    valid_llama = [c for c in llama_scores if c is not None]
    valid_qwen = [c for c in qwen_scores if c is not None]
    valid_combined = [c for c in combined_scores if c is not None]
    valid_abstentions = [a for a in abstentions if a is not None]
    
    n_valid = len(valid_hits_5)
    n_unanswerable = len([i for i in range(len(questions)) if source_chunk_ids[i] == "unanswerable"])
    
    if n_valid > 0:
        p_hit_5 = sum(valid_hits_5) / n_valid
        p_hit_10 = sum(valid_hits_10) / n_valid
        mrr = sum(valid_mrr_10) / n_valid
        p_llama = sum(valid_llama) / n_valid
        p_qwen = sum(valid_qwen) / n_valid
        p_comb = sum(valid_combined) / n_valid
        
        hit_lower, hit_upper = wilson_score_interval(p_hit_5, n_valid)
        llama_lower, llama_upper = wilson_score_interval(p_llama, n_valid)
        qwen_lower, qwen_upper = wilson_score_interval(p_qwen, n_valid)
        comb_lower, comb_upper = wilson_score_interval(p_comb, n_valid)
        
        agreements = sum(1 for l, q in zip(valid_llama, valid_qwen) if l == q)
        agreement_rate = agreements / n_valid
    else:
        p_hit_5 = p_hit_10 = mrr = p_llama = p_qwen = p_comb = hit_lower = hit_upper = llama_lower = llama_upper = qwen_lower = qwen_upper = comb_lower = comb_upper = agreement_rate = 0.0

    false_abstentions = 0
    for i in range(len(questions)):
        if source_chunk_ids[i] != "unanswerable" and abstentions[i] == 1:
            false_abstentions += 1
    false_abs_rate = false_abstentions / n_valid if n_valid > 0 else 0.0

    unans_abs = sum(1 for i in range(len(questions)) if source_chunk_ids[i] == "unanswerable" and abstentions[i] == 1)
    if n_unanswerable > 0:
        p_abs = unans_abs / n_unanswerable
        abs_lower, abs_upper = wilson_score_interval(p_abs, n_unanswerable)
    else:
        p_abs = abs_lower = abs_upper = 0.0

    print("\n--- EVALUATION SUMMARY ---")
    print(f"Total Questions Evaluated: {len(questions)}")
    print(f"Answerable valid responses: {n_valid}")
    print(f"Unanswerable questions: {n_unanswerable}")
    print(f"Fallback/Failed API Responses: {fallback_count}")
    print(f"Retrieval Hit Rate (Recall@5): {p_hit_5:.3f} (95% CI: [{hit_lower:.3f}, {hit_upper:.3f}])")
    print(f"Retrieval Hit Rate (Recall@10): {p_hit_10:.3f}")
    print(f"Mean Reciprocal Rank (MRR@10): {mrr:.3f}")
    print(f"Llama3.1 Correctness: {p_llama:.3f} (95% CI: [{llama_lower:.3f}, {llama_upper:.3f}])")
    print(f"Qwen2.5:7b Correctness: {p_qwen:.3f} (95% CI: [{qwen_lower:.3f}, {qwen_upper:.3f}])")
    print(f"Combined Correctness (Llama AND Qwen AND Det): {p_comb:.3f} (95% CI: [{comb_lower:.3f}, {comb_upper:.3f}])")
    print(f"Judge Agreement Rate: {agreement_rate:.3f}")
    print(f"Abstention Rate (on unanswerables): {p_abs:.3f} (95% CI: [{abs_lower:.3f}, {abs_upper:.3f}])")
    print(f"False Abstention Rate (on answerables): {false_abs_rate:.3f} ({false_abstentions}/{n_valid})")
    print(f"Results saved to {RESULTS_PATH}")
    print("--------------------------\n")

if __name__ == "__main__":
    run_evaluation()
