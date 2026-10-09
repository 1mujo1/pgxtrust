# PGxTrust — Claude Code Project Instructions

## Mission

Run a research-grade study that extends the pharmacogenomics (PGx) decision-support work of
Arafin, Moniruzzaman & Alkhateeb (2026), *Applied Sciences* 16(18):9148,
doi:10.3390/app16189148.

The goal is **not** to build the biggest PGx assistant. The goal is to answer one narrow,
pre-registered question rigorously (see `docs/research_protocol.md` §2, "Frozen core question").

This is a research prototype. It is **not** a clinical decision-support system and must never be
described as one.

## Current phase

- **P00 — novelty audit and research protocol: DONE** (see `docs/p00_novelty_audit.md`).
- **Next: P01 — research gate G1 (CPIC release-diff feasibility).** Do not build models, RAG
  pipelines, or UIs until G1 passes. See `docs/research_protocol.md` §6.

## User profile

The same researcher as `~/cystoguard-xai` (see that repo's CLAUDE.md for the full profile):

- Debian Linux, i5-10210U, 16 GB RAM, no usable local GPU (MX130 on nouveau)
- Heavy compute: Google Colab GPU, or hosted LLM APIs
- Python beginner (~2/10), statistics beginner (~3/10)
- Wants to explain the work to Dr. Abedalrhman Alkhateeb (Lakehead University)

Write code that is simple, commented, and teachable. Explain new concepts briefly the first time
they appear.

## Non-negotiable scientific rules

1. **No novelty claims without evidence.** Never write "first", "novel", "state-of-the-art", or
   "no prior work" unless `literature/literature_matrix.csv` supports it. Phrase gaps as
   "not found in our search (databases, date)", never as "does not exist".
2. Absence of evidence in an abstract is not evidence of absence. Rows read only at abstract
   level must use `unknown`, not `no` (the validator enforces this).
3. Pin every knowledge source by version and access date (CPIC release tag, PharmCAT release,
   ClinPGx download date). Never use "latest" in an experiment.
4. Freeze the evaluation item set **before** running any model on it. Never edit items after
   seeing model outputs. Item set hash goes in the experiment registry.
5. Split by (gene, drug) pair and guideline, never by record, when anything is tuned. The
   Alkhateeb paper's record-level split leaks entities across splits (its §6.5). Do not repeat it.
6. Failed and negative results stay in `docs/experiment_registry.md`.
7. Report confidence intervals (cluster bootstrap over gene–drug pairs) where feasible.
8. No clinical claims. "Correct" means "matches the pinned guideline version", not "safe for
   patients".
9. LLM-as-judge is never the primary metric. Primary metrics must be computable deterministically
   against the pinned CPIC/DPWG source.
10. Prefer few, well-controlled experiments over many loose ones.

## Data and licensing safety

Never commit:
- API keys, `.env`, tokens
- downloaded CPIC SQL dumps, ClinPGx bulk files, PharmCAT JARs (re-downloadable; record URL + hash)
- third-party PDFs (record DOI + SHA-256 in docs instead)
- model checkpoints or raw LLM transcripts larger than a few MB (put them on Drive, record a hash)

Licences are **not yet verified in this project** (believed: ClinPGx/PharmGKB data CC BY-SA 4.0;
CPIC terms at cpicpgx.org). Verify and record them in the registry before redistributing any
derived file.

## Code style

- Python 3.12, `src/` layout, package `pgxtrust`
- Type hints, docstrings, pathlib
- pytest for anything that touches item construction, version diffing, scoring, or splits
- Machine-readable outputs (JSON/CSV) under `results/`, each with git SHA + source version
- Explicit random seeds

Run tests:

```bash
cd ~/pgxtrust
source .venv/bin/activate
pytest -q
```

## Interaction style

Move fast. Make routine repo decisions without asking. When a command fails: inspect, make the
smallest fix, rerun tests. Ask only when a decision changes the research question.
