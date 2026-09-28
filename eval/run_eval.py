import json
import requests
import pandas as pd
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import answer_correctness
import os
from dotenv import load_dotenv

load_dotenv()

# Map Gemini to OpenAI so Ragas uses Gemini transparently
if os.getenv("GEMINI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = os.getenv("GEMINI_API_KEY")
    os.environ["OPENAI_API_BASE"] = "https://generativelanguage.googleapis.com/v1beta/openai/"
    os.environ["OPENAI_BASE_URL"] = "https://generativelanguage.googleapis.com/v1beta/openai/"

API_URL = os.getenv("API_URL", "http://localhost:8000/query")
EVAL_DATA_PATH = "eval/questions.jsonl"
RESULTS_PATH = "eval/results.csv"

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
                
    # Use only 5 questions to stay within 5 RPM rate limits
    questions = questions[:5]
    ground_truths = ground_truths[:5]
    source_chunk_ids = source_chunk_ids[:5]
                
    answers = []
    retrieved_citations_list = []
    hit_rates = []
    
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
            ans = ""
            citations = []
            
        answers.append(ans)
        retrieved_citations_list.append(citations)
        
        # Calculate retrieval hit rate (1 if ground_truth source_chunk_id is in citations, else 0)
        hit = 1 if source_chunk_ids[i] in citations else 0
        hit_rates.append(hit)
        
    print("Preparing evaluation results...")
    
    data_dict = {
        "question": questions,
        "answer": answers,
        "ground_truth": ground_truths,
        "hit_rate": hit_rates,
        "source_chunk_id": source_chunk_ids,
        "retrieved_chunk_ids": [",".join(c) for c in retrieved_citations_list]
    }
    
    df = pd.DataFrame(data_dict)
    df.to_csv(RESULTS_PATH, index=False)
    
    avg_hit_rate = sum(hit_rates) / len(hit_rates) if hit_rates else 0.0
    
    print("\n--- EVALUATION SUMMARY ---")
    print(f"Total Questions: {len(questions)}")
    print(f"Retrieval Hit Rate (Recall@5): {avg_hit_rate:.2f}")
    print(f"Results saved to {RESULTS_PATH}")
    print("--------------------------\n")

if __name__ == "__main__":
    run_evaluation()
