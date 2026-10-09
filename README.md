# PGxTrust

Research project extending Arafin, Moniruzzaman & Alkhateeb (2026),
*Evidence-Grounded Clinical Pharmacogenomics Decision Support*, Applied Sciences 16:9148
([doi:10.3390/app16189148](https://doi.org/10.3390/app16189148)).

**Research prototype only. Not a clinical decision-support tool.**

## Core question (frozen, protocol v0.1)

> When a CPIC recommendation has changed between guideline releases, do LLM-based PGx
> question-answering systems give the recommendation that was valid on the date asked, and does
> attaching release-version metadata to retrieved evidence reduce version errors?

Ground truth comes from CPIC's own tagged database releases (88 releases, 2020–2026), so the primary
outcome needs no LLM judge and no clinician labelling.

## Status

| Phase | Status |
|---|---|
| P00 novelty audit + protocol | done ([audit](docs/p00_novelty_audit.md), [protocol](docs/research_protocol.md)) |
| P01 G0 literature completion + G1 CPIC release-diff feasibility | **next** |

## Layout

```
docs/        research protocol, novelty audit, experiment registry
literature/  literature_matrix.csv (validated evidence base for every novelty statement)
src/pgxtrust/ library code
scripts/     command-line entry points
tests/       pytest
results/     small machine-readable outputs (JSON/CSV) per phase
data/        downloaded sources (git-ignored; provenance in data/README.md)
```

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/pytest -q
.venv/bin/python scripts/validate_literature.py
```
