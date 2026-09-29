# Permission-Aware Multi-Tenant RAG

A defense-in-depth, permission-aware multi-tenant RAG system built for secure AI interactions.

## Results

| TBD | TBD | TBD |

## Known Limitations (Phase 0)
- **Dense Retrieval on Pronouns:** Q0 and Q2 failed to retrieve the correct chunks because the ground truth chunks use pronouns ("The company", "We") instead of the explicit company name ("Apex Innovations"). 
  - Q0 improves significantly (Rank 1) when the company name is removed from the query.
  - Q2 does not improve (Rank 18) because the chunk lacks strong semantic overlap beyond "healthcare".
  - This highlights the limitation of dense-only retrieval on short, pronoun-heavy chunks without metadata or contextual augmentation.
