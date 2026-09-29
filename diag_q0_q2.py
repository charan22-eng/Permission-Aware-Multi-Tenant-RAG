from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

qdrant = QdrantClient(path='qdrant_storage')
model = SentenceTransformer('all-MiniLM-L6-v2')

q0_orig = 'When was Apex Innovations founded and by whom?'
q0_new = 'When was the company founded and by whom?'
gt0_id = '6cab9edc-d62e-4eaf-9f79-f3b2f5d5034c'

q2_orig = 'What industry does Apex Innovations specialize in?'
q2_new = 'What industry does the company specialize in?'
gt2_id = 'a3b3453c-d77a-48da-a12e-e4fe6be6ae9f'

# Fetch chunk texts
res0 = qdrant.retrieve(collection_name='chunks', ids=[gt0_id])[0].payload['text']
res2 = qdrant.retrieve(collection_name='chunks', ids=[gt2_id])[0].payload['text']

print(f'GT0 Text: {res0}')
print(f'Contains Apex Innovations? {"Apex Innovations" in res0}')
print(f'GT2 Text: {res2}')
print(f'Contains Apex Innovations? {"Apex Innovations" in res2}')

for q, gt_id in [(q0_new, gt0_id), (q2_new, gt2_id)]:
    vec = model.encode(q).tolist()
    points = qdrant.query_points(collection_name='chunks', query=vec, limit=50).points
    rank = next((i+1 for i, p in enumerate(points) if p.id == gt_id), -1)
    score = next((p.score for p in points if p.id == gt_id), -1)
    print(f'Query: {q}')
    print(f'Rank: {rank}, Score: {score:.3f}')
