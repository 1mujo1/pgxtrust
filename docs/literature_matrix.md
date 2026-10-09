# Literature matrix

> Generated from `literature/literature_matrix.csv` by
> `scripts/render_literature_matrix.py`. Edit the CSV, not this file.

Legend: ● yes · ◐ partial · ○ no · ? unknown (not read in enough depth) · – not applicable

| ID | Work | Year | Domain | Kind | Access | Rules | RAG | Conflict | Verify | Temporal | Counterf. | Abstain | Attrib. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `arafin2026` | Arafin, Moniruzzaman & Alkhateeb | 2026 | pgx | system | full_text | ○ | ● | ○ | ○ | ○ | ○ | ◐ | ○ |
| `corpas2026` | Corpas et al. | 2026 | pgx | benchmark | repo_results | ● | ◐ | ○ | ○ | ◐ | ◐ | ◐ | ● |
| `zack2026npj` | Zack et al. | 2026 | pgx | system | full_text | ○ | ● | ○ | ◐ | ◐ | ? | ○ | ? |
| `zack2025pgxj` | Zack et al. | 2025 | pgx | benchmark | full_text | ○ | ● | ○ | ? | ○ | ? | ○ | ? |
| `keat2025pgxqa` | Keat et al. (PGxQA) | 2025 | pgx | benchmark | full_text | ? | ? | ○ | ? | ◐ | ? | ● | ? |
| `murugan2024` | Murugan et al. | 2024 | pgx | system | full_text | ? | ● | ◐ | ? | ○ | ? | ○ | ◐ |
| `borishetty2025pgxrag` | Borishetty et al. (PGxRAG) | 2025 | pgx | system | full_text | ? | ● | ◐ | ? | ○ | ? | ○ | ? |
| `rector2025sherpa` | Rector et al. (Sherpa Rx) | 2025 | pgx | system | full_text | ? | ● | ○ | ? | ○ | ? | ○ | ? |
| `jeon2026hrag` | Jeon et al. | 2026 | pgx | system | abstract | ? | ● | ? | ? | ? | ? | ? | ? |
| `hsu2025jmir` | Hsu et al. | 2025 | pgx | evaluation | abstract | ? | ? | ? | ◐ | ◐ | ? | ◐ | ? |
| `pharmcat` | PharmCAT (Sangkuhl et al. 2019; Li et al. 2022) | 2026 | pgx | system | docs | ● | ○ | ◐ | – | ◐ | – | ◐ | ◐ |
| `cpicdb` | CPIC database and API | 2026 | pgx | resource | docs | ◐ | – | – | – | ◐ | – | – | – |
| `clinpgx` | ClinPGx (formerly PharmGKB) guideline annotations | 2026 | pgx | resource | docs | – | – | ◐ | – | ? | – | – | – |
| `abdullahkoolmees2021` | Abdullah-Koolmees, van Keulen, Nijenhuis et al. | 2021 | pgx | review | search_snippet | – | – | ● | – | – | – | – | – |
| `shugg2020` | Shugg, Pasternak, London et al. | 2020 | pgx | review | search_snippet | – | – | ● | – | – | – | – | – |
| `wu2025drift` | Wu et al. (DriftMedQA / ConflictMedQA) | 2025 | general_medical | benchmark | search_snippet | ? | ◐ | ◐ | ? | ● | ? | ? | ? |
| `guan2026tempomed` | Guan et al. (TempoMed-Bench) | 2026 | general_medical | benchmark | search_snippet | ? | ◐ | ? | ? | ● | ? | ? | ? |
| `han2026conflict` | Han, Lan & Kilicoglu | 2026 | general_medical | evaluation | search_snippet | ? | ◐ | ● | ? | ? | ◐ | ● | ? |
| `machcha2026abstain` | Machcha et al. (MedAbstain) | 2026 | general_medical | benchmark | search_snippet | ? | ? | ? | ? | ? | ◐ | ● | ? |
| `ji2026medragchecker` | Ji et al. (MedRAGChecker) | 2026 | general_medical | method | search_snippet | ? | ● | ? | ● | ? | ? | ? | ◐ |
| `ru2024ragchecker` | Ru et al. (RAGChecker) | 2024 | general | method | search_snippet | ? | ● | ? | ● | ? | ? | ? | ● |
| `sivakumar2026ragx` | Sivakumar et al. (RAG-X) | 2026 | general_medical | method | search_snippet | ? | ● | ? | ◐ | ? | ? | ? | ● |
| `xie2026neurosymbolic` | Xie et al. | 2026 | general_medical | method | search_snippet | ◐ | ? | ● | ? | ? | ? | ? | ? |
| `wang2026drugclaw` | Wang et al. (DrugClaw / DrugAudit) | 2026 | general_medical | system | search_snippet | ? | ● | ◐ | ● | ? | ? | ? | ? |
| `javadi2025contradictions` | Javadi et al. | 2025 | general_medical | evaluation | search_snippet | ? | ◐ | ● | ? | ◐ | ? | ? | ? |
| `overby2017ahrq` | Overby et al. (AHRQ R21 HS023390) | 2017 | pgx | system | docs | ● | – | – | – | ◐ | – | – | – |
| `cao2026guideskill` | Cao et al. (GuideSkill) | 2026 | general_medical | method | search_snippet | ● | ◐ | ? | ? | ? | ? | ? | ? |

## Details

### `arafin2026` — Arafin, Moniruzzaman & Alkhateeb (2026)

- **Title:** Evidence-Grounded Clinical Pharmacogenomics Decision Support: Integrating Fine-Tuned Large Language Models with Hybrid Retrieval-Augmented Generation
- **Venue / status:** Applied Sciences 16(18):9148 · peer_reviewed · read: full_text
- **Link:** 10.3390/app16189148
- **Problem / method:** PGx QA: LoRA fine-tuning + hybrid RAG (lexical filter + all-MiniLM-L6-v2 rerank) on Llama-3.1-8B-Instruct and Qwen3-8B
- **Knowledge sources:** CPIC DB tables (fine-tuning + retrieval); ClinPGx guideline text scraped via Playwright (retrieval)
- **Evidence / limitations:** TARGET PAPER. Free-text RAG answers; no executed rules or genotype calling. ClinPGx text covers DPWG but conflicts not handled. Prompt asks model to flag insufficient evidence (Sec 3.11) but this is not evaluated; abstention under insufficient/conflicting evidence listed as future work (Sec 6.7). Retrieval noise noted qualitatively only (Sec 6.6). Record-level split with gene/drug overlap across splits (Sec 6.5). Primary labels: rule-normalised 3 classes (decreased/increased/no significant association), 1000 held-out records. Judge: Mistral-7B-Instruct-v0.2. Manual review: 20 prompts by research team, no inter-rater agreement.
- **Relation to PGxTrust:** Paper being extended. Reproduce its RAG/LoRA arms on version-pinned data; its future work motivates temporal and conflict questions.

### `corpas2026` — Corpas et al. (2026)

- **Title:** Validated skills are necessary but not sufficient for trustworthy agentic genomics (revision title; earlier: Trustworthy agentic genomics through versioned skill libraries)
- **Venue / status:** Cell Genomics (under revision, CELL-GENOMICS-D-26-00551); repo + Zenodo · under_review · read: repo_results
- **Link:** https://github.com/manuelcorpas/24-AGENTIC-PGX-BENCHMARK
- **Problem / method:** Matched 5-cell comparison: knowledge (none / retrieved CPIC prose / structured rules) x mechanism (LLM generates / code executes); 110 CPIC Level A cases x 8 LLMs x 3 reps
- **Knowledge sources:** CPIC Level A; PharmGKB; PyPGx real-genome arm; PharmCAT concordance
- **Evidence / limitations:** CLOSEST COMPETITOR. RESULTS-REVISION.md (fetched 2026-10-09): executed CPIC mapping ~0.97 recommendation accuracy; RAG generation 0.55 with 137 lethal-class errors vs 54 for free generation. Under execution, residual error localises to the calling/input-interpretation step (call concordance 0.958). PharmCAT concordance 83/83 where both emit; PharmCAT abstains on 4. Adversarial scrambled/reversed specs = partial counterfactual. CPIC only (Zenodo 10.5281/zenodo.21710055 does not mention DPWG). Argues for versioned skills (model retirement) but public results contain no guideline-version-drift experiment. RAG used for answering; explanations not evaluated. Founder conflict of interest (ClawBio) declared. Not yet peer reviewed. G0: bioRxiv preprint 10.64898/2026.06.11.731523 (v1 2026-06-15) read in full (keyword-targeted): 'versioned' = provenance of skills; RECOMMENDS 'regression-testing the skill against guideline updates' but no experiment varies the guideline version.
- **Relation to PGxTrust:** Pre-empts 'executable rules beat RAG' and failure attribution. PGxTrust must cite it and not claim those; its CPIC-only, single-version design leaves version drift and DPWG open.

### `zack2026npj` — Zack et al. (2026)

- **Title:** An agentic AI system for automated pharmacogenomic recommendation generation
- **Venue / status:** npj Digital Medicine 9:541 · peer_reviewed · read: full_text
- **Link:** 10.1038/s41746-026-02590-w
- **Problem / method:** Agentic pipeline generating CPIC-style recommendations from full-text literature and FDA labels
- **Knowledge sources:** Full-text literature; FDA drug labels; CPIC as reference
- **Evidence / limitations:** G0 full text (PMC13369662; keyword-targeted reading). Agentic LLM pipeline from literature + FDA labels; 24 expert-rated recommendations, 22 articles for extraction. Describes an 'updater mode, suggesting revisions for outdated guidelines' but does NOT evaluate it; no cross-version test. DPWG only mentioned as a possible adaptation. No abstention/uncertainty measurement. Industry authors (PGxAI Inc.).
- **Relation to PGxTrust:** Evidence-synthesis competitor; check full text for any update/version evaluation (G0).

### `zack2025pgxj` — Zack et al. (2025)

- **Title:** Benchmarking large language models for replication of guideline-based PGx recommendations
- **Venue / status:** Pharmacogenomics Journal 25:23 · peer_reviewed · read: full_text
- **Link:** 10.1038/s41397-025-00383-0
- **Problem / method:** Benchmark of 599 CPIC gene-drug-phenotype scenarios; 5 LLMs incl. fine-tuned Llama; LLM Score validated by experts
- **Knowledge sources:** CPIC
- **Evidence / limitations:** G0 full text (Research Square preprint rs-6630450, version of record = this paper; keyword-targeted reading). CPIC-only benchmark: 'we did not incorporate data from other authorities like DPWG'. Contrasts naive vs retrieval/fine-tuning-enhanced LLMs. 'model confidence was not explicitly quantified'. No version/update evaluation. Industry authors (PGxAI Inc.).
- **Relation to PGxTrust:** Possible benchmark overlap; check for DPWG scenarios and version handling (G0).

### `keat2025pgxqa` — Keat et al. (PGxQA) (2025)

- **Title:** PGxQA: A Resource for Evaluating LLM Performance for Pharmacogenomic QA Tasks
- **Venue / status:** Pacific Symposium on Biocomputing 30:229-246 · peer_reviewed · read: full_text
- **Link:** 10.1142/9789819807024_0017
- **Problem / method:** PGxQA benchmark: clinician/patient/researcher PGx questions over CPIC Level A; GPT-4o and others
- **Knowledge sources:** CPIC; PharmGKB
- **Evidence / limitations:** G0 full text (PSB proceedings PDF; keyword-targeted reading). Measures REFUSAL rates on misspecified questions (fabricated genes/alleles) vs properly specified ones: Llama/Gemini <0.2 refusal on misspecified queries. Notes PGx guidelines are 'revised and updated irregularly' and that questions are regenerated from the routinely updated CPIC DB, but no cross-version evaluation. DPWG mentioned only as background.
- **Relation to PGxTrust:** Reusable public QA set; candidate external sanity benchmark.

### `murugan2024` — Murugan et al. (2024)

- **Title:** Empowering personalized pharmacogenomics with generative AI solutions
- **Venue / status:** JAMIA 31(6):1356-1366 · peer_reviewed · read: full_text
- **Link:** 10.1093/jamia/ocae039
- **Problem / method:** GPT-4 assistant with RAG over a CPIC knowledge base, prompt engineering and guardrails
- **Knowledge sources:** CPIC
- **Evidence / limitations:** G0 full text (PMC11105140, read via summarising fetch). KB includes CPIC + DPWG recommendations + FDA rosuvastatin label, but agreement/conflict between sources not evaluated. No version/update evaluation (only access dates). No abstention measurement. Retrieval tested separately (diplotype recall 0.61-0.72) = partial attribution. 47 provider + 33 patient queries, 4 expert raters.
- **Relation to PGxTrust:** Early CPIC RAG baseline to cite.

### `borishetty2025pgxrag` — Borishetty et al. (PGxRAG) (2025)

- **Title:** PGxRAG: A Retrieval Augmented Generation supported Pharmacogenomics Assistant
- **Venue / status:** medRxiv · preprint · read: full_text
- **Link:** 10.1101/2025.09.24.25336524
- **Problem / method:** 4 LLMs with/without RAG; 225 multiple-choice questions; hyperparameter sweep
- **Knowledge sources:** ClinPGx/PharmGKB, CPIC, DPWG (KNMP), FDA; 2617 chunks
- **Evidence / limitations:** G0 full text (medRxiv v3 JATS XML; keyword-targeted reading). KB: CPIC, DPWG (KNMP PDFs), RNPGx, FDA, PharmGKB; chunks tagged with source metadata. 225 MCQs with one SME-verified answer; disagreements between sources not discussed or evaluated. No version or abstention evaluation.
- **Relation to PGxTrust:** Closest multi-guideline RAG; check whether conflicts are evaluated (G0).

### `rector2025sherpa` — Rector et al. (Sherpa Rx) (2025)

- **Title:** Validating Pharmacogenomics Generative Artificial Intelligence Query Prompts Using Retrieval-Augmented Generation (RAG)
- **Venue / status:** arXiv · preprint · read: full_text
- **Link:** arXiv:2507.21453
- **Problem / method:** RAG PGx assistant evaluated on 260 queries over 26 CPIC guidelines
- **Knowledge sources:** CPIC; PharmGKB
- **Evidence / limitations:** G0 full text (arXiv PDF; keyword-targeted reading). RAG over CPIC + PharmGKB; 260 queries over 26 CPIC guidelines. No version, conflict or refusal/abstention evaluation found.
- **Relation to PGxTrust:** RAG baseline to cite.

### `jeon2026hrag` — Jeon et al. (2026)

- **Title:** Hierarchical RAG enhances a pharmacogenomic AI assistant in guideline related queries
- **Venue / status:** Computers in Biology and Medicine 200:111323 · peer_reviewed · read: abstract
- **Link:** 10.1016/j.compbiomed.2025.111323
- **Problem / method:** Hierarchical RAG over PGx guidelines for 5-FU, capecitabine, tamoxifen; PGxQA + RAGAS + human evaluation
- **Knowledge sources:** PGx guidelines organised as trees (one per guideline)
- **Evidence / limitations:** Abstract only. Both HRAG and RAG weak on numerical/entity matching (allele definitions); HRAG F1 0.89 vs RAG 0.80 on phenotype-to-guideline.
- **Relation to PGxTrust:** Retrieval-structure baseline; its weakness on allele/numeric matching supports executable lookup.

### `hsu2025jmir` — Hsu et al. (2025)

- **Title:** Extracting Clinical Guideline Information Using Two Large Language Models: Evaluation Study
- **Venue / status:** Journal of Medical Internet Research 27:e73486 · peer_reviewed · read: abstract
- **Link:** 10.2196/73486
- **Problem / method:** GPT-4o and Gemini-1.5-Pro classify 385 PGx guideline recommendations; 20 repeats each; agreement thresholds flag unstable items for manual review
- **Knowledge sources:** PGx guidelines (mostly CPIC)
- **Evidence / limitations:** Aim is supporting CDS updates (partial temporal). Cross-model and repeat-agreement flagging routes uncertain items to humans (partial verification and abstention). 93.5% / 92.7% accuracy vs expert labels.
- **Relation to PGxTrust:** Precedent for uncertainty routing in PGx guideline maintenance.

### `pharmcat` — PharmCAT (Sangkuhl et al. 2019; Li et al. 2022) (2026)

- **Title:** Pharmacogenomics Clinical Annotation Tool (PharmCAT)
- **Venue / status:** Clin Pharmacol Ther (tool papers); software v3.4.0 2026-07-14 · software · read: docs
- **Link:** 10.1002/cpt.1568
- **Problem / method:** Deterministic VCF -> named alleles -> diplotype -> phenotype/activity score -> guideline recommendation report
- **Knowledge sources:** CPIC; DPWG via ClinPGx curated annotations; FDA labels via ClinPGx
- **Evidence / limitations:** docs/methods/Matching-Recommendations.md: CPIC and DPWG annotations are tagged by source and grouped by drug; no reconciliation of disagreements. Guideline data pinned per release. Missing VCF positions are reported and may yield multiple candidate diplotypes; CYP2D6 from VCF is research-mode only. How-to paper: 10.1002/cpt.2790.
- **Relation to PGxTrust:** Deterministic comparator (B4). Shows CPIC and DPWG side by side; PGxTrust could add explicit disagreement labels and version-aware answers.

### `cpicdb` — CPIC database and API (2026)

- **Title:** CPIC database, API and versioned data releases
- **Venue / status:** cpicpgx/cpic-data (GitHub) + api.cpicpgx.org · resource · read: docs
- **Link:** https://github.com/cpicpgx/cpic-data
- **Problem / method:** Structured CPIC alleles, phenotype mappings and recommendations; REST API; versioned whole-database SQL dumps
- **Knowledge sources:** CPIC
- **Evidence / limitations:** 88 tagged releases (v0.6 2020-05-17 to v1.60.1 2026-08-12); per-release dumps at files.cpicpgx.org/data/database/cpic_db_dump-vX.sql.gz (HTTP 206 checked for v1.30.0 and v1.54.0); schema has a change_log table. API field recommendation.version = 1 for all 2115 rows (queried 2026-10-09), so it is NOT a usable change history. Examples of substantive releases: v1.54.0 thiopurines update (2026-02-04); v1.59.0 ondansetron guideline + RYR1 (2026-06-17).
- **Relation to PGxTrust:** Ground-truth source for the temporal benchmark (release dumps); API version field unusable.

### `clinpgx` — ClinPGx (formerly PharmGKB) guideline annotations (2026)

- **Title:** ClinPGx clinical guideline annotations
- **Venue / status:** clinpgx.org · resource · read: docs
- **Link:** https://www.clinpgx.org
- **Problem / method:** Curated machine-readable guideline annotations incl. DPWG (published by DPWG only as PDFs)
- **Knowledge sources:** CPIC, DPWG, other guideline bodies; FDA labels
- **Evidence / limitations:** Per PharmCAT docs, DPWG data reaches software only via ClinPGx curation. Bulk download endpoint did not return a file to curl on 2026-10-09 (HTTP 303); access route to be resolved in P01.
- **Relation to PGxTrust:** Only machine-readable DPWG route; needed for the conflict pivot.

### `abdullahkoolmees2021` — Abdullah-Koolmees, van Keulen, Nijenhuis et al. (2021)

- **Title:** Pharmacogenetics Guidelines: Overview and Comparison of the DPWG, CPIC, CPNDS, and RNPGx Guidelines
- **Venue / status:** Frontiers in Pharmacology 11:595219 · peer_reviewed · read: search_snippet
- **Link:** 10.3389/fphar.2020.595219
- **Problem / method:** Expert comparison of DPWG, CPIC, CPNDS and RNPGx guideline methods, genotype-to-phenotype translation and recommendations
- **Knowledge sources:** DPWG, CPIC, CPNDS, RNPGx
- **Evidence / limitations:** Human, descriptive comparison: documents that guideline bodies differ (e.g., fluoropyrimidine dosing, terminology). Ground-truth source for CPIC-DPWG disagreements; not a computational system.
- **Relation to PGxTrust:** Source of documented CPIC-DPWG disagreements (conflict ground truth).

### `shugg2020` — Shugg, Pasternak, London et al. (2020)

- **Title:** Prevalence and types of inconsistencies in clinical pharmacogenetic recommendations among major U.S. sources
- **Venue / status:** npj Genomic Medicine · peer_reviewed · read: search_snippet
- **Link:** 10.1038/s41525-020-00156-7
- **Problem / method:** Prevalence and types of inconsistencies in clinical PGx recommendations among major U.S. sources
- **Knowledge sources:** CPIC, FDA labels and other U.S. sources
- **Evidence / limitations:** Human, descriptive. Establishes that source disagreement is a real and measured phenomenon in PGx.
- **Relation to PGxTrust:** Evidence that source disagreement in PGx is common.

### `wu2025drift` — Wu et al. (DriftMedQA / ConflictMedQA) (2025)

- **Title:** Assessing and Mitigating Medical Knowledge Drift and Conflicts in Large Language Models
- **Venue / status:** arXiv · preprint · read: search_snippet
- **Link:** arXiv:2505.07968
- **Problem / method:** Benchmark of current vs pseudo-outdated recommendations (4290 scenarios, 7 LLMs); RAG + preference fine-tuning mitigation
- **Knowledge sources:** General clinical guidelines
- **Evidence / limitations:** Temporal drift covered for general medicine, using synthetic 'pseudo-outdated' recommendations rather than real version histories. Not PGx.
- **Relation to PGxTrust:** General-medical temporal-drift method; PGxTrust instantiates drift on real CPIC releases instead of synthetic items.

### `guan2026tempomed` — Guan et al. (TempoMed-Bench) (2026)

- **Title:** Large Language Models Lack Temporal Awareness of Medical Knowledge
- **Venue / status:** arXiv · preprint · read: search_snippet
- **Link:** arXiv:2605.13045
- **Problem / method:** Benchmark built from successive clinical guideline documents; tests current vs historical recommendation recall
- **Knowledge sources:** Successive guideline versions (general medicine)
- **Evidence / limitations:** Real guideline successions; reports agentic RAG only partially fixes temporal errors. Not PGx; no executable-rule baseline.
- **Relation to PGxTrust:** Closest general-medical temporal benchmark; PGxTrust adds PGx, exact executable gold and a version-pinned reference.

### `han2026conflict` — Han, Lan & Kilicoglu (2026)

- **Title:** When Evidence Conflicts: Uncertainty and Order Effects in Retrieval-Augmented Biomedical Question Answering
- **Venue / status:** BioNLP 2026; arXiv · preprint · read: search_snippet
- **Link:** arXiv:2605.14115
- **Problem / method:** RAG biomedical QA under conflicting evidence (HealthContradict); order effects; conflict-aware abstention score
- **Knowledge sources:** HealthContradict documents
- **Evidence / limitations:** Document-order swaps flip 11.4-25.2% of predictions (perturbation = partial counterfactual). Conflict-aware abstention beats confidence-only. Not PGx.
- **Relation to PGxTrust:** Method to borrow for conflict-aware abstention.

### `machcha2026abstain` — Machcha et al. (MedAbstain) (2026)

- **Title:** Knowing When to Abstain: Medical LLMs Under Clinical Uncertainty
- **Venue / status:** EACL 2026; arXiv · peer_reviewed · read: search_snippet
- **Link:** arXiv:2601.12471
- **Problem / method:** Abstention benchmark for medical MCQA: conformal prediction, adversarial perturbations, explicit abstain option
- **Knowledge sources:** Medical MCQA datasets
- **Evidence / limitations:** Abstention in medical QA is covered as a general method. Not PGx.
- **Relation to PGxTrust:** Method to borrow for abstention evaluation.

### `ji2026medragchecker` — Ji et al. (MedRAGChecker) (2026)

- **Title:** MedRAGChecker: Claim-Level Verification for Biomedical Retrieval-Augmented Generation
- **Venue / status:** arXiv · preprint · read: search_snippet
- **Link:** arXiv:2601.06519
- **Problem / method:** Claim-level NLI verification of biomedical RAG answers + KG consistency; distilled checkers
- **Knowledge sources:** Biomedical QA benchmarks
- **Evidence / limitations:** Claim-level evidence verification is covered as a general method. Not PGx.
- **Relation to PGxTrust:** Method to borrow for claim-level explanation verification.

### `ru2024ragchecker` — Ru et al. (RAGChecker) (2024)

- **Title:** RAGChecker: A Fine-grained Framework for Diagnosing Retrieval-Augmented Generation
- **Venue / status:** arXiv · preprint · read: search_snippet
- **Link:** arXiv:2408.08067
- **Problem / method:** Fine-grained claim-level diagnosis of retriever vs generator errors in RAG
- **Knowledge sources:** 10-domain benchmark
- **Evidence / limitations:** Retriever-vs-generator failure attribution is an established general method.
- **Relation to PGxTrust:** Method to borrow for retriever-vs-generator attribution.

### `sivakumar2026ragx` — Sivakumar et al. (RAG-X) (2026)

- **Title:** RAG-X: Systematic Diagnosis of Retrieval-Augmented Generation for Medical Question Answering
- **Venue / status:** arXiv · preprint · read: search_snippet
- **Link:** arXiv:2603.03541
- **Problem / method:** Diagnostic framework separating retrieval and generation failures in medical QA; context-utilisation metrics
- **Knowledge sources:** Medical QA datasets
- **Evidence / limitations:** Failure attribution for medical RAG covered as a general method. Not PGx.
- **Relation to PGxTrust:** Method to borrow for medical RAG failure diagnosis.

### `xie2026neurosymbolic` — Xie et al. (2026)

- **Title:** Neuro-Symbolic Resolution of Recommendation Conflicts in Multimorbidity Clinical Guidelines
- **Venue / status:** arXiv · preprint · read: search_snippet
- **Link:** arXiv:2604.17340
- **Problem / method:** Neuro-symbolic resolution of recommendation conflicts across multimorbidity guidelines
- **Knowledge sources:** General clinical guidelines
- **Evidence / limitations:** Guideline-conflict resolution with symbolic components exists for multimorbidity (venue reported as AAAI 2026 in a snippet; unverified). Not PGx.
- **Relation to PGxTrust:** Neuro-symbolic conflict resolution outside PGx; cite for conflict engine design.

### `wang2026drugclaw` — Wang et al. (DrugClaw / DrugAudit) (2026)

- **Title:** DrugClaw and DrugAudit: A Primary-Source-Grounded Agent and Authority-Aware Benchmark for Drug-Information Question Answering
- **Venue / status:** arXiv · preprint · read: search_snippet
- **Link:** arXiv:2606.01434
- **Problem / method:** Primary-source-grounded multi-agent drug-information QA; authority-aware benchmark (3772 items) scoring source match and citation faithfulness
- **Knowledge sources:** Regulatory and peer-reviewed drug records
- **Evidence / limitations:** Authority-aware source scoring and citation faithfulness for drug information; PGx/CPIC/DPWG not mentioned in abstract.
- **Relation to PGxTrust:** Authority-aware drug-information benchmark; cite for source/authority scoring.

### `javadi2025contradictions` — Javadi et al. (2025)

- **Title:** Contradictions in Context: Challenges for Retrieval-Augmented Generation in Healthcare
- **Venue / status:** arXiv · preprint · read: search_snippet
- **Link:** arXiv:2511.06668
- **Problem / method:** Contradictions in retrieved context (incl. outdated PubMed abstracts) and their effect on healthcare RAG
- **Knowledge sources:** PubMed abstracts
- **Evidence / limitations:** Retrieved-context contradiction and staleness for healthcare RAG. Not PGx.
- **Relation to PGxTrust:** Evidence that stale or contradictory retrieved context harms healthcare RAG.

### `overby2017ahrq` — Overby et al. (AHRQ R21 HS023390) (2017)

- **Title:** Electronic Health Record-linked Decision Support for Communicating Genomic Data
- **Venue / status:** AHRQ project report (Johns Hopkins, 2014-2017) · resource · read: docs
- **Link:** https://digital.ahrq.gov/ahrq-funded-projects/electronic-health-record-linked-decision-support-communicating-genomic-data
- **Problem / method:** Translate a CPIC guideline into computer-interpretable CDS mapped to EHR data elements; services for revising CDS content when guidelines change
- **Knowledge sources:** CPIC
- **Evidence / limitations:** Rule-based (non-LLM) PGx CDS. Built services to revise CDS content after guideline changes; no evaluation of answer correctness across versions reported on the project page.
- **Relation to PGxTrust:** Shows guideline-update maintenance is a known implementation problem in rule-based PGx CDS; PGxTrust measures it for LLM/RAG systems.

### `cao2026guideskill` — Cao et al. (GuideSkill) (2026)

- **Title:** GuideSkill: Evolving Executable LLM Agent Skills for Guideline-Grounded Clinical Reasoning
- **Venue / status:** arXiv · preprint · read: search_snippet
- **Link:** arXiv:2607.26160
- **Problem / method:** Compile guideline diagnostic criteria into executable functions used by an LLM agent; compared with guideline RAG
- **Knowledge sources:** Clinical practice guidelines (diagnosis)
- **Evidence / limitations:** Reports +13.45% macro accuracy over guideline RAG across 4 benchmarks and 4 backbones (abstract). Executable guideline logic beating RAG is established outside PGx too.
- **Relation to PGxTrust:** Further evidence that 'execute rules, do not retrieve prose' is not a novel claim.

