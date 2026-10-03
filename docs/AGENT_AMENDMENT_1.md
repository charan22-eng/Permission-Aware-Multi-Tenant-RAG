# AMENDMENT 1 to `docs/AGENT_MASTER_PROMPT.md`

**Version:** 2.1 · 2026-10-02 · **Authority:** this amendment overrides the master prompt wherever they differ. The master prompt still governs everything this file does not mention.

**First action:** save this file verbatim as `docs/AGENT_AMENDMENT_1.md`, commit it, then follow section 5 (execution order). Do not wait for any human approval.

---

## 0. Why this amendment exists

Your first run produced a real engine and an honest refusal to fake results, which is good. A review of `docs/VERIFICATION_STATUS.md` found defects, listed below. Treat each as a bug in **your** work (or in the master prompt where noted) and fix it.

| # | Defect found | Why it matters |
|---|---|---|
| F1 | Tags `phase0-done`, `phase1-done`, `phase2-done`, `phase3-done` exist although **no** phase had its HARD gates passing, and `eval-v1` does not exist. | Violates R12. Tags are claims; these are false. |
| F2 | The status document contains hard-coded or placeholder text presented as results: "Frozen hashes OK" while `eval/FROZEN.md` does not exist; "Evidence manifest OK"; "Claim trace: to be implemented"; "Resume lines placeholder"; "ACTION-REQUIRED: None yet" while the secrets scan never ran; "Deviations: None". | Violates section 3.6 and section 10 (the builder computes everything; unknown means `NOT COMPUTED`). |
| F3 | `docs/LIMITATIONS.md` has auto-generated entries, including `LIM-G0.11` three times for a gate that **passed**, and entries for gates that crashed ("did not meet threshold" with no measurement). | Fabricated limitations. A limitation must cite a real measured SOFT failure. |
| F4 | 90 gates are `BLOCKED: Docker/Qdrant not running` or `Ollama not running`. Docker and Ollama were **stopped, not missing**; you never started them. Many of those gates need neither (static checks, unit tests, data checks), and G3.1 was blocked with the reason "Neo4j cannot run", which is unrelated. | `BLOCKED` is only valid for a capability that remains unavailable **after** a documented start attempt, and only if the gate actually needs it. |
| F5 | Eight gates are `ERROR` (G1.37, G1.38, G1.40, G4.1, G4.2, G4.3, G4.4, G4.9): the scripts crashed instead of reporting measurements (for example a missing file should report `sections_found: 0`, which is a `FAIL`, not a crash). | Gate scripts must report numbers and never crash on missing artifacts. |
| F6 | `verify/gates.yaml` rules are prose (`both true`, `0, 0, true`, `empty list`, `produced`). Prose cannot be evaluated. So the three `PASS` results (G0.11, G0.12, G0.13) were **not** verified by the evaluator. *(This one was a flaw in the master prompt's rule column, not your mistake.)* | The evaluator, not the gate script, must compute every verdict. |
| F7 | Verdict says `HALTED AT PHASE 0 (gate G0.1)` although G0.1 was `BLOCKED`, not a failed HARD gate. | `HALTED` means a HARD gate failed 3 times. Otherwise the correct verdict is `INCOMPLETE`. |
| F8 | Phase 1 to 4 application code appears not to exist, and its gates were blanket-blocked rather than recorded as not built. | A gate whose code you have not written is `FAIL` (or `NOT-RUN` before its turn). It is never `BLOCKED`. |

Record each of F1 to F8 in `docs/DEVIATIONS.md` (date, what, why, fix).

---

## 1. Integrity fixes (do these first, in this order)

**1.1 Tags.** Run `git tag -l` and `git ls-remote --tags origin`. Delete the four wrongly created tags locally and on the remote (`git tag -d <t>` and `git push origin --delete tag <t>`). Record the commit each pointed at in `docs/DEVIATIONS.md`. This is the only tag deletion permitted, and it is not a history rewrite. Then write `scripts/tag_phase.py <phase>`: it reads `docs/evidence/results/*.json` and creates the phase tag **only if every HARD gate of that phase is `PASS`** (for phase 0 it also requires `eval/FROZEN.md` and creates `eval-v1`). Remove every other place that calls `git tag`. Phase tags are named `phase<n>-done`; the freeze tag is `eval-v1`; the final tag is `project-v1` (requires all HARD gates of all phases `PASS`).

**1.2 Status builder.** Rewrite `scripts/build_status_doc.py` so that **nothing** in the output is a literal "OK", "None", or placeholder. Required behavior:
- Integrity section is computed by actually running `verify/check_frozen.py`, `verify/check_evidence.py`, comparing the `gates.yaml` hash to `docs/evidence/gates_yaml.sha256`, and counting results files against gates. If `eval/FROZEN.md` does not exist it prints `FROZEN: NOT YET CREATED`, never "OK".
- Claim trace, resume lines and ACTION-REQUIRED are computed. If a prerequisite gate is not `PASS` it prints `NOT COMPUTED (gate <id> is <status>)` or `NOT CLAIMABLE: gate <id> is <status>`. If G4.10 has not run, ACTION-REQUIRED must say `UNKNOWN: secrets scan not run`.
- Deviations section prints the contents of `docs/DEVIATIONS.md`.
- Verdict: `ALL HARD GATES PASS`; or `HALTED AT PHASE <n> (gate <id>)` only if a HARD gate has status `FAIL` after 3 recorded attempts; otherwise `INCOMPLETE: <counts of NOT-RUN, BLOCKED, ERROR, FAIL>`.
- The builder exits non-zero if the output contains any of: `to be implemented`, `placeholder`, `TODO`, `None yet`, or an unreplaced `{...}` template field.
- Add `tests/ci/test_status_builder.py` using fixture results (a PASS gate, a SOFT FAIL with a LIM entry, a BLOCKED gate, a missing FROZEN file, a HALT case) and assert the exact outputs above.

**1.3 Limitations.** Copy the current auto-generated `docs/LIMITATIONS.md` to `docs/evidence/archive/LIMITATIONS_autogen_20261002.md` (R11), then reset it. LIM entries are written **by you, manually, only** for SOFT gates whose status is `FAIL` and whose `measured` is non-null, and each entry quotes the measured value. The builder validates this and exits non-zero if a LIM cites a gate that is `PASS`, `ERROR`, `BLOCKED`, `NOT-RUN`, or a HARD gate.

**1.4 Canonical gates and evaluator.**
- Replace `verify/gates.yaml` with the canonical file in section 6 of this amendment, **verbatim**. Record the new hash in `docs/evidence/gates_yaml.sha256`. Log a `THRESHOLD-CHANGED` deviation with this reason: "prose rules in the first gates.yaml could not be evaluated; thresholds are unchanged from the master prompt; rules are now explicit Python expressions". Where a rule here differs in key names from the master prompt tables, **this file wins**.
- `rule` is a Python expression over a dict named `measured`. Evaluate it with `eval(rule, {"__builtins__": {}}, {"measured": measured, "len": len, "all": all, "any": any, "min": min, "max": max, "abs": abs})`. A rule that raises (for example a missing key) makes the gate `FAIL` with note `RULE-ERROR: <key>`, not a crash.
- The evidence file for every gate must start with a header that prints: the rule, the measured values, the evaluated boolean, and the resulting status. Gate scripts **never** print or decide a verdict.
- Gate script contract (replaces the master prompt's): print exactly one line `RESULT_JSON: {"measured": {...}, "blocked": null, "notes": "..."}`. For a `REPORT` gate, include `"produced": true` in `measured` when the numbers were produced.
- `blocked` may be non-null only as `{"capability": "<name>", "attempted_fix": "<what you ran>", "evidence": "<path to the output>"}`. The evaluator accepts `BLOCKED` only if `capability` is in that gate's `needs` list in `gates.yaml`, `attempted_fix` is non-empty, and the evidence file exists and is non-empty. Otherwise the status is `FAIL` with note `INVALID-BLOCK`. Gates with `needs: []` can **never** be blocked.
- Valid capability names: `docker`, `qdrant`, `ollama`, `neo4j`, `small_model`, `reranker_model`, `network`, `gh_cli`.
- Gate scripts never crash on missing artifacts. Catch the error, report zeros or `false` in `measured`, and let the evaluator produce `FAIL`. Fix the eight `ERROR` gates (F5) this way. A crash that remains is status `ERROR`, which counts as `FAIL` and is a defect you must fix.
- Re-run G0.11, G0.12, G0.13 under the new evaluator and confirm the headers show the evaluated expressions.

---

## 2. Start the services (preflight must do this, and it was missing)

The master prompt said to attempt "the obvious automatic fix". For services the obvious fix is to start them. Extend `scripts/preflight.py` and record **every command and its full output** in `docs/evidence/preflight_attempts.txt`.

**2.1 Docker.** If `docker info` fails: launch Docker Desktop (`Start-Process "$env:ProgramFiles\Docker\Docker\Docker Desktop.exe"`; also try `$env:LOCALAPPDATA\Programs\Docker\Docker\Docker Desktop.exe`), then run a **bounded readiness loop inside the script** (up to 240 seconds, every 5 seconds) until `docker info` succeeds. Then find the existing Qdrant container with `docker ps -a` and `docker start <id>`. **Never** recreate containers, run `docker compose down -v`, `docker volume rm`, or `docker system prune`: the Phase 0 `chunks` collection lives in that container's volume. If no Qdrant container exists, create one from the compose file and record that `chunks` must be rebuilt by master prompt section 5.1 step 3. Verify with a request to Qdrant's collections endpoint and print the point count of `chunks`.

**2.2 Ollama.** If `http://127.0.0.1:11434/api/tags` fails: start `ollama serve` as a hidden detached process (`Start-Process -WindowStyle Hidden`), bounded readiness loop up to 90 seconds, then `ollama list`. For any missing required model (`llama3.1`, `qwen2.5:7b`) run `ollama pull` once. Create the Modelfile tags from `eval/judges/` (and `llama-gen` later).

**2.3** Only if a start attempt fails after the bounded loop may a gate that `needs` that capability be `BLOCKED`, and the `blocked` object must carry the exact error text. If Docker Desktop cannot be launched by you (for example it needs an interactive login or elevation), put exactly that in `ACTION-REQUIRED`. That is the only situation where a human is needed.

Bounded readiness loops **inside a blocking script** are allowed. Rule R1 still forbids agent-side timers, background jobs you wait on, and polling by you.

---

## 3. Corrections to the master prompt

- **R12 reinforced:** tags only through `scripts/tag_phase.py`.
- **BLOCKED** is defined in section 1.4 of this amendment, and **only** that definition counts. A gate whose code you have not yet written is `FAIL` (if its turn has come) or `NOT-RUN` (if not), never `BLOCKED`.
- **Verdict wording** is defined in section 1.2.
- **CI-safe tests may use `QdrantClient(":memory:")`** for logic that does not need payload indexes. Tests that check payload indexes, and every gate whose `needs` includes `qdrant`, run against the Docker Qdrant with `test_`-prefixed collections.
- **Capability list:** `needs` in the canonical `gates.yaml` is authoritative for what each gate may be blocked on.

---

## 4. What "done" means for this amendment

Before continuing the master loop, produce a short report in the chat with: (a) `git tag -l` before and after; (b) the evaluator headers for G0.11, G0.12, G0.13; (c) the list of the eight previously `ERROR` gates and their new status; (d) `docker info` and `ollama list` output and the Qdrant `chunks` point count. Then **continue directly** with section 5. Do not wait for a reply.

---

## 5. Execution order

1. Sections 1.1 to 1.4 (integrity fixes).
2. Section 2 (start services; extend preflight; rerun it).
3. Restart the master loop (master prompt section 11) from Phase 0 with services running. Implement each phase's application code and tests as the master prompt specifies. Run each gate through `verify/run_gate.py`.
4. `scripts/tag_phase.py` after each phase; never tag by hand.
5. FINAL: `scripts/make_results_table.py`, `scripts/check_claims.py`, `scripts/build_status_doc.py`, commit, push, and reply per master prompt section 12 (verdict line, counts, failed or unrun HARD gates, every BLOCKED gate with its reason, ACTION-REQUIRED items, path to the status document).

---

## 6. Canonical `verify/gates.yaml` (save verbatim)

```yaml
gates:
  - {id: G0.1, phase: 0, type: HARD, title: "API health fingerprint", needs: [qdrant], command: "python verify/gates/g0_01.py", evidence_dir: "docs/evidence/phase0", rule: "measured['project_ok'] is True and measured['corpus_version_matches_env'] is True"}
  - {id: G0.2, phase: 0, type: HARD, title: "Single listener on API port", needs: [qdrant], command: "python verify/gates/g0_02.py", evidence_dir: "docs/evidence/phase0", rule: "measured['listeners']==1 and measured['pid_is_ours'] is True"}
  - {id: G0.3, phase: 0, type: SOFT, title: "Two identical sequential baseline runs", needs: [qdrant, ollama], command: "python verify/gates/g0_03.py", evidence_dir: "docs/evidence/phase0", rule: "measured['rows']==70 and measured['diff_rows']==0 and measured['errors']==0"}
  - {id: G0.4, phase: 0, type: SOFT, title: "Retrieval metrics Hit@5 Recall@10 MRR@10", needs: [qdrant], command: "python verify/gates/g0_04.py", evidence_dir: "docs/evidence/phase0", rule: "measured['hit5']>=0.93 and measured['recall10']>=0.97"}
  - {id: G0.5, phase: 0, type: SOFT, title: "Combined correctness under frozen scorer", needs: [qdrant, ollama], command: "python verify/gates/g0_05.py", evidence_dir: "docs/evidence/phase0", rule: "measured['combined']>=0.90"}
  - {id: G0.6, phase: 0, type: SOFT, title: "Held-out judge gate", needs: [ollama], command: "python verify/gates/g0_06.py", evidence_dir: "docs/evidence/phase0", rule: "measured['number_swap_negation_catch']>=9 and measured['reword_false_fail']<=1"}
  - {id: G0.7, phase: 0, type: SOFT, title: "Sanity set rerun with committed rows", needs: [ollama], command: "python verify/gates/g0_07.py", evidence_dir: "docs/evidence/phase0", rule: "measured['rows_nonempty'] is True and measured['number_swap_catch']>=9 and measured['reword_false_fail']<=2 and measured['numeric_false_fail_rate_valid']<0.05"}
  - {id: G0.8, phase: 0, type: SOFT, title: "GPU residency during judge pass", needs: [ollama], command: "python verify/gates/g0_08.py", evidence_dir: "docs/evidence/phase0", rule: "measured['judge_processor']=='100% GPU' and measured['judge_context']==2048"}
  - {id: G0.9, phase: 0, type: SOFT, title: "Abstention on unanswerable set", needs: [qdrant, ollama], command: "python verify/gates/g0_09.py", evidence_dir: "docs/evidence/phase0", rule: "measured['abstain']>=9 and measured['false_abstain']<=2"}
  - {id: G0.10, phase: 0, type: HARD, title: "Frozen hashes match and eval-v1 tag exists", needs: [], command: "python verify/gates/g0_10.py", evidence_dir: "docs/evidence/phase0", rule: "measured['hashes_match'] is True and measured['tag_exists'] is True"}
  - {id: G0.11, phase: 0, type: SOFT, title: "README known-limitations items present", needs: [], command: "python verify/gates/g0_11.py", evidence_dir: "docs/evidence/phase0", rule: "measured['items_found']==5"}
  - {id: G0.12, phase: 0, type: HARD, title: "Evidence integrity", needs: [], command: "python verify/gates/g0_12.py", evidence_dir: "docs/evidence/phase0", rule: "measured['zero_byte']==0 and measured['modified_or_deleted']==0"}
  - {id: G0.13, phase: 0, type: HARD, title: "Frozen files unchanged since e0d55b5", needs: [], command: "python verify/gates/g0_13.py", evidence_dir: "docs/evidence/phase0", rule: "len(measured['changed_files'])==0"}
  - {id: G0.14, phase: 0, type: SOFT, title: "Rerun reproduces reference combined correctness", needs: [qdrant, ollama], command: "python verify/gates/g0_14.py", evidence_dir: "docs/evidence/phase0", rule: "measured['combined_diff_questions']<=2"}
  - {id: G1.1, phase: 1, type: HARD, title: "Deterministic chunk IDs", needs: [qdrant], command: "python verify/gates/g1_01.py", evidence_dir: "docs/evidence/phase1", rule: "measured['ids_equal'] is True"}
  - {id: G1.2, phase: 1, type: SOFT, title: "Question ID migration complete", needs: [], command: "python verify/gates/g1_02.py", evidence_dir: "docs/evidence/phase1", rule: "measured['unmapped']==0"}
  - {id: G1.3, phase: 1, type: HARD, title: "Payload completeness", needs: [qdrant], command: "python verify/gates/g1_03.py", evidence_dir: "docs/evidence/phase1", rule: "measured['points']>0 and measured['missing_fields']==0"}
  - {id: G1.4, phase: 1, type: HARD, title: "Ingestion refuses chunk without tenant_id", needs: [qdrant], command: "python verify/gates/g1_04.py", evidence_dir: "docs/evidence/phase1", rule: "measured['refused'] is True and measured['stored']==0"}
  - {id: G1.5, phase: 1, type: HARD, title: "Old collection untouched", needs: [qdrant], command: "python verify/gates/g1_05.py", evidence_dir: "docs/evidence/phase1", rule: "measured['count_before']==measured['count_after']"}
  - {id: G1.6, phase: 1, type: SOFT, title: "Apex employee regression on chunks_v2", needs: [qdrant, ollama], command: "python verify/gates/g1_06.py", evidence_dir: "docs/evidence/phase1", rule: "measured['misses_subset_of_q0_q2'] is True and measured['hit5']>=0.93 and measured['combined']>=0.90"}
  - {id: G1.7, phase: 1, type: HARD, title: "JWT rejection matrix", needs: [], command: "python verify/gates/g1_07.py", evidence_dir: "docs/evidence/phase1", rule: "measured['cases']>0 and measured['rejected_401']==measured['cases'] and measured['generic_body'] is True"}
  - {id: G1.8, phase: 1, type: HARD, title: "Body and query identity ignored; mutation M4", needs: [qdrant], command: "python verify/gates/g1_08.py", evidence_dir: "docs/evidence/phase1", rule: "measured['server_used_token_tenant'] is True and measured['m4_fails_test'] is True"}
  - {id: G1.9, phase: 1, type: SOFT, title: "Token script mints every persona", needs: [], command: "python verify/gates/g1_09.py", evidence_dir: "docs/evidence/phase1", rule: "measured['personas_defined']>0 and measured['personas_minted']==measured['personas_defined']"}
  - {id: G1.10, phase: 1, type: HARD, title: "Layer 1 cases; mutation M1", needs: [qdrant], command: "python verify/gates/g1_10.py", evidence_dir: "docs/evidence/phase1", rule: "measured['cases_pass'] is True and measured['m1_fails_layer1_tests'] is True"}
  - {id: G1.11, phase: 1, type: HARD, title: "Layer 2 catches broken Layer 1", needs: [qdrant], command: "python verify/gates/g1_11.py", evidence_dir: "docs/evidence/phase1", rule: "measured['leaks']==0 and measured['alerts']>0"}
  - {id: G1.12, phase: 1, type: HARD, title: "Stale payload revoke blocked; mutation M6", needs: [qdrant], command: "python verify/gates/g1_12.py", evidence_dir: "docs/evidence/phase1", rule: "measured['blocked'] is True and measured['m6_fails_test'] is True"}
  - {id: G1.13, phase: 1, type: HARD, title: "Missing or mismatched ACL row fails closed", needs: [qdrant], command: "python verify/gates/g1_13.py", evidence_dir: "docs/evidence/phase1", rule: "measured['dropped_and_alerted'] is True"}
  - {id: G1.14, phase: 1, type: HARD, title: "Single Qdrant entry point (AST scan)", needs: [], command: "python verify/gates/g1_14.py", evidence_dir: "docs/evidence/phase1", rule: "measured['violations']==0"}
  - {id: G1.15, phase: 1, type: HARD, title: "No admin bypass; mutation M5", needs: [qdrant], command: "python verify/gates/g1_15.py", evidence_dir: "docs/evidence/phase1", rule: "measured['admin_blocked'] is True and measured['named_user_allowed'] is True and measured['m5_fails_test'] is True"}
  - {id: G1.16, phase: 1, type: HARD, title: "Citations and eval fields gated; mutation M7", needs: [qdrant], command: "python verify/gates/g1_16.py", evidence_dir: "docs/evidence/phase1", rule: "measured['citation_violations']==0 and measured['eval_field_leaks']==0 and measured['k_cap_ok'] is True and measured['m7_fails_test'] is True"}
  - {id: G1.17, phase: 1, type: HARD, title: "Audit append-only; mutation M8", needs: [], command: "python verify/gates/g1_17.py", evidence_dir: "docs/evidence/phase1", rule: "measured['update_blocked'] is True and measured['delete_blocked'] is True and measured['m8_fails_test'] is True"}
  - {id: G1.18, phase: 1, type: HARD, title: "Audit completeness and traces", needs: [qdrant], command: "python verify/gates/g1_18.py", evidence_dir: "docs/evidence/phase1", rule: "measured['requests']>0 and measured['null_fields']==0 and measured['traces_found_rate']==1.0"}
  - {id: G1.19, phase: 1, type: HARD, title: "Audit endpoint scoping", needs: [qdrant], command: "python verify/gates/g1_19.py", evidence_dir: "docs/evidence/phase1", rule: "measured['own_tenant_ok'] is True and measured['other_tenant_response_identical_to_nonexistent'] is True and measured['non_admin_denied'] is True"}
  - {id: G1.20, phase: 1, type: SOFT, title: "Three tenants built to spec", needs: [], command: "python verify/gates/g1_20.py", evidence_dir: "docs/evidence/phase1", rule: "measured['tenants']==3 and measured['apex_ok'] is True and measured['northwind_ok'] is True and measured['helix_ok'] is True"}
  - {id: G1.21, phase: 1, type: SOFT, title: "Cross-tenant topic and name overlap", needs: [], command: "python verify/gates/g1_21.py", evidence_dir: "docs/evidence/phase1", rule: "measured['shared_topics']>=5 and measured['shared_names']>=2"}
  - {id: G1.22, phase: 1, type: HARD, title: "Canaries unique and confined to confidential docs", needs: [], command: "python verify/gates/g1_22.py", evidence_dir: "docs/evidence/phase1", rule: "measured['confidential_docs']>0 and measured['with_canary']==measured['confidential_docs'] and measured['duplicates']==0 and measured['canary_in_nonconfidential']==0"}
  - {id: G1.23, phase: 1, type: SOFT, title: "Injection documents present", needs: [], command: "python verify/gates/g1_23.py", evidence_dir: "docs/evidence/phase1", rule: "measured['apex_has'] is True and measured['helix_has'] is True"}
  - {id: G1.24, phase: 1, type: SOFT, title: "Attack matrix size", needs: [], command: "python verify/gates/g1_24.py", evidence_dir: "docs/evidence/phase1", rule: "measured['cases']>=150"}
  - {id: G1.25, phase: 1, type: HARD, title: "Cross-tenant and escalation leaks", needs: [qdrant], command: "python verify/gates/g1_25.py", evidence_dir: "docs/evidence/phase1", rule: "measured['cases']>0 and measured['leaks_in_retrieval']==0 and measured['leaks_in_prompt']==0 and measured['leaks_in_response']==0"}
  - {id: G1.26, phase: 1, type: HARD, title: "Token tampering rejected", needs: [], command: "python verify/gates/g1_26.py", evidence_dir: "docs/evidence/phase1", rule: "measured['cases']>0 and measured['rejected']==measured['cases']"}
  - {id: G1.27, phase: 1, type: HARD, title: "Request-body injection leaks", needs: [qdrant], command: "python verify/gates/g1_27.py", evidence_dir: "docs/evidence/phase1", rule: "measured['cases']>0 and measured['leaks']==0"}
  - {id: G1.28, phase: 1, type: HARD, title: "Revoke then re-query", needs: [qdrant], command: "python verify/gates/g1_28.py", evidence_dir: "docs/evidence/phase1", rule: "measured['cases']>0 and measured['retrieved_after_revoke']==0"}
  - {id: G1.29, phase: 1, type: HARD, title: "Indirect injection: foreign canary leaks", needs: [qdrant, ollama], command: "python verify/gates/g1_29.py", evidence_dir: "docs/evidence/phase1", rule: "measured['cases']>0 and measured['foreign_canary_leaks']==0"}
  - {id: G1.30, phase: 1, type: HARD, title: "Mutation harness M1-M8 and CI workflow valid", needs: [qdrant], command: "python verify/gates/g1_30.py", evidence_dir: "docs/evidence/phase1", rule: "measured['mutants']>=8 and measured['behaved_as_expected']==measured['mutants'] and measured['workflow_valid'] is True"}
  - {id: G1.31, phase: 1, type: SOFT, title: "New-tenant answerable questions by construction", needs: [], command: "python verify/gates/g1_31.py", evidence_dir: "docs/evidence/phase1", rule: "measured['per_tenant_min']>=20 and measured['gt_found_rate']==1.0"}
  - {id: G1.32, phase: 1, type: SOFT, title: "abstain_forbidden set by construction", needs: [], command: "python verify/gates/g1_32.py", evidence_dir: "docs/evidence/phase1", rule: "measured['count']>=20 and measured['acl_violations']==0"}
  - {id: G1.33, phase: 1, type: HARD, title: "Full extended eval leak count", needs: [qdrant, ollama], command: "python verify/gates/g1_33.py", evidence_dir: "docs/evidence/phase1", rule: "measured['questions']>0 and measured['leaks']==0"}
  - {id: G1.34, phase: 1, type: REPORT, title: "Correct-refusal rate with CI", needs: [qdrant, ollama], command: "python verify/gates/g1_34.py", evidence_dir: "docs/evidence/phase1", rule: "measured.get('produced') is True"}
  - {id: G1.35, phase: 1, type: REPORT, title: "Filtering overhead p50 and p95", needs: [qdrant], command: "python verify/gates/g1_35.py", evidence_dir: "docs/evidence/phase1", rule: "measured['n']>=200"}
  - {id: G1.36, phase: 1, type: SOFT, title: "Extended eval identical across two runs", needs: [qdrant, ollama], command: "python verify/gates/g1_36.py", evidence_dir: "docs/evidence/phase1", rule: "measured['diff_rows']==0"}
  - {id: G1.37, phase: 1, type: SOFT, title: "Threat model structure", needs: [], command: "python verify/gates/g1_37.py", evidence_dir: "docs/evidence/phase1", rule: "measured['sections_required']>0 and measured['sections_found']>=measured['sections_required']"}
  - {id: G1.38, phase: 1, type: SOFT, title: "Phase 1 self-review present", needs: [], command: "python verify/gates/g1_38.py", evidence_dir: "docs/evidence/phase1", rule: "measured['least_confident_section'] is True and measured['residual_risks']>=3"}
  - {id: G1.39, phase: 1, type: HARD, title: "Side channels: forbidden vs nonexistent", needs: [qdrant], command: "python verify/gates/g1_39.py", evidence_dir: "docs/evidence/phase1", rule: "measured['pairs']>0 and measured['status_identical'] is True and measured['body_identical'] is True"}
  - {id: G1.40, phase: 1, type: SOFT, title: "README Phase 1 table traced to results", needs: [], command: "python verify/gates/g1_40.py", evidence_dir: "docs/evidence/phase1", rule: "measured['numbers_checked']>0 and measured['unmatched_numbers']==0"}
  - {id: G2.1, phase: 2, type: HARD, title: "Cache lookup key fields", needs: [], command: "python verify/gates/g2_01.py", evidence_dir: "docs/evidence/phase2", rule: "measured['key_fields_ok'] is True"}
  - {id: G2.2, phase: 2, type: HARD, title: "Cross-tenant cache reuse; mutation M10", needs: [], command: "python verify/gates/g2_02.py", evidence_dir: "docs/evidence/phase2", rule: "measured['cross_tenant_hits']==0 and measured['m10_fails_test'] is True"}
  - {id: G2.3, phase: 2, type: HARD, title: "Cross-role cache reuse; mutation M9", needs: [], command: "python verify/gates/g2_03.py", evidence_dir: "docs/evidence/phase2", rule: "measured['cross_role_hits']==0 and measured['m9_fails_test'] is True"}
  - {id: G2.4, phase: 2, type: HARD, title: "Revoke invalidates cache; mutation M11", needs: [], command: "python verify/gates/g2_04.py", evidence_dir: "docs/evidence/phase2", rule: "measured['served_after_revoke']==0 and measured['evicted'] is True and measured['m11_fails_test'] is True"}
  - {id: G2.5, phase: 2, type: HARD, title: "acl_version bump not served", needs: [], command: "python verify/gates/g2_05.py", evidence_dir: "docs/evidence/phase2", rule: "measured['cases']>0 and measured['served_stale']==0"}
  - {id: G2.6, phase: 2, type: HARD, title: "corpus_version bump not served", needs: [], command: "python verify/gates/g2_06.py", evidence_dir: "docs/evidence/phase2", rule: "measured['cases']>0 and measured['served_stale']==0"}
  - {id: G2.7, phase: 2, type: HARD, title: "Never-cache rules", needs: [], command: "python verify/gates/g2_07.py", evidence_dir: "docs/evidence/phase2", rule: "measured['cases']>=6 and measured['stored_violations']==0"}
  - {id: G2.8, phase: 2, type: HARD, title: "TTL expiry", needs: [], command: "python verify/gates/g2_08.py", evidence_dir: "docs/evidence/phase2", rule: "measured['cases']>0 and measured['served_expired']==0"}
  - {id: G2.9, phase: 2, type: SOFT, title: "Threshold sweep", needs: [], command: "python verify/gates/g2_09.py", evidence_dir: "docs/evidence/phase2", rule: "measured['false_hits_at_chosen']==0 and measured['sweep_complete'] is True"}
  - {id: G2.10, phase: 2, type: SOFT, title: "Generated pair sets", needs: [], command: "python verify/gates/g2_10.py", evidence_dir: "docs/evidence/phase2", rule: "measured['paraphrase']>=50 and measured['near_miss']>=50 and measured['cross_tenant']>=10 and measured['cross_role']>=10 and measured['hash_recorded_before_sweep'] is True"}
  - {id: G2.11, phase: 2, type: SOFT, title: "Router accuracy on test split", needs: [], command: "python verify/gates/g2_11.py", evidence_dir: "docs/evidence/phase2", rule: "measured['accuracy_test']>=0.80 and measured['dev_test_separated'] is True"}
  - {id: G2.12, phase: 2, type: REPORT, title: "Escalation rate and quality", needs: [qdrant, ollama, small_model], command: "python verify/gates/g2_12.py", evidence_dir: "docs/evidence/phase2", rule: "measured.get('produced') is True"}
  - {id: G2.13, phase: 2, type: SOFT, title: "Benchmark design", needs: [qdrant, ollama, small_model], command: "python verify/gates/g2_13.py", evidence_dir: "docs/evidence/phase2", rule: "measured['repeat_fraction']>=0.5 and measured['sequential'] is True and measured['same_questions'] is True"}
  - {id: G2.14, phase: 2, type: SOFT, title: "Simulated cost reduction", needs: [qdrant, ollama, small_model], command: "python verify/gates/g2_14.py", evidence_dir: "docs/evidence/phase2", rule: "measured['cost_reduction_pct_simulated']>=20 and measured['labeled_simulated'] is True"}
  - {id: G2.15, phase: 2, type: SOFT, title: "Latency p95 not worse", needs: [qdrant, ollama, small_model], command: "python verify/gates/g2_15.py", evidence_dir: "docs/evidence/phase2", rule: "measured['p95_change_pct']<=0"}
  - {id: G2.16, phase: 2, type: SOFT, title: "Quality non-inferiority vs always-large", needs: [qdrant, ollama, small_model], command: "python verify/gates/g2_16.py", evidence_dir: "docs/evidence/phase2", rule: "measured['quality_delta_ci_low']>=-0.10"}
  - {id: G2.17, phase: 2, type: HARD, title: "Leak re-run with cache cases and mutants", needs: [qdrant], command: "python verify/gates/g2_17.py", evidence_dir: "docs/evidence/phase2", rule: "measured['leaks']==0 and measured['mutants_ok'] is True"}
  - {id: G2.18, phase: 2, type: SOFT, title: "Dashboard panels and PNG", needs: [], command: "python verify/gates/g2_18.py", evidence_dir: "docs/evidence/phase2", rule: "measured['panels_with_data']==6 and measured['png_exists'] is True"}
  - {id: G2.19, phase: 2, type: SOFT, title: "Benchmark identical across two runs", needs: [qdrant, ollama, small_model], command: "python verify/gates/g2_19.py", evidence_dir: "docs/evidence/phase2", rule: "measured['diff_rows']==0"}
  - {id: G2.20, phase: 2, type: SOFT, title: "Phase 1 regression", needs: [qdrant, ollama], command: "python verify/gates/g2_20.py", evidence_dir: "docs/evidence/phase2", rule: "measured['phase1_leaks']==0 and measured['hit5_within_ci'] is True"}
  - {id: G3.1, phase: 3, type: SOFT, title: "Dataset sample and source", needs: [], command: "python verify/gates/g3_01.py", evidence_dir: "docs/evidence/phase3", rule: "measured['source'] in ('hotpotqa','FALLBACK-SYNTHETIC') and measured['n']>=30 and measured['license_noted'] is True"}
  - {id: G3.2, phase: 3, type: SOFT, title: "Benchmark tenant ACL", needs: [qdrant], command: "python verify/gates/g3_02.py", evidence_dir: "docs/evidence/phase3", rule: "measured['all_chunks_tenant_ok'] is True and measured['acl_public'] is True"}
  - {id: G3.3, phase: 3, type: REPORT, title: "Vector baseline EM F1 SF recall", needs: [qdrant, ollama], command: "python verify/gates/g3_03.py", evidence_dir: "docs/evidence/phase3", rule: "measured.get('produced') is True"}
  - {id: G3.4, phase: 3, type: REPORT, title: "Rerank baseline", needs: [qdrant, ollama, reranker_model], command: "python verify/gates/g3_04.py", evidence_dir: "docs/evidence/phase3", rule: "measured.get('produced') is True"}
  - {id: G3.5, phase: 3, type: SOFT, title: "Extraction validity", needs: [ollama], command: "python verify/gates/g3_05.py", evidence_dir: "docs/evidence/phase3", rule: "measured['valid_rate']>=0.95 and measured['cached_jsonl'] is True"}
  - {id: G3.6, phase: 3, type: SOFT, title: "Entity resolution on planted sets", needs: [], command: "python verify/gates/g3_06.py", evidence_dir: "docs/evidence/phase3", rule: "measured['precision']>=0.90 and measured['cross_tenant_merges']==0"}
  - {id: G3.7, phase: 3, type: SOFT, title: "Graph load integrity", needs: [], command: "python verify/gates/g3_07.py", evidence_dir: "docs/evidence/phase3", rule: "measured['nodes']>0 and measured['nodes_without_tenant']==0 and measured['edges_without_tenant']==0 and measured['edges_without_evidence']==0"}
  - {id: G3.8, phase: 3, type: HARD, title: "Graph tenant isolation; mutation M12", needs: [], command: "python verify/gates/g3_08.py", evidence_dir: "docs/evidence/phase3", rule: "measured['cross_tenant_nodes']==0 and measured['cross_tenant_chunks']==0 and measured['m12_fails_test'] is True"}
  - {id: G3.9, phase: 3, type: HARD, title: "ACL on graph path; mutation M13", needs: [], command: "python verify/gates/g3_09.py", evidence_dir: "docs/evidence/phase3", rule: "measured['unauthorized_chunks_in_prompt']==0 and measured['unauthorized_triples_in_prompt']==0 and measured['layer2_alerts_when_cypher_unscoped']>0 and measured['m13_fails_test'] is True"}
  - {id: G3.10, phase: 3, type: HARD, title: "Graph-pivot leakage suite", needs: [], command: "python verify/gates/g3_10.py", evidence_dir: "docs/evidence/phase3", rule: "measured['cases']>=30 and measured['leaks']==0"}
  - {id: G3.11, phase: 3, type: REPORT, title: "Multi-hop results for baselines and graph", needs: [qdrant, ollama], command: "python verify/gates/g3_11.py", evidence_dir: "docs/evidence/phase3", rule: "measured.get('produced') is True"}
  - {id: G3.12, phase: 3, type: SOFT, title: "Single-hop non-regression", needs: [qdrant, ollama], command: "python verify/gates/g3_12.py", evidence_dir: "docs/evidence/phase3", rule: "measured['single_hop_delta_ci_low']>=-0.10"}
  - {id: G3.13, phase: 3, type: SOFT, title: "Ablation table", needs: [], command: "python verify/gates/g3_13.py", evidence_dir: "docs/evidence/phase3", rule: "measured['variants_reported']==3 or (measured['variants_reported']==2 and measured.get('rerank_blocked') is True)"}
  - {id: G3.14, phase: 3, type: REPORT, title: "Indexing cost", needs: [ollama], command: "python verify/gates/g3_14.py", evidence_dir: "docs/evidence/phase3", rule: "measured.get('produced') is True"}
  - {id: G3.15, phase: 3, type: REPORT, title: "Question decomposition comparison", needs: [ollama], command: "python verify/gates/g3_15.py", evidence_dir: "docs/evidence/phase3", rule: "measured.get('produced') is True"}
  - {id: G3.16, phase: 3, type: HARD, title: "Cache interplay via graph path", needs: [], command: "python verify/gates/g3_16.py", evidence_dir: "docs/evidence/phase3", rule: "measured['served_after_revoke_via_graph']==0 and measured['sources_complete'] is True"}
  - {id: G3.17, phase: 3, type: SOFT, title: "Phase 1 and 2 regression", needs: [qdrant, ollama], command: "python verify/gates/g3_17.py", evidence_dir: "docs/evidence/phase3", rule: "measured['leaks']==0 and measured['metrics_within_noise'] is True"}
  - {id: G3.18, phase: 3, type: SOFT, title: "Resource fit", needs: [], command: "python verify/gates/g3_18.py", evidence_dir: "docs/evidence/phase3", rule: "measured['stack_ran'] is True"}
  - {id: G4.1, phase: 4, type: SOFT, title: "README architecture stages", needs: [], command: "python verify/gates/g4_01.py", evidence_dir: "docs/evidence/phase4", rule: "measured['stages_found']==7"}
  - {id: G4.2, phase: 4, type: SOFT, title: "Results table traced to results", needs: [], command: "python verify/gates/g4_02.py", evidence_dir: "docs/evidence/phase4", rule: "measured['numbers_checked']>0 and measured['unmatched_numbers']==0"}
  - {id: G4.3, phase: 4, type: SOFT, title: "Threat model linked in README", needs: [], command: "python verify/gates/g4_03.py", evidence_dir: "docs/evidence/phase4", rule: "measured['linked'] is True"}
  - {id: G4.4, phase: 4, type: SOFT, title: "Limitations entries cite gates", needs: [], command: "python verify/gates/g4_04.py", evidence_dir: "docs/evidence/phase4", rule: "measured['entries']>=5 and measured['each_cites_gate'] is True"}
  - {id: G4.5, phase: 4, type: SOFT, title: "Compose config valid and services healthy", needs: [docker], command: "python verify/gates/g4_05.py", evidence_dir: "docs/evidence/phase4", rule: "measured['compose_valid'] is True and measured['services_healthy'] is True"}
  - {id: G4.6, phase: 4, type: SOFT, title: "Fresh-clone smoke test", needs: [network], command: "python verify/gates/g4_06.py", evidence_dir: "docs/evidence/phase4", rule: "measured['smoke_pass'] is True"}
  - {id: G4.7, phase: 4, type: SOFT, title: "CI on main succeeded", needs: [gh_cli], command: "python verify/gates/g4_07.py", evidence_dir: "docs/evidence/phase4", rule: "measured['conclusion']=='success'"}
  - {id: G4.8, phase: 4, type: SOFT, title: "Demo assets exist", needs: [], command: "python verify/gates/g4_08.py", evidence_dir: "docs/evidence/phase4", rule: "measured['dashboard_png'] is True and measured['blocked_query_image'] is True"}
  - {id: G4.9, phase: 4, type: HARD, title: "Claims trace to results", needs: [], command: "python verify/gates/g4_09.py", evidence_dir: "docs/evidence/phase4", rule: "measured['numbers_checked']>0 and measured['unmatched_numbers']==0"}
  - {id: G4.10, phase: 4, type: HARD, title: "Secrets scan of full history ran", needs: [], command: "python verify/gates/g4_10.py", evidence_dir: "docs/evidence/phase4", rule: "measured['scan_ran'] is True"}
  - {id: G4.11, phase: 4, type: HARD, title: "Evidence manifest complete", needs: [], command: "python verify/gates/g4_11.py", evidence_dir: "docs/evidence/phase4", rule: "measured['manifest_ok'] is True and measured['hash_mismatches']==0"}
  - {id: G4.12, phase: 4, type: HARD, title: "Status document built, nothing unrun", needs: [], command: "python verify/gates/g4_12.py", evidence_dir: "docs/evidence/phase4", rule: "measured['status_doc_built'] is True and measured['not_run']==0"}
```
