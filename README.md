# Permission-Aware Multi-Tenant RAG

## Known limitations
- Q0 and Q2 dense-only misses (Q0 improves when the company name is removed, Q2 does not)
- numeric veto is one-directional and passes answers containing no numbers
- judge prompt was tuned on a small set
- the corpus is one-fact-per-chunk so the eval is a regression detector, not proof of quality
- spelled-out numbers are invisible to the numeric check
