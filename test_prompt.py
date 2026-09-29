from openai import OpenAI

llm_judge = OpenAI(
    api_key='ollama',
    base_url='http://localhost:11434/v1'
)

q = 'Who is the VP of Sales?'
gt = 'The VP of Sales is Michael Chang.'
ans = 'Michael Chang [3d82f1c4-3413-402c-bcd9-0ad01d6f7ddf].'

old_prompt = f"""You are an expert evaluator. Evaluate the student's answer against the reference answer.
Question: {q}
Reference Answer: {gt}
Student Answer: {ans}

Is the student's answer correct and factually consistent with the reference answer?
Respond with ONLY "1" if correct, or "0" if incorrect."""

new_prompt = f"""You are an expert evaluator. Evaluate the student's answer against the reference answer.
Question: {q}
Reference Answer: {gt}
Student Answer: {ans}

Is the student's answer correct and factually consistent with the reference answer? Ignore phrasing, sentence fragments, and citation formats. Focus ONLY on whether the key facts match.
Respond with ONLY "1" if correct, or "0" if incorrect."""

res_old = llm_judge.chat.completions.create(model='llama3.1', messages=[{'role': 'user', 'content': old_prompt}], temperature=0.0, seed=42)
res_new = llm_judge.chat.completions.create(model='llama3.1', messages=[{'role': 'user', 'content': new_prompt}], temperature=0.0, seed=42)

print(f'Old Prompt Result (Q49): {res_old.choices[0].message.content.strip()}')
print(f'New Prompt Result (Q49): {res_new.choices[0].message.content.strip()}')
