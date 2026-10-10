# Experiment registry

Every run, gate check and literature pass is recorded here: successes, failures and abandoned
attempts alike. Never delete an entry. Correct an entry by adding a new dated line under it.

Required fields: **ID · date · git SHA · protocol version · inputs (with versions/hashes) ·
outputs · result · status · notes**.

Status values: `planned` · `running` · `done` · `failed` · `abandoned` · `superseded`.

P00 artefacts (E01–E05) are at git commit `4463d9d` (pushed 2026-10-09, branch `main`).

---

## Summary

| ID | Phase | What | Status | Result |
|---|---|---|---|---|
| P00-E01 | P00 | Identify and extract the target paper | done | Arafin, Moniruzzaman & Alkhateeb 2026, Appl Sci 16:9148 |
| P00-E02 | P00 | Official resource survey (CPIC, PharmCAT, ClinPGx) | done | CPIC: 88 releases, dumps per release; API `version` not a history; PharmCAT v3.4.0 reports CPIC/DPWG side by side |
| P00-E03 | P00 | Literature search + matrix (25 rows; 27 after E05) | done | Matrix valid; 13/13 tests pass at that point |
| P00-E04 | P00 | Defensibility assessment + freeze core question | done | Core question = CPIC guideline-version drift (protocol v0.1); pivot = CPIC–DPWG conflicts |
| P00-E05 | P00 | Realignment with the master instructions (README.md) | done | Protocol v0.2 (maps to master H4); +2 searches, +2 matrix rows (27); data_sources.md; 15 tests pass |
| P01-G0 | P01 | Literature completion (full texts of `unknown` PGx rows) | **pass (candidate A)** | 7/8 full texts + preprint search; temporal and conflict still gaps; abstention now covered (PGxQA) |
| P01-G1 | P01 | CPIC release-diff feasibility | **automatic criteria pass; manual check pending** | 228 conservative items, 6 guidelines, 43 net post-2025 items — but all post-2025 items are thiopurines |
| P02-E01 | P02 | Build, validate and freeze the temporal question set + prompt v001 | **done (frozen)** | 3,116 questions, 80 clusters, 0 reference-lookup failures; sha256 6189860… |
| P03-E00 | P03 | Retrieval corpora, run harness, zero-cost dry run | **done** | Oracle 100% on all 4 arms × 3,116; random 24.6%; resume verified; recall measured, not tuned |
| P02-G2 | P02 | Power check on real item count | **pass after expansion (v0.5)** | Strict model failed on 228 items/16 clusters (12.9 pts); researcher adopted "appeared" items → 857 items/80 clusters, 6.8 pts, P = 0.99 |

---

## P00-E01 — Target paper identification and extraction

- **Date:** 2026-10-09
- **Protocol:** pre-protocol
- **Inputs:** Crossref + Semantic Scholar metadata for doi:10.3390/app16189148; full-text PDF from the
  MDPI CDN (`mdpi-res.com/.../applsci-16-09148.pdf`), SHA-256
  `7c237d3e22dc3afb5d2540c8bf616c94d57688923aeb1294f708c7113565da01`. The PDF is not committed.
- **Outputs:** `docs/novelty_audit.md` §1 (architecture, data, baselines, metrics, results,
  limitations, future work).
- **Result:** identification is unambiguous (the only 2026 PGx paper with Alkhateeb as an author in
  the sources searched).
- **Notes:** the MDPI HTML returns 403 to scripted clients; the CDN PDF works. A related Lakehead
  thesis is embargoed until 2027.

## P00-E02 — Official resource survey

- **Date:** 2026-10-09
- **Inputs:**
  - CPIC API `/v1/recommendation` (2115 rows) and `/v1/guideline` (29 rows);
  - GitHub `cpicpgx/cpic-data` releases (88; v0.6 2020-05-17 → v1.60.1 2026-08-12);
  - HTTP range checks on the v1.30.0 and v1.54.0 dumps (206 OK);
  - GitHub `PharmGKB/PharmCAT` releases (latest v3.4.0, 2026-07-14) and
    `docs/methods/Matching-Recommendations.md`.
- **Result:**
  - `recommendation.version` = 1 for all 2115 rows, so the API is not a change history and release
    dumps must be diffed;
  - the schema has a `change_log` table;
  - recent releases since v1.44 have no GitHub assets but link dumps on files.cpicpgx.org;
  - PharmCAT tags CPIC/DPWG annotations by source and does not reconcile them;
  - the ClinPGx bulk download returned HTTP 303 to curl (unresolved).
- **Status:** done.

## P00-E03 — Literature search and matrix

- **Date:** 2026-10-09
- **Inputs:** searches listed in `docs/novelty_audit.md` §7.
- **Outputs:**
  - `literature/literature_matrix.csv` (25 rows × 8 capability axes);
  - `src/pgxtrust/literature.py` (validator);
  - `scripts/validate_literature.py`;
  - `results/p00/literature_coverage.json`;
  - `tests/test_literature_matrix.py`.
- **Result:** the matrix is valid. PGx computational candidate gaps: multi_guideline_conflict,
  evidence_verification, temporal_updates, counterfactual_eval, uncertainty_abstention. All except
  counterfactual_eval already have the method in general medical NLP.
- **Tests:** `pytest -q` → 13 passed.
- **Caveat:** 6–8 PGx rows per axis are `unknown` (abstract-only). These are resolved in G0.

## P00-E04 — Defensibility assessment and core-question freeze

- **Date:** 2026-10-09
- **Outputs:** `docs/novelty_audit.md` §5; `docs/research_protocol.md` v0.1.
- **Result:**
  - **Covered (do not claim):**
    - RAG for PGx QA;
    - executable CPIC rules vs RAG (Corpas 2026);
    - failure attribution (Corpas 2026, RAGChecker, RAG-X);
    - abstention, claim verification and conflict-aware abstention as methods;
    - an all-in-one "trustworthy PGx assistant".
  - **Defensible, subject to gates:**
    - A. PGx guideline-version drift on real CPIC releases (**chosen**);
    - B. CPIC–DPWG disagreement handling (**pivot**);
    - C. counterfactual date/genotype tests (**instrument only**).
- **Status:** done.

## P00-E05 — Realignment with the master instructions

- **Date:** 2026-10-09
- **What happened:**
  - The user's prompt said "Read CLAUDE.md completely before doing anything else". No PGxTrust
    CLAUDE.md existed locally, so P00-E01..E04 were drafted under the prompt alone, using
    `~/cystoguard-xai/CLAUDE.md` as a style reference.
  - At push time, a private GitHub repo `1mujo1/pgxtrust` already existed (created 2026-10-09 00:13
    UTC). Its `README.md` contains the master project instructions (§1–51), which call themselves
    "this CLAUDE.md".
- **Actions:**
  - Read the master instructions in full.
  - Ran the two master-checklist searches that were missing: CPIC CDS implementations and
    neuro-symbolic medical RAG.
  - Added rows `overby2017ahrq` and `cao2026guideskill`.
  - Added `title` and `relation_to_pgxtrust` columns, as master §26 requires.
  - Generated `docs/literature_matrix.md`.
  - Renamed the audit to `docs/novelty_audit.md`.
  - Added `docs/data_sources.md` and the master repository skeleton.
  - Protocol v0.2 maps the frozen question to master H4 and adds optional arm A4 (LoRA on an older
    release).
- **Unchanged:** the frozen core question and the G1 thresholds. No data had been seen.
- **Repo handling:** the user's `README.md` is kept unchanged. The local `CLAUDE.md` points to it and
  records the project state. Copying the master text into `CLAUDE.md` was blocked by the auto-mode
  safety classifier (writing downloaded text into an instructions file), and not pursued further.
- **Tests:** `pytest -q` → 15 passed; `ruff check .` → all checks passed.

## P01-G0 — Literature completion

- **Date:** 2026-10-09
- **Inputs:**
  - Full texts of zack2026npj, zack2025pgxj, keat2025pgxqa, rector2025sherpa, murugan2024 and
    borishetty2025pgxrag.
  - The Corpas bioRxiv preprint.
  - Europe PMC title/abstract search over preprints and papers, 2024–2026 (queries in
    `docs/novelty_audit.md` §7).
  - Not obtained: jeon2026hrag (paywalled; stays `unknown`).
- **Method:** keyword-targeted reading of each full text (versions, updates, outdated, DPWG,
  conflict, abstention, refusal). Matrix rows were updated, and axes not searched remain
  `unknown`.
- **Result:** **PASS** for candidate A.
  - No PGx work evaluates answers across real guideline versions. Zack 2026 describes an updater
    mode but does not evaluate it; Corpas recommends regression-testing against guideline updates
    but does not run it.
  - Candidate B (conflicts) is also still open.
  - **Correction:** PGxQA measures refusal on misspecified questions, so PGx abstention is
    covered.
- **Licence:** CPIC content is CC0 1.0 (cpic-data `LICENSE.md`). The ClinPGx data usage policy
  that also binds the DB/API is unread (JavaScript-only page), so CPIC text stays out of git for
  now.
- **Tests:** 35 passed, including the new `test_no_full_text_pgx_work_evaluates_temporal_drift`.

## P01-G1 — CPIC release-diff feasibility

- **Date:** 2026-10-09
- **Protocol:** v0.4 (v0.3 clarifications made before any diff; the v0.4 re-keying filter is
  **post hoc** and conservative).
- **Code:** `src/pgxtrust/cpic_releases.py`, `scripts/p01_cpic_release_diff.py`; 34 tests pass.
- **Inputs:** 88 cpic-data release tags.
  - 84 dumps downloaded from files.cpicpgx.org.
  - 4 returned HTTP 404: v0.6, v0.7, v1.17.1, and v1.60.1 (an application-only release).
  - Tags, URLs and SHA-256 hashes are in `results/p01/cpic_dump_manifest.tsv`. Dumps are
    git-ignored.
  - Window: v0.8 (2020-07) → v1.60.0 (2026-08-08). All 84 parsed with no errors and no duplicate
    keys.
- **Outputs:**
  - `results/p01/g1_summary.json`;
  - `results/p01/cpic_changes.csv` (keys, types, action classes; no CPIC text);
  - full-text tables under `data/p01/` (git-ignored, because the CPIC licence is unverified).
- **Results:**

  | Metric | Value |
  |---|---|
  | Raw changes (consecutive releases) | M 197 · A 893 · R 822 · N 629 |
  | Substantive, as originally defined (§5.2) | 1770 |
  | Re-keyings found (R/A pairs with identical text, same release + pair) | 771 pairs; 597 in v1.21.0 and 110 in v1.25.0 |
  | **Substantive, re-keyings removed** | **228** (M 55, A 122, R 51) |
  | Guidelines with items | **6**: clopidogrel, phenytoin, G6PD, RYR1/CACNA1S, statins, thiopurines |
  | **Net post-2025 items** (v1.43.0 → v1.60.0) | **43, all in TPMT/NUDT15–thiopurines** (3 drugs) |
  | Version-pinned lookup reproduces sampled items | 20/20 |

- **Gate:** all three frozen automatic criteria pass, even on the conservative pool. The
  **manual check is pending**: the researcher fills `manual_action_changed` for the 20 rows in
  `data/p01/g1_sanity_sample_fulltext.csv`. A pass needs ≥16/20.
- **Caveats (must carry into P02):**
  1. **Post-cut-off drift sits in one guideline.** All 43 net post-2025 changes are thiopurines
     (3 gene–drug clusters). Any "changed after the model's training cut-off" stratum is therefore
     a single-guideline case study and must not be presented as a general result.
  2. **v1.54.0 → v1.55.0 was a transitional round trip.** Indeterminate-NUDT15 rows were blanked to
     "n/a" and restored five weeks later. Step-wise counts double-count it, which is why the net
     diff is used for "recent".
  3. **The re-keying filter can hide real drift.** The CYP2D6 activity-score threshold redefinitions
     (e.g. "≥4.5" → "≥3.75", 2023) keep the same text but change *which patients* receive it. That
     is genotype-to-phenotype drift, which this item definition does not capture. It is a candidate
     second item type for P02, not counted here.
- **Status:** automatic criteria pass; manual check pending; G0 not started.

## P02-E01 — Frozen temporal question set

- **Date:** 2026-10-09
- **Protocol:** v0.6.
- **Code:** `src/pgxtrust/items.py`, `src/pgxtrust/prompts.py`, `scripts/p02_build_items.py`.
  67 tests pass.
- **Inputs:** 84 CPIC release dumps (`results/p01/cpic_dump_manifest.tsv`); the primary pool of
  857 items.
- **Outputs:**
  - `data/p02/items_v1.jsonl`, git-ignored because it contains CPIC text. SHA-256
    `618986063db57ad7807f38c3011801edc6bca4b27bc4812bef90eae449e44af8`.
  - `results/p02/items_manifest.json` and `results/p02/items_meta.csv` (no option text).
  - Prompt `configs/prompts/forced_choice_v001.txt`, SHA-256
    `0880a65b54a5a8c8ef8c5ab31cfc894a264d9320138ebbe8b9f984951b59ef98`.
- **Result:**

  | Quantity | Value |
  |---|---|
  | Targets kept | 779 of 857: 214 changed, 565 appeared. 78 dropped because both versions were "no recommendation" |
  | Questions | 3,116 = 779 × {target, control} × {before, after} |
  | Gold kind | targets 766 no-rec / 792 rec; controls 766 / 792 (identical) |
  | Options | exactly 4 for all 3,116 questions |
  | Control match | 86 same pair, 36 same guideline, 657 same release only |
  | Reference lookup (arm R) | reproduces 3,116/3,116 gold answers |

- **Fixed before freezing (first build, no model run):**
  - no-recommendation imbalance (49% of targets vs 0% of controls);
  - 2–5 options per question;
  - normalised, unreadable gene/population text in prompts;
  - bare activity-score numbers.
- **Carried caveat:** most controls come from other guidelines. Protocol v0.6 pre-registers a
  same-pair/same-guideline sensitivity analysis and the control-free date-flip analysis.
- **Model decision (researcher, 2026-10-09):** "Llama-8B + 1 hosted model".
  - **Open:** `meta-llama/Llama-3.1-8B-Instruct` on Colab GPU, the same model as the target paper.
  - **Hosted:** `claude-sonnet-5-5` via the Anthropic API (Claude's default choice; the researcher
    may swap it).
  - **Decoding:** temperature 0; max 5 output tokens; one call per question; 3 attempts on API
    errors, never scored.
  - **Still needed before running:**
    - an Anthropic API key in `.env` (never committed);
    - a Hugging Face token with the Llama 3.1 licence accepted (gated model);
    - the retrieval corpora for arms A1–A3;
    - the training cut-off date of each model, recorded from its official documentation.

## P03-E00 — Run harness and dry run (no model, no cost)

- **Date:** 2026-10-09
- **Protocol:** v0.7.
- **Code:**
  - `src/pgxtrust/retrieval.py` (corpora + BM25), `backends.py` (oracle, random, Claude,
    Llama), `runner.py` (append-only, resumable);
  - `scripts/p03_build_corpora.py`, `scripts/p03_run.py` (refuses to run if the items or template
    hash differs);
  - 76 tests pass.
- **Corpora:** current 2,115, mixed 3,426, tagged 3,426 documents. Hashes are in
  `results/p03/corpora_manifest.json`.
- **Dry run** (`results/p03/dryrun_summary.json`; the raw dry-run rows are git-ignored):
  - oracle 3,116/3,116 correct on each of A0–A3;
  - random 24.6% (A2);
  - rerunning a finished arm skipped all 3,116;
  - 0 errors, 0 unparseable.
- **Retrieval recall** of the gold document in the top 5 (questions whose gold answer is a
  recommendation; targets / controls):

  | Arm | Targets | Controls |
  |---|---|---|
  | A1 | 500/792 | 428/792 |
  | A2 | 605/792 | 592/792 |
  | A3 | 631/792 | 608/792 |

  Reported, **not tuned**: tuning on the evaluation items would leak.
- **Bugs caught by tests before any model run:**
  - the tokenizer glued full stops to words, so drug names never matched;
  - duplicate questions were answered twice within one run;
  - the metadata check would have blocked resuming after a new commit.
- **Model plan revised (2026-10-10):** the researcher asked for a free option. The workload is about
  8.1M input tokens and 12,464 calls per model. Free hosted tiers would take weeks (reported caps,
  unverified), and FreeLLMAPI switches models under rate limits (invalid for research).
  - **Recommended:** both target-paper models on free Colab: `meta-llama/Llama-3.1-8B-Instruct` @
    `0e9e39f2…` (gated) and `Qwen/Qwen3-8B` @ `b968826d…` (the paper's own revision; Apache-2.0,
    ungated).
  - `claude-sonnet-5-5` becomes optional; a paid hosted model can be added later as a bonus.
  - Awaiting the researcher's confirmation.
- **Ready for real runs:** see `docs/running_p03.md`. This needs the researcher's Anthropic API key
  and Hugging Face token. On a free Colab T4, Llama needs `--quant 4bit` (a declared deviation).

## P02-G2 — Power / precision check

- **Date:** 2026-10-09
- **Code:** `src/pgxtrust/power.py`, `scripts/p01_g2_power.py` (41 tests pass). Output in
  `results/p01/g2_power.json`.
- **Set-up:**
  - Assumed truth: 80% accuracy on unchanged items vs 65% on changed items (a 15-point penalty).
  - 1:1 matched unchanged items.
  - Cluster bootstrap (1,000 resamples) × 200 simulated studies, seed 20261009.
  - Items: the 228 conservative G1 items in 16 gene–drug clusters (43, 38, 34, 30, 16, 16, 14,
    seven of 5, two of 1).
- **Pre-specified decision** (pair clusters, cluster_sd = 1.0): half-width **0.079 → pass**.
- **Flaw found after running:**
  - The half-width barely moved with the number of clusters (16 → 3) or with cluster_sd.
  - Cause: the simulated cluster effect shifted changed and unchanged items equally, so it
    cancelled out of the difference. That implicitly assumed the same penalty for every drug.
  - **Post hoc fix:** a `penalty_sd` term lets the penalty vary by cluster. A regression test
    (`test_penalty_heterogeneity_widens_intervals`) covers it.
- **Strict result (post hoc, used for the decision):**

  | Scenario | Half-width | P(lower CI > 0) |
  |---|---|---|
  | pair clusters (16), penalty_sd = 1.0 | **0.129 ❌** | 0.60 |
  | pair clusters, penalty_sd = 0.5 | 0.096 | 0.82 |
  | guideline clusters (6), penalty_sd = 1.0 | 0.146 | 0.53 |
  | thiopurines only (3), penalty_sd = 1.0 | 0.168 | 0.40 |

- **Decision:** **G2 FAILS** under the strict model. The protocol §6 rule applies: expand the item
  pool before any model run.
- **Expansion options evaluated (exploratory, not yet adopted):**
  - **Option 1, new gene–drug pairs (N items):** before the guideline existed the correct as-of
    answer is "CPIC has no recommendation". This gives 629 items in 68 pairs (64 new) across 9
    guidelines. Core + N = 80 pair clusters: half-width **0.068**, P = 0.99 (penalty_sd = 1.0).
    Clustered by guideline (12): 0.120.
  - **Option 2, re-keyed rows** (threshold/phenotype redefinitions, 35 pairs): needs
    genotype-to-phenotype logic, and many are pure formatting changes. Not pursued now.
- **Decision (2026-10-09):** the researcher chose **Option 1**, which became protocol v0.5.
  - The pool is 857 items: 228 "changed" + 629 "appeared". It spans 80 gene–drug clusters across
    12 guidelines.
  - Rerun on the v0.5 pool: pair clusters half-width **0.068** (P = 0.99) at penalty_sd = 1.0, and
    0.051 at penalty_sd = 0.5. Guideline clusters: 0.120 at penalty_sd = 1.0 and 0.076 at 0.5.
- **G2 status:** **PASS on the v0.5 pool**, using the protocol's pair-level clustering.
- **Carried caveats:**
  - The "changed"-only estimate stays underpowered and is exploratory.
  - Guideline-level clustering is a sensitivity analysis.
  - Post-2025 drift is thiopurines only.
