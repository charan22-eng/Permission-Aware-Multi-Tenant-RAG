import json
import requests
import pandas as pd
import os
from openai import OpenAI

API_URL = os.getenv("API_URL", "http://localhost:8000/query")
EVAL_DATA_PATH = "eval/questions.jsonl"
RESULTS_PATH = "eval/results.csv"

# LLM Judge setup via Ollama OpenAI-compatible endpoint
llm_judge = OpenAI(
    api_key="ollama",
    base_url="http://localhost:11434/v1"
)

def evaluate_correctness(question: str, ground_truth: str, answer: str) -> int:
    """Uses a local LLM to score if the answer matches the ground truth (0 or 1)."""
    if "Error: Rate limit exhausted" in answer or not answer.strip():
        return 0
        
    prompt = f"""You are an expert evaluator. Evaluate the student's answer against the reference answer.
Question: {question}
Reference Answer: {ground_truth}
Student Answer: {answer}

Is the student's answer correct and factually consistent with the reference answer?
Respond with ONLY "1" if correct, or "0" if incorrect."""
    
    try:
        response = llm_judge.chat.completions.create(
            model="llama3.1",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )
        result = response.choices[0].message.content.strip()
        if "1" in result:
            return 1
        return 0
    except Exception as e:
        print(f"Eval LLM error: {e}")
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
    hit_rates = []
    correctness_scores = []
    fallback_count = 0
    
    print(f"Running {len(questions)} questions through {API_URL}...")
    for i, q in enumerate(questions):
        try:
            resp = requests.post(API_URL, json={"query": q})
            resp.raise_for_status()
            res_json = resp.json()
            ans = res_json["answer"]
            citations = res_json["citations"]
        except Exception as e:
            print(f"Error on question {i}: {e}")
            ans = "Error: Rate limit exhausted or API unavailable."
            citations = []
            
        answers.append(ans)
        retrieved_citations_list.append(citations)
        
        # Check for fallback
        if "Error: Rate limit exhausted" in ans:
            fallback_count += 1
            hit_rates.append(None)
            correctness_scores.append(None)
            continue
            
        # Calculate retrieval hit rate (1 if ground_truth source_chunk_id is in citations, else 0)
        hit = 1 if source_chunk_ids[i] in citations else 0
        hit_rates.append(hit)
        
        # Calculate answer correctness via LLM judge
        correctness = evaluate_correctness(q, ground_truths[i], ans)
        correctness_scores.append(correctness)
        
    print("Preparing evaluation results...")
    
    data_dict = {
        "question": questions,
        "answer": answers,
        "ground_truth": ground_truths,
        "hit_rate": hit_rates,
        "correctness": correctness_scores,
        "source_chunk_id": source_chunk_ids,
        "retrieved_chunk_ids": [",".join(c) for c in retrieved_citations_list]
    }
    
    df = pd.DataFrame(data_dict)
    df.to_csv(RESULTS_PATH, index=False)
    
    # Calculate metrics, ignoring fallbacks
    valid_hits = [h for h in hit_rates if h is not None]
    valid_correct = [c for c in correctness_scores if c is not None]
    
    avg_hit_rate = sum(valid_hits) / len(valid_hits) if valid_hits else 0.0
    avg_correctness = sum(valid_correct) / len(valid_correct) if valid_correct else 0.0
    
    print("\n--- EVALUATION SUMMARY ---")
    print(f"Total Questions Evaluated: {len(questions)}")
    print(f"Valid Responses: {len(valid_hits)}")
    print(f"Fallback/Failed Responses: {fallback_count}")
    print(f"Retrieval Hit Rate (Recall@5): {avg_hit_rate:.2f} ({sum(valid_hits)}/{len(valid_hits)})")
    print(f"Answer Correctness Score: {avg_correctness:.2f} ({sum(valid_correct)}/{len(valid_correct)})")
    print(f"Results saved to {RESULTS_PATH}")
    print("--------------------------\n")

if __name__ == "__main__":
    run_evaluation()
