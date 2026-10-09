# PGxTrust — Claude Code project state

**Read `README.md` completely first.** It holds the user's master project instructions
(sections 1–51: role, hypotheses H1–H7, architecture, benchmarks, phases, gates, rules). This file
only records the current state of the project and the extra rules adopted during P00. Where they
differ, the master instructions win, except for the frozen core question below, which the master
instructions themselves ask P00 to produce (§51.10, "freeze the primary research question").

Last updated: 2026-10-09 (end of P00).

## Where we are

- **P00 novelty audit: DONE.** See:
  - `docs/novelty_audit.md`
  - `docs/literature_matrix.md` (generated from `literature/literature_matrix.csv`)
  - `docs/data_sources.md`
  - `docs/research_protocol.md`
  - `docs/experiment_registry.md`
- **Core paper question: FROZEN** in `docs/research_protocol.md` §2 (protocol v0.2). It is the
  smallest defensible slice of the master programme and corresponds to master hypothesis **H4**
  (version-aware executable knowledge vs parametric/RAG knowledge), measured on real CPIC release
  history (master §13).
- **P01 status (2026-10-09):**
  - **G0 PASS:** no PGx work evaluates real version drift; abstention is now covered by PGxQA.
  - **G1 automatic criteria PASS:** 228 conservative items, 6 guidelines, 43 net post-2025 items,
    all thiopurines.
  - **G2 FAILS (strict model):** CI half-width 12.9 points with 16 clusters. Adding new-pair (N)
    items would give 80 clusters and 6.8 points. Waiting on the researcher's decision (protocol
    v0.5).
  - **Pending:** the researcher's 20-item manual check in `data/p01/g1_sanity_sample_fulltext.csv`.
  - Do not build RAG, LoRA, verifier, conflict engine or UI before the manual check and G2.
- **CPIC licence:** CC0 1.0. The ClinPGx data usage policy is still unread, so CPIC text stays out
  of git.

## What P00 found (do not contradict without new evidence)

- **Already covered in PGx, so never claim as new:**
  - RAG for PGx QA (≥6 papers including the target paper);
  - executable CPIC rules beating RAG generation, and failure localisation to the
    calling/input-interpretation step (Corpas et al. 2026, under revision at Cell Genomics);
  - PharmCAT as a deterministic CPIC + DPWG reporter.
- **Covered as general methods outside PGx:** abstention, claim-level verification, conflict-aware
  abstention, retriever/generator attribution, executable guideline skills (GuideSkill 2026), and
  temporal drift (synthetic, or without executable gold).
- **Candidate PGx gaps (not found in our searches as of 2026-10-09):**
  - (A) answer correctness across *real* CPIC version changes — **chosen**;
  - (B) CPIC–DPWG disagreement handling by LLM/RAG systems — **pivot**;
  - (C) counterfactual consistency — evaluation instrument only.
- Master H1/H2 are framed as replications of Corpas 2026 in our setting, not as contributions.
  The full neuro-symbolic system (master §4 primary question) remains the long-term programme.

## Target paper

Arafin, Moniruzzaman & Alkhateeb (2026), *Applied Sciences* 16(18):9148,
doi:10.3390/app16189148. Full extraction in `docs/novelty_audit.md` §1.

## Extra rules adopted in P00

1. Novelty statements must be backed by `literature/literature_matrix.csv`, validated by
   `scripts/validate_literature.py` and `tests/test_literature_matrix.py`. Phrase gaps as "not found
   in our searches (sources, date)".
2. Rows read only at abstract/snippet level must say `unknown`, never `no`. The validator enforces
   this.
3. `docs/literature_matrix.md` is generated. Edit the CSV, then run
   `scripts/render_literature_matrix.py`; a test fails if it is stale.
4. The CPIC API `recommendation.version` field is 1 for every row and is **not** a change history.
   Use per-release SQL dumps from files.cpicpgx.org.
5. Never commit third-party PDFs, SQL dumps, PharmCAT JARs, model weights or secrets. Record URL +
   SHA-256 in `data/README.md` / `docs/data_sources.md` instead.
6. Licences for CPIC and ClinPGx data are **not yet verified**. Verify them before redistributing
   anything derived.

## Session commands

```bash
cd ~/pgxtrust && git status && git pull
source .venv/bin/activate
pytest -q && ruff check .
python scripts/validate_literature.py
python scripts/render_literature_matrix.py --check
```
