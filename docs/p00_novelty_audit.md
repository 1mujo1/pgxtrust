# P00 — Novelty audit

- **Date:** 2026-10-09
- **Status:** complete
- **Searches:** web search (standard + extended), PubMed E-utilities, arXiv API, Crossref, Semantic
  Scholar, GitHub API (repos, releases), PharmCAT docs, CPIC API. Queries and coverage are listed
  in §7.
- **Evidence base:** `literature/literature_matrix.csv` (25 rows, validated by
  `scripts/validate_literature.py`; coverage snapshot in `results/p00/literature_coverage.json`).

> **Reading rule.** "Not found" below always means "not found in the searches listed in §7 as of
> 2026-10-09". It never means "does not exist". 6–8 PGx rows per axis were read only at abstract
> level and are marked `unknown`. They could still cover an axis (see §6, gate G0).

---

## 1. The paper we are extending

**Arafin P, Moniruzzaman M, Alkhateeb A.** *Evidence-Grounded Clinical Pharmacogenomics Decision
Support: Integrating Fine-Tuned Large Language Models with Hybrid Retrieval-Augmented Generation.*
Applied Sciences 2026, 16(18), 9148. doi:[10.3390/app16189148](https://doi.org/10.3390/app16189148).
Received 12 Jun 2026, accepted 10 Sep 2026, published 15 Sep 2026. CC BY 4.0. Lakehead University
(Arafin, Alkhateeb) and Thompson Rivers University (Moniruzzaman). NSERC RGPIN-2026-07654.

Identification: the only 2026 PGx paper with Alkhateeb as an author that we found in Crossref,
Semantic Scholar, PubMed and web search. A related Lakehead thesis with the same design is embargoed
until 2027 (knowledgecommons.lakeheadu.ca/handle/2453/5615).
Full text read from the MDPI CDN PDF (28 pp., SHA-256
`7c237d3e22dc3afb5d2540c8bf616c94d57688923aeb1294f708c7113565da01`; not committed).

### 1.1 Architecture

| Component | What they did |
|---|---|
| Base LLMs | Meta-Llama-3.1-8B-Instruct; Qwen3-8B (base checkpoint, rev `b968826d…`) |
| Adaptation | LoRA on q/k/v/o projections, r=16, α=32, dropout 0.05, batch 1 × grad-accum 8, 1000 steps, warm-up 50, LR 1e-5 (Qwen); loss on answer tokens only |
| Knowledge source 1 | CPIC PostgreSQL DB → CSV → joined (PySpark/DuckDB) → JSONL instruction records. Used for **both fine-tuning and retrieval** |
| Knowledge source 2 | ClinPGx guideline pages scraped (browser-console JS + Playwright) → cleaned → 500-char chunks, 100 overlap. Used for retrieval only |
| Retrieval | "Hybrid": entity-based lexical filter over JSONL files, then all-MiniLM-L6-v2 cosine rerank, top-K. ClinPGx text: dense similarity only |
| Generation | Structured prompt (question + evidence); instructed to flag insufficient evidence |
| Compute | SHARCNET Nibi, H100 |

### 1.2 Data and evaluation

| Item | Detail |
|---|---|
| Classification set | 1000 held-out JSONL records; labels from **rule-based normalisation** of reference text into 3 classes: decreased response (66), increased response (395), no significant association (539) |
| Split | JSONL-record level. Evaluation item + exact duplicates excluded from retrieval. **Records sharing genes/drugs/phenotypes remain across splits** (their §6.5) |
| Text metrics | Cosine similarity, BERTScore F1, LLM-as-judge (Mistral-7B-Instruct-v0.2, 1–10 score) |
| Human review | 20 prompts, research team, 4 criteria × 5 points; not blinded, no inter-rater agreement |
| Baselines | Base model, LoRA-only, RAG+LoRA, for each of 2 LLMs. **No external system baseline** (they say so in §7) and no RAG-only arm |

### 1.3 Main results (as reported)

| Model | Config | Acc | Macro-F1 | Judge |
|---|---|---|---|---|
| Llama-3.1-8B | base | 0.435 | 0.33 | 43.3% |
| Llama-3.1-8B | LoRA | 0.556 | 0.21 | 56.5% |
| Llama-3.1-8B | RAG + LoRA | 0.91 | 0.87 | 88% |
| Qwen3-8B | base | 0.38 | 0.32 | 10.2% |
| Qwen3-8B | LoRA | 0.43 | 0.34 | 89.8% |
| Qwen3-8B | RAG + LoRA | 0.35 | 0.28 | 94.7% |

Manual: Llama 333/400, Qwen 330.5/400.

### 1.4 Stated limitations (their §6.5–6.6, §7)

- Simulated, controlled setting; no validation by practising clinicians.
- Small, static human evaluation; no expert panel; no inter-rater agreement.
- Performance bottlenecked by retrieved-evidence quality (tangential or noisy chunks).
- External validity limited to CPIC/ClinPGx; record-level held-out evaluation, not unseen entities.
- LLM-as-judge evaluator bias; class imbalance; prompt sensitivity.
- No direct benchmarking against published systems.

### 1.5 Stated future work (their §3.9, §6.7)

Quoted or closely paraphrased, with the ones most relevant to PGxTrust **in bold**:

- **"develop uncertainty estimation methods that allow the system to abstain from answering when
  evidence is insufficient or conflicting"**
- **"incorporate other pharmacogenomic guideline sources beyond CPIC and ClinPGx, such as DPWG …
  and the FDA Table of Pharmacogenetic Associations"**
- **"evaluate the system on full clinical case scenarios, rather than isolated QA pairs"**
- **"adaptive retrieval mechanisms to handle noisy or partially relevant evidence"**; GraphRAG,
  CRAG, agentic retrieval for "dispute resolution, or dynamic evidence verification"
- patient-specific attributes; clarifying questions; multilingual queries
- real-time lab values (INR, TDM); FHIR/EHR integration; red-teaming; bias evaluation
- **release the instruction dataset and propose a standardised PGx QA benchmark**
- compare BM25 / inverted-index / vector-DB retrieval backends

### 1.6 Weaknesses we can address without attacking the paper

These are observations from the full text. They are written to motivate an extension, not as
criticism.

1. **The outcome is association direction, not a prescribing action.** The three labels (decreased /
   increased / no association) do not say *what to do* (e.g., "avoid codeine", "reduce dose 50%").
2. **There is no executable baseline.** A CPIC lookup answers in-scope questions exactly, and the
   paper has no deterministic reference to measure the LLM against.
3. **The split leaks entities.** The paper itself acknowledges this (§6.5).
4. **Sources are unversioned.** The CPIC data and ClinPGx text were accessed around April–July 2026
   with no release tag recorded. Answers cannot be checked against "the guideline as of date X".
5. **Abstention and conflict handling were prompted but not measured.**

---

## 2. Official structured resources

### 2.1 CPIC database and API

- REST API `api.cpicpgx.org` (PostgREST), live and queried 2026-10-09: 29 guidelines, 2115
  recommendations. Each recommendation has `lookupkey` (gene → phenotype/activity/allele status),
  `drugrecommendation` and `classification` (strength).
- **Versioning:** 88 tagged releases on GitHub `cpicpgx/cpic-data`, from v0.6 (2020-05-17) to v1.60.1
  (2026-08-12). Whole-DB SQL dumps exist per release at
  `files.cpicpgx.org/data/database/cpic_db_dump-v<X>.sql.gz` (spot-checked v1.30.0 and v1.54.0).
  The schema includes a `change_log` table.
- **Caveat:** the API's `recommendation.version` field is `1` for all 2115 rows. **It is not a
  change history.** Changes must be reconstructed by diffing release dumps.
- Substantive recent releases include v1.54.0 (2026-02-04, thiopurines guideline update) and v1.59.0
  (2026-06-17, ondansetron guideline + RYR1 + PharmVar update).

### 2.2 PharmCAT

- Latest release **v3.4.0 (2026-07-14)** (GitHub `PharmGKB/PharmCAT`). Tool papers: Sangkuhl et al.,
  CPT 2019 (doi:10.1002/cpt.1568); Li et al., CPT 2022 (doi:10.1002/cpt.2790).
- Pipeline: VCF → Named Allele Matcher → diplotype → phenotype / activity score / allele status →
  recommendation lookup (Phenotyper + Reporter). Outside calls (e.g., CYP2D6 from another caller)
  are accepted.
- **Sources:** CPIC (machine-readable); **DPWG only via ClinPGx curation**, because DPWG publishes PDFs
  only; FDA labels via ClinPGx, limited to genes with CPIC/DPWG guidelines.
- **Multi-source handling:** annotations are "tagged … with a 'source' property" and "grouped …
  under a 'drug' object". **PharmCAT reports CPIC and DPWG side by side and does not reconcile them.**
- Missing VCF positions are reported and can yield multiple candidate diplotypes. CYP2D6 calling
  from VCF is research-mode only.

### 2.3 ClinPGx (formerly PharmGKB)

This is the curated, machine-readable source for DPWG and other guideline annotations. The bulk
download endpoint redirected (HTTP 303) for curl on 2026-10-09. The access route and licence still
need confirming (P01).

---

## 3. Closest existing work

### 3.1 Closest competitor: Corpas et al. 2026 (under revision, *Cell Genomics*)

"Validated skills are necessary but not sufficient for trustworthy agentic genomics" (earlier
titles: "Trustworthy agentic genomics through versioned skill libraries…", "Executable skills
localise LLM errors to input interpretation…"). Repository
`manuelcorpas/24-AGENTIC-PGX-BENCHMARK`; data doi:10.5281/zenodo.21710055. Not yet peer reviewed;
the author founded ClawBio, whose format is evaluated.

Their matched five-cell design crosses **knowledge** (none / retrieved CPIC prose / structured rules)
with **mechanism** (LLM generates / code executes): 110 CPIC Level A cases × 8 LLMs × 3 replicates.

| Cell | Recommendation acc. | Lethal-class errors |
|---|---|---|
| free generation | 0.62 | 54 |
| RAG generation | 0.55 | 137 |
| RAG → execution | 0.97 | 23 |
| rules → execution | 0.97 | 25 |
| rules → generation | 0.97 | 26 |

Other findings:
- Under execution, errors localise to the **calling / input-interpretation step** (call concordance
  0.958).
- PharmCAT concordance is 83/83 where both emit, and PharmCAT abstains on 4.
- They run an adversarial corrupted-spec test and a four-cohort real-genome ancestry analysis.

**Consequence for us:** "executable PGx rules beat RAG" and "failure attribution to
retrieval/calling vs generation" are **already shown in PGx**. We must not claim either.

Their public work does **not** include, as far as we found:
- DPWG or any second guideline body (CPIC only);
- guideline-version drift (their versioning argument concerns model retirement and determinism, and
  no experiment changes the CPIC version);
- evaluation of explanations.

### 3.2 Other PGx LLM work

| Work | What it adds | Relevance |
|---|---|---|
| Zack et al. 2026, npj Digit Med | Agentic generation of CPIC-style recommendations from literature + FDA labels; 24 expert-rated items | Evidence synthesis; "faster updates" motivation; industry |
| Zack et al. 2025, Pharmacogenomics J | 599-scenario CPIC benchmark; fine-tuned Llama | Benchmark; industry |
| Keat et al. 2025, PSB (PGxQA) | Public PGx QA benchmark over CPIC Level A | Reusable evaluation set |
| Murugan et al. 2024, JAMIA | GPT-4 + CPIC RAG assistant | Early RAG baseline |
| Borishetty et al. 2025, medRxiv (PGxRAG) | RAG over CPIC + **DPWG** + **FDA**; 225 MCQs | Multi-source KB, but conflicts not evaluated (abstract) |
| Rector et al. 2025, arXiv (Sherpa Rx) | RAG over CPIC + PharmGKB; 260 queries | RAG baseline |
| Jeon et al. 2026, Comput Biol Med | Hierarchical RAG; weak on allele/numeric matching | Retrieval structure |
| Hsu et al. 2025, JMIR | Two-LLM agreement flags unstable guideline classifications for review | Uncertainty-routing precedent |

### 3.3 General-medical work that already owns the *methods*

| Capability | Already done (outside PGx) |
|---|---|
| Temporal guideline drift | DriftMedQA (Wu et al. 2025, synthetic "pseudo-outdated" items); TempoMed-Bench (Guan et al. 2026, real guideline successions) |
| Conflicting evidence + abstention | Han, Lan & Kilicoglu 2026 (conflict-aware abstention); MedAbstain (Machcha et al., EACL 2026) |
| Claim-level evidence verification | MedRAGChecker 2026; RAGChecker 2024; DrugClaw/DrugAudit 2026 (citation faithfulness) |
| Retriever vs generator failure attribution | RAGChecker 2024; RAG-X 2026 |
| Guideline conflict resolution | Xie et al. 2026 (neuro-symbolic, multimorbidity); Javadi et al. 2025 (contradictions in context) |

---

## 4. Coverage of the proposed combination

PGx rows only, computational work only (systems, methods, benchmarks, evaluations). The counts come
from `results/p00/literature_coverage.json`.

| Capability | PGx: fully covered by | PGx: partial | Method exists outside PGx | Verdict |
|---|---|---|---|---|
| Executable PGx rules | Corpas 2026, PharmCAT | — | — | **Covered** |
| RAG explanations | Arafin 2026, Murugan, PGxRAG, Sherpa Rx, Jeon, Zack 2026 | Corpas | yes | **Covered** |
| Failure attribution | Corpas 2026 | PharmCAT | RAGChecker, RAG-X | **Covered** |
| Uncertainty / abstention | — | Arafin (prompted, unmeasured), Corpas, Hsu, PharmCAT | Han 2026, MedAbstain | Method covered; PGx measurement thin |
| Evidence verification | — | Zack 2026, Hsu | MedRAGChecker, RAGChecker, DrugAudit | Method covered; PGx application thin |
| Multi-guideline conflict | — | PharmCAT (side by side, no reconciliation), PGxRAG (multi-source KB) | Han 2026, Xie 2026 | **Candidate gap in PGx** |
| Temporal guideline updates | — | Corpas (argued), Zack 2026 (motivation), Hsu, PharmCAT (pinned data) | DriftMedQA, TempoMed | **Candidate gap in PGx** |
| Counterfactual evaluation | — | Corpas (corrupted spec) | not found as a full "yes" | Small gap; an evaluation technique, not a paper |

---

## 5. What is defensible and what is not

### Already well covered: do **not** claim as contributions

1. **RAG improves LLM answers to PGx questions.** At least six PGx papers show this, including the
   target paper.
2. **Executable or deterministic CPIC rules are more reliable than LLM generation.** Corpas 2026
   shows this directly, with 13,199 evaluations. PharmCAT has been the deterministic engine since
   2019.
3. **Failure attribution (retrieval/calling vs generation).** Corpas 2026 in PGx; RAGChecker and
   RAG-X in general.
4. **Abstention, claim verification and conflict-aware abstention as methods.** These are covered
   in general medical NLP. We can *use* these methods, but we cannot claim them as new.
5. **"A trustworthy PGx assistant" combining all eight capabilities.** This would be a systems
   integration with no single falsifiable claim, and each piece has prior art. **Rejected as the
   paper question.**

### Appears defensible (subject to gates G0–G1)

**A. Guideline-version drift in PGx, measured on real CPIC release history.** Most defensible.
- Nothing in our matrix evaluates PGx LLM/RAG systems on *recommendations that actually changed
  between guideline versions*.
- General-medical drift work either synthesises "pseudo-outdated" items (DriftMedQA) or has no
  executable reference (TempoMed).
- CPIC is unusual in having **88 machine-readable tagged releases**. Drift items and their correct
  answers can therefore be derived *deterministically*, with no LLM judge and no clinician labelling.
  That removes the target paper's weakest evaluation components.
- The target paper's own data were unversioned, and its future work asks for "dynamic evidence
  verification".
- **Framing:** "an established failure mode (temporal drift), measured in PGx for the first time *in
  our search*, with an exact executable reference". Not a new method.

**B. CPIC–DPWG disagreement handling.** Defensible, but second choice.
- Disagreements are documented by human reviews (Abdullah-Koolmees 2021; Shugg 2020).
- PharmCAT shows both sources and does not reconcile them. PGxRAG mixes sources in one index without
  evaluating conflicts.
- We found no computational PGx study measuring whether systems *surface* or *collapse* the
  disagreement. This directly answers the target paper's stated future work (DPWG/FDA plus abstaining
  "when evidence is … conflicting").
- It is second choice because building ground truth needs ClinPGx DPWG annotations (licence and
  access are unresolved), plus a judgement about "correct handling" that is softer than A.

**C. Counterfactual genotype tests.** Useful as an *evaluation instrument* inside A or B, e.g. changing
the diplotype must change the answer, and changing an irrelevant gene must not. Too thin to be the
paper.

---

## 6. Gates before implementation

See `docs/research_protocol.md` §6 for the full gate definitions.

- **G0 (literature completion):** read the full texts of the PGx rows still marked `unknown` on
  `temporal_updates` and `multi_guideline_conflict` (Zack 2025, Zack 2026, PGxRAG, Jeon, Murugan,
  Rector, PGxQA). Also run a bioRxiv/medRxiv full-text search. If any of them already evaluates real
  version drift in PGx, candidate A is downgraded.
- **G1 (data feasibility):** diff CPIC release dumps and count substantive recommendation changes.
  The pass thresholds are frozen in the protocol before looking at the data.

---

## 7. Search log

| Source | Query / action | Date |
|---|---|---|
| Crossref, Semantic Scholar | DOI 10.3390/app16189148 metadata, abstract, 41 references | 2026-10-09 |
| MDPI CDN | full-text PDF (HTML blocked with 403) | 2026-10-09 |
| PubMed E-utilities | `(pharmacogenomic*[tiab] OR pharmacogenetic*[tiab]) AND (LLM/GPT/"large language model"/"retrieval-augmented"/agentic)[tiab] AND 2024:2026[dp]` → 15 hits; abstracts of 5 fetched | 2026-10-09 |
| arXiv API | `all:pharmacogenomic(s)`, `all:pharmacogenetic(s)` (≤100 each), filtered ≥2024 for LLM/RAG/agent terms → 3 hits (1 relevant: Sherpa Rx); 12 IDs verified by `id_list` | 2026-10-09 |
| Web search | Alkhateeb 2026 PGx; PharmCAT 3.x; LLM + PharmCAT tool calling; CPIC vs DPWG discordance; PGx LLM benchmarks 2025–26; temporal guideline drift; counterfactual genotype + abstention; PGxAI-Recommender; LLM PGx report explanation; CPIC versioning; multi-guideline conflict RAG; RAGChecker / failure attribution; HRAG Jeon; DPWG+CPIC+LLM; medRxiv PGx guideline update; Corpas/ClawBio; medical abstention + conflict; claim-level verification | 2026-10-09 |
| GitHub API | `manuelcorpas/24-AGENTIC-PGX-BENCHMARK` (README, RESULTS-REVISION.md); `PharmGKB/PharmCAT` releases + docs; `cpicpgx/cpic-data` releases (88) | 2026-10-09 |
| Zenodo | record 21710055 | 2026-10-09 |
| CPIC API | `/v1/recommendation`, `/v1/guideline` | 2026-10-09 |

**Known blind spots:**
- no Google Scholar, Scopus, IEEE Xplore or ACM DL;
- bioRxiv/medRxiv searched only through the web search engine;
- non-English literature not searched;
- full texts not read for most PGx rows (abstract only).
