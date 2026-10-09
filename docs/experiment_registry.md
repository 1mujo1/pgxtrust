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
| P01-G0 | P01 | Literature completion (full texts of `unknown` PGx rows) | planned | — |
| P01-G1 | P01 | CPIC release-diff feasibility | planned | thresholds frozen in protocol §6 |
| P02-G2 | P02 | Power check on real item count | planned | — |

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

## P01-G0 — Literature completion (planned)

See protocol §6 G0.

## P01-G1 — CPIC release-diff feasibility (planned)

See protocol §6 G1. Thresholds are frozen before data are seen: ≥40 substantive items, ≥4
guidelines, ≥15 dated ≥2025-01-01, and a sanity check on 20 items.

## P02-G2 — Power check (planned)

See protocol §6 G2.
