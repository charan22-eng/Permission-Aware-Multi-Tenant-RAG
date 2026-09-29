import pandas as pd

df = pd.read_csv('eval/results.csv')

# 1. Misses and Failures
print('--- RETRIEVAL MISSES ---')
misses = df[df['hit_rate'] == 0]
for idx, row in misses.iterrows():
    print(f'Q (Index {idx}): {row["question"]}')
    print(f'Ref: {row["ground_truth"]}')
    print(f'Retrieved Chunks: {row["retrieved_chunk_ids"]}')
    print(f'Generated: {row["answer"]}')
    print(f'Verdict: {row["correctness"]}\n')

print('--- CORRECTNESS FAILURES ---')
failures = df[df['correctness'] == 0]
for idx, row in failures.iterrows():
    print(f'Q (Index {idx}): {row["question"]}')
    print(f'Ref: {row["ground_truth"]}')
    print(f'Retrieved Chunks: {row["retrieved_chunk_ids"]}')
    print(f'Generated: {row["answer"]}')
    print(f'Verdict: {row["correctness"]}\n')

# 2. Random sample of 10 correct
print('--- 10 RANDOM CORRECT ---')
correct = df[df['correctness'] == 1]
sample = correct.sample(n=10, random_state=42)
for idx, row in sample.iterrows():
    print(f'Q (Index {idx}): {row["question"]}')
    print(f'Ref: {row["ground_truth"]}')
    print(f'Generated: {row["answer"]}\n')
