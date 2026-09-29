import json

unanswerable = [
    {'question': 'What is the CEO\'s favorite color?', 'reference_answer': 'I don\'t know.', 'source_chunk_id': 'unanswerable'},
    {'question': 'How much does the HealthAI product cost per year?', 'reference_answer': 'I don\'t know.', 'source_chunk_id': 'unanswerable'},
    {'question': 'Are pets allowed in the Silicon Valley office?', 'reference_answer': 'I don\'t know.', 'source_chunk_id': 'unanswerable'},
    {'question': 'What is the WiFi password for the guest network?', 'reference_answer': 'I don\'t know.', 'source_chunk_id': 'unanswerable'},
    {'question': 'Who won the Apex Innovations ping pong tournament in 2021?', 'reference_answer': 'I don\'t know.', 'source_chunk_id': 'unanswerable'},
    {'question': 'Does the company offer a 4-day work week permanently?', 'reference_answer': 'I don\'t know.', 'source_chunk_id': 'unanswerable'},
    {'question': 'What is the stock ticker symbol for Apex Innovations?', 'reference_answer': 'I don\'t know.', 'source_chunk_id': 'unanswerable'},
    {'question': 'How many employees work at the London regional office?', 'reference_answer': 'I don\'t know.', 'source_chunk_id': 'unanswerable'},
    {'question': 'Who was the CEO before Alice Smith?', 'reference_answer': 'I don\'t know.', 'source_chunk_id': 'unanswerable'},
    {'question': 'What brand of coffee is provided in the break room?', 'reference_answer': 'I don\'t know.', 'source_chunk_id': 'unanswerable'}
]

with open('eval/questions.jsonl', 'a') as f:
    for item in unanswerable:
        f.write(json.dumps(item) + '\n')
