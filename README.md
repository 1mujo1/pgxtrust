# PGxTrust

**Do LLM pharmacogenomics assistants give the recommendation that was valid *on the date asked*?**

Pharmacogenomic (PGx) guidelines from CPIC change between releases. A model trained on, or retrieving
from, the wrong release can give advice that was correct once but is stale now, or is too new for a
question about the past. PGxTrust measures this version drift on CPIC's real release history and
tests whether labelling retrieved evidence with its release version and date reduces version errors.

> Research prototype only. **Not** a clinical diagnostic or prescribing tool, and not medical advice.

## Research question

> When a CPIC recommendation has changed between guideline releases, do LLM-based PGx question
> answering systems give the recommendation that was valid on the date asked, and does attaching
> release-version metadata to retrieved evidence reduce version errors?

The correct answer is always the recommendation in the CPIC release valid on the stated date,
recovered from that release's SQL dump. No LLM judge and no clinician labelling are needed for the
primary outcome. Full protocol: [`docs/research_protocol.md`](docs/research_protocol.md).

The project extends Arafin, Moniruzzaman & Alkhateeb (2026),
*Evidence-Grounded Clinical Pharmacogenomics Decision Support*, Applied Sciences 16(18):9148,
[doi:10.3390/app16189148](https://doi.org/10.3390/app16189148).

## Benchmark

- **3,116 dated multiple-choice questions** built from consecutive CPIC release dumps, frozen in P02
  (SHA-256 recorded in `results/p02/items_manifest.json`).
- **857 primary items** across **80 gene–drug clusters**: recommendations that *changed* between
  releases, or *appeared* in a newer release, each paired with unchanged controls.
- Each model answers under four conditions:

| Arm | What the model sees | What it tests |
|---|---|---|
| A0 | the question only | what the model remembers |
| A1 | + 5 passages from the **current** CPIC release | does up-to-date retrieval help or hurt "as of an old date" questions? |
| A2 | + 5 passages from **all** releases, unlabelled | a realistic stale or mixed index |
| A3 | + the same passages **labelled with CPIC version and date** | does version metadata fix version errors? |

## Status

| Phase | What | Status |
|---|---|---|
| P00 | Novelty audit and literature matrix | done |
| P01 | CPIC release diff (gate G1) and power check (G2) | passed |
| P02 | Question set and prompt v001 | frozen |
| P03 | Retrieval corpora, run harness, zero-cost dry run | done: oracle 100% on all arms, random baseline 24.6% |
| P03 | Model runs (Claude, Llama-3.1-8B, Qwen) | pending |

Every run and gate is logged in [`docs/experiment_registry.md`](docs/experiment_registry.md).

## Reproduce

Requires Python 3.12+.

```bash
git clone https://github.com/1mujo1/pgxtrust && cd pgxtrust
python3 -m venv .venv && .venv/bin/pip install -e . pytest
.venv/bin/python -m pytest                         # unit tests

.venv/bin/python scripts/p01_cpic_release_diff.py  # download CPIC release dumps, diff releases
.venv/bin/python scripts/p01_g2_power.py           # power check
.venv/bin/python scripts/p02_build_items.py        # build the question set
.venv/bin/python scripts/p03_build_corpora.py      # build retrieval corpora for A1–A3
.venv/bin/python scripts/p03_run.py --arm A0 --backend oracle   # zero-cost pipeline check
```

CPIC text is downloaded into `data/` and is git-ignored; only derived metadata and hashes are
committed under `results/`. Running real models (Claude via API, Llama and Qwen on Colab) is
described step by step in [`docs/running_p03.md`](docs/running_p03.md). API keys go in `.env`
(copy `.env.example`; never committed).

## Repository layout

```
src/pgxtrust/   library: CPIC release handling, items, prompts, retrieval, model backends, runner
scripts/        one script per pipeline step (p01_…, p02_…, p03_…)
configs/        versioned prompts
results/        committed outputs: manifests, summaries, metadata (no CPIC text)
docs/           protocol, novelty audit, literature matrix, data sources, registry, run guide
literature/     literature matrix source (CSV)
tests/          unit tests
data/           downloads, git-ignored
```

`docs/project_instructions.md` holds the full long-term research programme (hypotheses H1–H7,
architecture, phases and gates) that this core study is the first slice of.

## Citation and licence

Cite via [`CITATION.cff`](CITATION.cff). Code is MIT-licensed. CPIC guideline content belongs to
CPIC and is not redistributed here.
