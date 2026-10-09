# Data sources

Status of every knowledge source PGxTrust may use. Nothing listed here has been downloaded into
the repository yet. Downloads and hashes go in `data/README.md` when P01 ingests them.

Last checked: 2026-10-09.

| Source | What it provides | Machine-readable access | Versioning | Licence / terms | Role in core paper | Status |
|---|---|---|---|---|---|---|
| **CPIC database** | Alleles, function, genotype→phenotype, recommendations (`drugrecommendation`, `classification`, `lookupkey`) for 29 guidelines / 2115 recommendations | REST API `api.cpicpgx.org/v1/*` (PostgREST); whole-DB SQL dumps `files.cpicpgx.org/data/database/cpic_db_dump-v<X>.sql.gz` | 88 GitHub release tags `cpicpgx/cpic-data` (v0.6 2020-05-17 → v1.60.1 2026-08-12); API serves latest only; `recommendation.version` = 1 for all rows (not a history); DB has `change_log` table | **CC0 1.0** for all curated CPIC content (cpic-data `LICENSE.md`, read 2026-10-09). Attribution requested: cite clinpgx.org as primary source, URL, access date and version. DB/API additionally "bound by" the ClinPGx data usage policy (clinpgx.org/page/dataUsagePolicy, JavaScript-only, **not yet read**). Recommendation text is kept out of git until that policy is read | **Primary ground truth** (per-release dumps) | API queried; dumps v1.30.0 & v1.54.0 reachable (HTTP 206) |
| **PharmCAT** | Deterministic VCF → diplotype → phenotype → CPIC/DPWG/FDA recommendation report (JSON/HTML/TSV) | GitHub releases `PharmGKB/PharmCAT` (JAR + Docker) | Release tags; latest **v3.4.0 (2026-07-14)**; guideline data embedded per release | Code: MPL-2.0 (GitHub API); embedded guideline data follows source terms | Deterministic comparator (master B4); not needed for the core temporal question | Docs read |
| **ClinPGx** (formerly PharmGKB) | Curated guideline annotations (CPIC, DPWG, others), drug-label annotations, clinical annotations | Website downloads / API (`api.clinpgx.org`) | Download dates; no release tags seen | Believed CC BY-SA 4.0 (PharmGKB data licence); **to be verified** | Only machine-readable DPWG route → needed for the conflict pivot (G1b) | Bulk download returned HTTP 303 to curl; route unresolved |
| **DPWG** (KNMP) | Dutch guideline recommendations | PDFs only (per PharmCAT docs); structured form only via ClinPGx | Publication dates | KNMP terms; **to be verified** | Pivot only | Not accessed |
| **FDA Table of Pharmacogenetic Associations / labels** | Regulatory PGx associations | FDA web table; labels via ClinPGx | Page update dates | US government work; **to be verified** | Out of scope for core paper | Not accessed |
| **Target paper** (Arafin et al. 2026) | Methods and results for comparison | MDPI CDN PDF | Published version 2026-09-15 | CC BY 4.0 | Comparison and reproduction reference | Read; SHA-256 `7c237d3e…65da01`; not committed |
| **Corpas et al. benchmark** | 110 CPIC Level A cases, five-cell results | GitHub `manuelcorpas/24-AGENTIC-PGX-BENCHMARK` (MIT per GitHub API); Zenodo 10.5281/zenodo.21710055 (CC BY 4.0 per record) | Repo tags; Zenodo versions | MIT / CC BY 4.0 | Possible external sanity set; closest prior work | README + results read |
| **PGxQA** (Keat et al. 2025) | Public PGx QA benchmark | To locate in P01 | — | To verify | Possible external sanity set | Abstract only |

## Rules

- Ground truth for the core paper comes **only** from CPIC release dumps, never from the live API
  (which serves "latest") and never from an LLM.
- Every downloaded file gets: source, version/tag, URL, download date, SHA-256 and licence. These go
  in `data/README.md` and are copied into the experiment registry entry that uses the file.
- Do not scrape a website when an official export or API exists (master §10).
