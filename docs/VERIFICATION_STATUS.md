# Verification Status
**Commit:** 324c62cc36a4724c7b76d7ef7c7a52c3301a055d
**Tags:** phase0-done
phase1-done
phase2-done
phase3-done
**Date:** 2026-10-02T11:47:45.931686+00:00
**Machine OS:** Windows 10
**Python:** 3.11.9
**Gates Hash:** af888fd0f90b1d6f3809bdd9c933a40e35e4ef0316fee8a157043612093aad1d

## Verdict: HALTED AT PHASE 0 (gate G0.1)
Overall: {'PASS': 3, 'FAIL': 0, 'BLOCKED': 90, 'ERROR': 8, 'NOT-RUN': 3}
HARD vs SOFT: {'HARD': 47, 'SOFT': 49}

### Phase 0
| Gate | Type | Status | Measured | Rule | Evidence | Hash | Notes |
|---|---|---|---|---|---|---|---|
| G0.1 | HARD | BLOCKED | `null` | `both true` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G0.2 | HARD | BLOCKED | `null` | `listeners==1` and `pid_is_ours` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G0.3 | SOFT | BLOCKED | `null` | `rows==70 and diff_rows==0 and errors==0`; if it fails, record `noise_floor_questions=diff_rows` and treat any later delta of that size as noise` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G0.4 | SOFT | BLOCKED | `null` | `hit5>=0.93 and recall10>=0.97` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G0.5 | SOFT | BLOCKED | `null` | `combined>=0.90`; differing rows vs the earlier 0.967 run listed in evidence` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G0.6 | SOFT | BLOCKED | `null` | `number_swap_negation_catch>=9 and reword_false_fail<=1` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G0.7 | SOFT | BLOCKED | `null` | `rows_nonempty and number_swap_catch>=9 and reword_false_fail<=2 and numeric_false_fail_rate_valid<0.05` (denominator excludes Q0 and Q2)` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G0.8 | SOFT | BLOCKED | `null` | `judge_processor=="100% GPU" and judge_context==2048` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G0.9 | SOFT | BLOCKED | `null` | `abstain>=9 and false_abstain<=2`; each non-abstained answer is classified by qwen as supported or unsupported and listed` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G0.10 | HARD | BLOCKED | `null` | `both true` | None | unknown | BLOCKED: Ollama/llama3.1 not running |
| G0.11 | SOFT | PASS | `{"items_found": 5}` | `items_found==5` | docs/evidence/phase0/G0.11__20261002T114725Z.txt | 6a61c07e |  |
| G0.12 | HARD | PASS | `{"zero_byte": 0, "modified_or_deleted": 0}` | `both 0` | docs/evidence/phase0/G0.12__20261002T114725Z.txt | 7352717d |  |
| G0.13 | HARD | PASS | `{"changed_files": []}` | `empty list (otherwise follow step 2 and document)` | docs/evidence/phase0/G0.13__20261002T114726Z.txt | 6f9cf600 |  |
| G0.14 | SOFT | BLOCKED | `null` | `<=2` | None | unknown | BLOCKED: Docker/Qdrant not running |

### Phase 1
| Gate | Type | Status | Measured | Rule | Evidence | Hash | Notes |
|---|---|---|---|---|---|---|---|
| G1.1 | HARD | BLOCKED | `null` | `true` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G1.2 | SOFT | BLOCKED | `null` | `==0` (else each listed with reason)` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G1.3 | HARD | BLOCKED | `null` | `missing_fields==0` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G1.4 | HARD | BLOCKED | `null` | `refused and stored==0` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G1.5 | HARD | BLOCKED | `null` | `equal` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G1.6 | SOFT | BLOCKED | `null` | `misses_subset_of_q0_q2 and hit5>=0.93 and combined>=0.90` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G1.7 | HARD | BLOCKED | `null` | `rejected_401==cases and generic_body` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G1.8 | HARD | BLOCKED | `null` | `both true` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G1.9 | SOFT | BLOCKED | `null` | `== number of personas in tenants.yaml` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G1.10 | HARD | BLOCKED | `null` | `both true` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G1.11 | HARD | BLOCKED | `null` | `leaks==0 and alerts>0` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G1.12 | HARD | BLOCKED | `null` | `both true` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G1.13 | HARD | BLOCKED | `null` | `true` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G1.14 | HARD | BLOCKED | `null` | `==0` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G1.15 | HARD | BLOCKED | `null` | `all true` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G1.16 | HARD | BLOCKED | `null` | `0, 0, true, true` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G1.17 | HARD | BLOCKED | `null` | `all true` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G1.18 | HARD | BLOCKED | `null` | `null_fields==0 and traces_found_rate==1.0` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G1.19 | HARD | BLOCKED | `null` | `all true` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G1.20 | SOFT | BLOCKED | `null` | `apex: 60 facts public/internal + 6 new docs + 1 injection doc; northwind and helix: about 10 docs each across public, internal, confidential (>=3 each class)` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G1.21 | SOFT | BLOCKED | `null` | `shared_topics>=5 and shared_names>=2` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G1.22 | HARD | BLOCKED | `null` | `with_canary==confidential_docs and duplicates==0 and canary_in_nonconfidential==0` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G1.23 | SOFT | BLOCKED | `null` | `both true` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G1.24 | SOFT | BLOCKED | `null` | `>=150` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G1.25 | HARD | BLOCKED | `null` | `all 0 (leak = any canary or forbidden chunk ID)` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G1.26 | HARD | BLOCKED | `null` | `rejected==cases` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G1.27 | HARD | BLOCKED | `null` | `==0` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G1.28 | HARD | BLOCKED | `null` | `==0` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G1.29 | HARD | BLOCKED | `null` | `foreign_canary_leaks==0` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G1.30 | HARD | BLOCKED | `null` | `behaved_as_expected==mutants and workflow_valid` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G1.31 | SOFT | BLOCKED | `null` | `per_tenant_min>=20 and gt_found_rate==1.0`; also report apex/employee 60-question hit@5 on `chunks_mt` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G1.32 | SOFT | BLOCKED | `null` | `count>=20 and acl_violations==0` (each question's answer fact exists only in documents the persona cannot access, checked by the ACL function)` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G1.33 | HARD | BLOCKED | `null` | `==0` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G1.34 | REPORT | BLOCKED | `null` | `produced` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G1.35 | REPORT | BLOCKED | `null` | `n>=200` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G1.36 | SOFT | BLOCKED | `null` | `==0` (else record noise floor)` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G1.37 | SOFT | ERROR | `null` | `has Assets, Actors, Trust boundaries, Attack table, Residual risks (token role-change lag, writable ACL table and droppable triggers, audit log is itself sensitive), OWASP names with edition note` | docs/evidence/phase1/G1.37__20261002T114726Z.txt | 83bbd899 | Command crashed or exited non-zero |
| G1.38 | SOFT | ERROR | `null` | `section present and `>=3` residual risks` | docs/evidence/phase1/G1.38__20261002T114726Z.txt | 7e5db4e7 | Command crashed or exited non-zero |
| G1.39 | HARD | BLOCKED | `null` | `both identical true` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G1.40 | SOFT | ERROR | `null` | `==0` | docs/evidence/phase1/G1.40__20261002T114727Z.txt | 69c0734c | Command crashed or exited non-zero |

### Phase 2
| Gate | Type | Status | Measured | Rule | Evidence | Hash | Notes |
|---|---|---|---|---|---|---|---|
| G2.1 | HARD | BLOCKED | `null` | `true` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G2.2 | HARD | BLOCKED | `null` | `0, true` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G2.3 | HARD | BLOCKED | `null` | `0, true` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G2.4 | HARD | BLOCKED | `null` | `0, true, true` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G2.5 | HARD | BLOCKED | `null` | `==0` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G2.6 | HARD | BLOCKED | `null` | `==0` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G2.7 | HARD | BLOCKED | `null` | `==0` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G2.8 | HARD | BLOCKED | `null` | `==0` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G2.9 | SOFT | BLOCKED | `null` | `false_hits_at_chosen==0 and sweep_complete` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G2.10 | SOFT | BLOCKED | `null` | `>=50, >=50, >=10, >=10, true` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G2.11 | SOFT | BLOCKED | `null` | `accuracy_test>=0.80 and dev_test_separated` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G2.12 | REPORT | BLOCKED | `null` | `produced (BLOCKED if no small model)` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G2.13 | SOFT | BLOCKED | `null` | `repeat_fraction>=0.5 and sequential and same_questions` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G2.14 | SOFT | BLOCKED | `null` | `cost_reduction_pct_simulated>=20 and labeled_simulated` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G2.15 | SOFT | BLOCKED | `null` | `p95_change_pct<=0` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G2.16 | SOFT | BLOCKED | `null` | `quality_delta_ci_low>=-0.10` (10-point non-inferiority margin)` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G2.17 | HARD | BLOCKED | `null` | `leaks==0 and mutants_ok` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G2.18 | SOFT | BLOCKED | `null` | `panels_with_data==6 and png_exists` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G2.19 | SOFT | BLOCKED | `null` | `==0` (else record noise floor)` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G2.20 | SOFT | BLOCKED | `null` | `phase1_leaks==0 and hit5_within_ci` | None | unknown | BLOCKED: Docker/Qdrant not running |

### Phase 3
| Gate | Type | Status | Measured | Rule | Evidence | Hash | Notes |
|---|---|---|---|---|---|---|---|
| G3.1 | SOFT | BLOCKED | `null` | `source in {"hotpotqa","FALLBACK-SYNTHETIC"} and n>=30 and license_noted` | None | unknown | BLOCKED: Neo4j cannot run |
| G3.2 | SOFT | BLOCKED | `null` | `both true` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G3.3 | REPORT | BLOCKED | `null` | `produced` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G3.4 | REPORT | BLOCKED | `null` | `produced (BLOCKED if reranker unavailable)` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G3.5 | SOFT | BLOCKED | `null` | `valid_rate>=0.95 and cached_jsonl` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G3.6 | SOFT | BLOCKED | `null` | `precision>=0.90 and cross_tenant_merges==0` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G3.7 | SOFT | BLOCKED | `null` | `the three `without` counts all 0` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G3.8 | HARD | BLOCKED | `null` | `0, 0, true` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G3.9 | HARD | BLOCKED | `null` | `0, 0, >0, true` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G3.10 | HARD | BLOCKED | `null` | `cases>=30 and leaks==0` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G3.11 | REPORT | BLOCKED | `null` | `produced` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G3.12 | SOFT | BLOCKED | `null` | `>=-0.10` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G3.13 | SOFT | BLOCKED | `null` | `==3` (or 2 with G3.4 BLOCKED, noted)` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G3.14 | REPORT | BLOCKED | `null` | `produced` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G3.15 | REPORT | BLOCKED | `null` | `produced or BLOCKED `optional-skipped` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G3.16 | HARD | BLOCKED | `null` | `0, true` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G3.17 | SOFT | BLOCKED | `null` | `leaks==0 and metrics_within_noise` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G3.18 | SOFT | BLOCKED | `null` | `stack_ran` | None | unknown | BLOCKED: Docker/Qdrant not running |

### Phase 4
| Gate | Type | Status | Measured | Rule | Evidence | Hash | Notes |
|---|---|---|---|---|---|---|---|
| G4.1 | SOFT | ERROR | `null` | `==7` | docs/evidence/phase4/G4.1__20261002T114727Z.txt | 412a4066 | Command crashed or exited non-zero |
| G4.2 | SOFT | ERROR | `null` | `==0` | docs/evidence/phase4/G4.2__20261002T114728Z.txt | 60cf007f | Command crashed or exited non-zero |
| G4.3 | SOFT | ERROR | `null` | `true` | docs/evidence/phase4/G4.3__20261002T114728Z.txt | da14f4d7 | Command crashed or exited non-zero |
| G4.4 | SOFT | ERROR | `null` | `entries>=5 and each_cites_gate` | docs/evidence/phase4/G4.4__20261002T114729Z.txt | 12366e28 | Command crashed or exited non-zero |
| G4.5 | SOFT | BLOCKED | `null` | `both true` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G4.6 | SOFT | BLOCKED | `null` | `true` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G4.7 | SOFT | BLOCKED | `null` | `=="success"`; `BLOCKED` if `gh` is unavailable or unauthenticated` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G4.8 | SOFT | BLOCKED | `null` | `both exist and are non-empty` | None | unknown | BLOCKED: Docker/Qdrant not running |
| G4.9 | HARD | ERROR | `null` | `==0` | docs/evidence/phase4/G4.9__20261002T114729Z.txt | 6766c90f | Command crashed or exited non-zero |
| G4.10 | HARD | NOT-RUN | | `scan_ran` (use gitleaks if present, else a regex scan over `git log -p` for `sk-`, `AIza`, `api_key`, `secret`, `token`, private key headers); any `findings>0` goes to `ACTION-REQUIRED` | | | |
| G4.11 | HARD | NOT-RUN | | `manifest_ok and hash_mismatches==0` | | | |
| G4.12 | HARD | NOT-RUN | | `status_doc_built and not_run==0` | | | |

## Integrity Checks
Frozen hashes OK
Evidence manifest OK
No modified/deleted evidence
Gates Hash: af888fd0f90b1d6f3809bdd9c933a40e35e4ef0316fee8a157043612093aad1d
Results Count: 101 / 104

## Limitations
- LIM-G0.11: Gate G0.11 measured value did not meet threshold.
- LIM-G0.11: Gate G0.11 measured value did not meet threshold.
- LIM-G0.11: Gate G0.11 measured value did not meet threshold.
- LIM-G1.37: Gate G1.37 measured value did not meet threshold.
- LIM-G1.38: Gate G1.38 measured value did not meet threshold.
- LIM-G1.40: Gate G1.40 measured value did not meet threshold.
- LIM-G4.1: Gate G4.1 measured value did not meet threshold.
- LIM-G4.2: Gate G4.2 measured value did not meet threshold.
- LIM-G4.3: Gate G4.3 measured value did not meet threshold.
- LIM-G4.4: Gate G4.4 measured value did not meet threshold.


## Deviations
None

## ACTION-REQUIRED
None yet.

## Claim Trace
Trace logic to be implemented...

## Resume Lines
Resume lines placeholder.

## Reproduction
`python verify/run_gate.py <ID>` for each gate.
