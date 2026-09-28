import json
import requests
import pandas as pd
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import answer_correctness
import os

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
        
    print("Preparing RAGAS evaluation...")
    # Ragas answer_correctness expects 'question', 'answer', 'ground_truth'
    # Some older versions might expect 'ground_truths' as a list of strings for each row
    data_dict = {
        "question": questions,
        "answer": answers,
        "ground_truth": ground_truths
    }
    
    dataset = Dataset.from_dict(data_dict)
    
    print("Running RAGAS answer_correctness metric...")
    result = evaluate(
        dataset,
        metrics=[answer_correctness]
    )
    
    ragas_df = result.to_pandas()
    
    # Add our hit_rate and source citations back to the dataframe
    ragas_df["hit_rate"] = hit_rates
    ragas_df["source_chunk_id"] = source_chunk_ids
    ragas_df["retrieved_chunk_ids"] = [",".join(c) for c in retrieved_citations_list]
    
    ragas_df.to_csv(RESULTS_PATH, index=False)
    
    avg_hit_rate = sum(hit_rates) / len(hit_rates)
    # Get mean answer_correctness if available
    avg_correctness = ragas_df["answer_correctness"].mean() if "answer_correctness" in ragas_df.columns else 0.0
    
    print("\n--- EVALUATION SUMMARY ---")
    print(f"Total Questions: {len(questions)}")
    print(f"Retrieval Hit Rate (Recall@5): {avg_hit_rate:.2f}")
    print(f"Average Answer Correctness (RAGAS): {avg_correctness:.2f}")
    print(f"Results saved to {RESULTS_PATH}")
    print("--------------------------\n")

if __name__ == "__main__":
    run_evaluation()
