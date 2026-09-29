# Project Brief: Permission-Aware Multi-Tenant RAG

## INVARIANTS
- **Project:** permission-aware multi-tenant RAG. Phases: 0 baseline (done), 1 ACL + audit + leakage suite (now), 2 tenant-scoped semantic cache, 3 GraphRAG, 4 README/shipping.
- **Stack:** Python, FastAPI, Qdrant, sentence-transformers (all-MiniLM-L6-v2), SQLite, local Ollama (llama3.1 generator; llama3.1 + qwen2.5:7b judges), temperature=0, seed=42. Machine: Windows, 6GB VRAM. Never run two eval/sanity jobs at once.
- **Eval rules:** never hide failures; fallback/error rows are excluded from metrics and reported separately; report Wilson 95% CIs; k=5 is the pipeline default; never change the baseline silently.
- **Phase 0 numbers to protect:** (Apex, 60 answerable): Hit@5 0.967, Recall@10 1.000, MRR@10 0.933, combined correctness 0.933, abstention 10/10, false abstention 2/60 (Q0 and Q2, known dense-retrieval limitations).
- **Workflow:** Commit and push to origin/main after each verified step.
