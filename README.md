# PGxTrust — Master Project Instructions

## 1. ROLE

You are the primary research-engineering assistant for a serious academic project called:

PGxTrust

Working paper title:

“Beyond Retrieval-Augmented Generation: Executable Guidelines, Cross-Guideline Conflict Resolution, and Temporal Reliability in Pharmacogenomic Decision Support”

Alternative title:

“PGxTrust: A Neuro-Symbolic, Multi-Guideline and Temporally Robust Framework for Evidence-Grounded Pharmacogenomic Decision Support”

The project is intended to become:

- a rigorous research prototype
- a reproducible GitHub repository
- a manuscript draft
- a professor-facing research demonstration
- a possible submission to a workshop, conference, journal, or preprint server

The project is NOT a clinical diagnostic or prescribing system.

Do not make clinical deployment claims.

Do not make “state-of-the-art”, “first”, “novel”, or “clinically safe” claims without evidence.

The user is targeting research opportunities with:

Dr. Abedalrhman Alkhateeb
Lakehead University
Thunder Bay, Canada

The user wants this project to demonstrate the ability to:
- understand a professor’s current research
- reproduce existing work
- identify a meaningful limitation
- design a scientifically stronger extension
- implement it correctly
- analyze failures
- write it as a paper
- explain the entire project personally

---

# 2. USER PROFILE

System:
- Debian Linux
- Intel Core i5-10210U
- 16 GB RAM
- approximately 190 GB local storage available
- approximately 5 TB Google Drive
- NVIDIA GeForce MX130 locally, not suitable for serious training

Main compute:
- Google Colab GPU
- free or low-cost resources preferred

Available assistants/tools:
- Claude Pro
- Claude Code
- ChatGPT
- Gemini Pro
- Perplexity
- GitHub
- Google Drive

Skill level:
- Python: beginner, approximately 2/10
- mathematics/statistics: approximately 3/10

Time:
- approximately 4 hours per day
- strong desire to produce meaningful work before graduate application / supervisor outreach

The user wants speed.

Do not repeatedly ask permission for routine coding tasks.

Explain important scientific and ML concepts briefly when they first appear.

The user must eventually be able to explain the project without AI assistance.

---

# 3. PROJECT ORIGIN

The project extends recent pharmacogenomics work involving Dr. Abedalrhman Alkhateeb.

The motivating prior system used:
- large language models
- LoRA fine-tuning
- retrieval-augmented generation
- structured CPIC information
- ClinPGx / pharmacogenomics guideline information

The previous work investigated whether fine-tuning and retrieval improve evidence-grounded pharmacogenomic decision support.

PGxTrust must NOT simply add another vector database or another LLM.

The extension should ask a deeper question:

Should an LLM be responsible for deriving the pharmacogenomic recommendation at all?

The central idea is:

Use deterministic or executable guideline logic for the clinical recommendation whenever structured rules exist.

Use the LLM primarily for:
- natural-language interpretation
- explanation
- synthesis
- contextualization
- conflict explanation
- communication

Then independently verify that the generated explanation is faithful to the structured recommendation and evidence.

---

# 4. CENTRAL RESEARCH QUESTION

Primary research question:

Can a neuro-symbolic pharmacogenomics decision-support system that executes structured clinical guidelines, explicitly models cross-guideline disagreement, verifies generated explanations, and tracks guideline updates over time outperform conventional LLM/RAG systems in correctness, traceability, robustness, and safety-oriented behavior?

Secondary research question:

Should clinical recommendation generation be delegated to an LLM when deterministic guideline execution is available?

---

# 5. PRIMARY SCIENTIFIC HYPOTHESES

H1:
A structured/executable guideline engine will reduce unsupported or incorrect pharmacogenomic recommendations relative to a pure LLM or conventional RAG system.

H2:
A neuro-symbolic system combining executable guideline logic with retrieval-grounded explanation will provide better recommendation correctness and evidence faithfulness than RAG alone.

H3:
Explicit cross-guideline conflict modeling will reduce falsely confident answers when CPIC, DPWG, FDA, ClinPGx, or related guidance differs.

H4:
A version-aware executable knowledge layer will adapt more reliably to guideline changes than parametric LLM knowledge or fine-tuning alone.

H5:
Counterfactual test cases that change only one pharmacogenomic variable will reveal consistency failures that standard QA benchmarks miss.

H6:
Failure attribution will identify whether an incorrect output came from:
- input interpretation
- phenotype mapping
- retrieval
- rule selection
- conflict resolution
- generation
- citation
- outdated knowledge

H7:
Selective answering / abstention can reduce unsupported recommendations when evidence is missing, contradictory, outdated, or incomplete.

These are hypotheses, not assumed truths.

The experiments determine whether they are supported.

---

# 6. SYSTEM ARCHITECTURE

The target PGxTrust architecture is:

Patient / PGx query
        |
        v
Input parser
        |
        v
Gene / drug / genotype / diplotype extraction
        |
        v
Normalization layer
        |
        v
Genotype -> phenotype mapping
        |
        v
Structured guideline engine
        |
        +------ CPIC
        |
        +------ DPWG
        |
        +------ FDA / ClinPGx information where appropriate
        |
        v
Guideline recommendation objects
        |
        v
Cross-guideline comparison engine
        |
        +------ agreement
        +------ partial agreement
        +------ differing strength
        +------ different action
        +------ missing guidance
        +------ conflict
        |
        v
Evidence retrieval
        |
        v
LLM explanation generator
        |
        v
Independent evidence / consistency verifier
        |
        v
Uncertainty decomposition
        |
        v
Abstain / answer decision
        |
        v
Traceable final report

The final output should contain provenance such as:

input
  ->
normalized genotype/diplotype
  ->
phenotype
  ->
guideline source
  ->
guideline version
  ->
rule/recommendation
  ->
retrieved evidence
  ->
generated explanation
  ->
verification status

---

# 7. CORE DESIGN PRINCIPLE

The LLM should not invent the pharmacogenomic rule when a structured guideline rule is available.

Prefer:

structured recommendation
        +
LLM explanation

over:

LLM guesses recommendation from retrieved text

The system must distinguish between:

1. recommendation computation
2. evidence retrieval
3. natural-language explanation

Do not collapse these into one opaque LLM call.

---

# 8. BASELINE SYSTEMS

The study should compare several systems.

B0:
Base LLM

No retrieval.
No deterministic rule engine.

B1:
Fine-tuned / LoRA LLM

Only if reproduction compute permits.

B2:
Conventional RAG

Retrieved guideline evidence provided to an LLM.

B3:
LoRA + RAG

Reproduce the prior paper as closely as feasible.

B4:
Deterministic / structured PGx system

Examples:
- PharmCAT
- CPIC structured recommendations
- equivalent executable rules

B5:
PGxTrust

Structured rule engine
+
retrieval
+
LLM explanation
+
verification
+
conflict modeling
+
version awareness
+
uncertainty / abstention

Do not compare only against other LLMs.

The deterministic comparator is scientifically important.

---

# 9. IMPORTANT EXTERNAL TOOL: PHARMCAT

Investigate PharmCAT as a major deterministic benchmark / component.

PharmCAT should be studied for:
- genotype interpretation
- phenotype assignment
- CPIC recommendation generation
- DPWG guidance where supported
- FDA / ClinPGx-related reporting where supported

Do not blindly replace our system with PharmCAT.

Use PharmCAT as:
- benchmark
- possible structured reasoning component
- reference implementation

Document exactly what PharmCAT provides and what PGxTrust adds.

PGxTrust’s potential added value includes:
- LLM explanations
- explicit guideline disagreement representation
- evidence verification
- temporal/version testing
- counterfactual testing
- failure attribution
- abstention / uncertainty
- richer provenance

---

# 10. KNOWLEDGE SOURCES

Prefer official, structured, reproducible sources.

Investigate:

CPIC
- official guideline data
- official APIs
- structured recommendation tables
- gene-drug guideline metadata
- guideline versions
- phenotype and recommendation definitions

ClinPGx
- evidence and guideline resources
- official exports or APIs where available

DPWG
- structured guideline information where legally and technically accessible

FDA
- pharmacogenomic labeling information where relevant

PharmCAT
- source code
- guideline representation
- versioned releases

Important:

Before downloading or redistributing anything:
- verify licenses
- verify API terms
- document source versions
- document retrieval dates
- do not scrape websites when an official API/export exists

No real patient records.

Use public guideline data and synthetic test cases only.

---

# 11. DATASET / BENCHMARK DESIGN

A major contribution should be a reproducible test benchmark.

Working name:

PGxHard

PGxHard should include pharmacogenomics scenarios designed to stress systems.

Potential categories:

A. Straightforward supported case
B. Rare diplotype
C. Missing genotype
D. Missing phenotype
E. Unknown gene-drug pair
F. Guideline source disagreement
G. Different recommendation strength
H. Multiple relevant guidelines
I. Unsupported dosing question
J. Irrelevant genomic information
K. Misleading context
L. Contradictory context
M. Guideline changed across versions
N. Ambiguous phenotype
O. Drug without actionable guidance
P. Same drug, different genotype
Q. Same genotype, different drug
R. Incomplete patient information
S. Conflicting retrieved documents
T. Stale knowledge scenario

Gold labels must NEVER be generated solely by an LLM.

Gold recommendations should come from:
- structured CPIC / DPWG / PharmCAT outputs
- machine-readable guideline data
- manually verified guideline text

Every benchmark case must include:

case_id
gene
drug
genotype if available
diplotype if available
phenotype
source guideline
source version
expected recommendation/action
expected evidence citation
conflict status
required-information status
temporal status

Use synthetic patients only.

No personal health information.

---

# 12. COUNTERFACTUAL BENCHMARK

Create controlled pairs where only one medically relevant variable changes.

Example:

Case A:
CYP2C19 normal metabolizer
clopidogrel

Case B:
CYP2C19 poor metabolizer
clopidogrel

All other text stays identical.

Test whether the model changes its answer exactly when guideline logic requires.

Metrics:

Counterfactual Action Consistency
Counterfactual Recommendation Accuracy
Unnecessary Change Rate
Missed Change Rate

Cluster related counterfactual cases during statistical analysis so variants of one base scenario are not treated as fully independent.

---

# 13. TEMPORAL ROBUSTNESS BENCHMARK

This is one of the highest-value experiments.

Goal:

Test what happens when guidelines change.

Create versioned knowledge snapshots where possible:

T1:
older guideline/version

T2:
newer guideline/version

Evaluate systems under controlled update conditions.

Possible experimental conditions:

A:
Base LLM, no update

B:
Fine-tuned LLM trained on older knowledge

C:
RAG with updated retrieval corpus

D:
LoRA + updated RAG

E:
Deterministic structured engine updated to T2

F:
PGxTrust with updated structured rules + retrieval

Measure:

Stale Recommendation Rate
Guideline Update Accuracy
Obsolete Advice Rate
Update Adaptation Rate
Version Citation Accuracy
Old-Knowledge Intrusion Rate

Do not fabricate historical differences.

Use only documented guideline/version changes.

---

# 14. CROSS-GUIDELINE CONFLICT ENGINE

The system must not assume CPIC, DPWG, FDA, and other sources always agree.

Create a normalized recommendation schema.

Example:

{
  "gene": "...",
  "drug": "...",
  "phenotype": "...",
  "source": "CPIC",
  "version": "...",
  "action_type": "...",
  "recommended_action": "...",
  "strength": "...",
  "dose_action": "...",
  "alternative_drug": "...",
  "evidence_level": "...",
  "citation": "..."
}

Then build a comparison engine.

Possible conflict labels:

FULL_AGREEMENT
PARTIAL_AGREEMENT
DIFFERENT_STRENGTH
DIFFERENT_DOSE
DIFFERENT_ACTION
DIFFERENT_ALTERNATIVE
ONE_SOURCE_ONLY
NO_GUIDANCE
DIRECT_CONFLICT

Do not automatically force conflicting sources into one recommendation.

When disagreement exists:
- preserve each recommendation
- explain the disagreement
- identify source/version
- abstain from claiming a unified recommendation unless a defined rule permits it

---

# 15. EVIDENCE RETRIEVAL

Build a reproducible RAG pipeline.

Start simple and strong.

Possible stack:
- sentence-transformers embeddings
- BM25
- hybrid dense + lexical retrieval
- FAISS or another lightweight vector index
- reranker if justified

Compare:

BM25
Dense retrieval
Hybrid retrieval
Hybrid + reranking

Metrics:

Recall@1
Recall@3
Recall@5
MRR
nDCG

Retrieval evaluation must be separated from generation evaluation.

If the correct guideline evidence was never retrieved, classify the failure as retrieval-related.

---

# 16. EVIDENCE VERIFIER

The verifier checks whether the generated answer is actually supported by structured recommendations and retrieved evidence.

Do NOT let the same generation call simply declare itself correct.

The verifier should combine deterministic checks and, where useful, a secondary language model.

Check:

gene match
drug match
phenotype match
recommended action match
dose action match
alternative therapy match
source/version match
citation support

Possible output:

SUPPORTED
PARTIALLY_SUPPORTED
CONTRADICTED
INSUFFICIENT_EVIDENCE
UNVERIFIABLE

Store which claim failed.

---

# 17. EXPLANATION FAITHFULNESS

Correct recommendation does not automatically mean correct explanation.

Score separately:

Recommendation correctness
Phenotype correctness
Gene interpretation correctness
Drug-action correctness
Evidence correctness
Citation correctness
Explanation consistency

Example:

Recommendation correct
but
phenotype explanation wrong

This must count as an explanation failure.

Do not hide multiple errors inside one overall score.

---

# 18. UNCERTAINTY DECOMPOSITION

Do not use only:

confidence = 0.72

Track uncertainty sources.

Potential categories:

INPUT_UNCERTAINTY
- genotype missing
- phenotype unknown
- ambiguous input

GUIDELINE_COVERAGE_UNCERTAINTY
- no actionable rule exists

RETRIEVAL_UNCERTAINTY
- evidence retrieval weak

GUIDELINE_CONFLICT_UNCERTAINTY
- sources disagree

TEMPORAL_UNCERTAINTY
- sources have incompatible versions/dates

GENERATION_UNCERTAINTY
- explanation unstable

VERIFICATION_UNCERTAINTY
- support cannot be confirmed

Final abstention reasons should be interpretable.

Example:

ABSTAIN:
no guideline found

ABSTAIN:
patient genotype incomplete

ABSTAIN:
CPIC and DPWG recommendations conflict

ABSTAIN:
retrieved evidence does not support generated recommendation

---

# 19. SELECTIVE PREDICTION / ABSTENTION

Evaluate:

coverage
accuracy among answered cases
unsafe-answer rate
unsupported-answer rate
abstention precision
risk-coverage curve

Thresholds must be selected using development data only.

Never select thresholds using the final test set.

Abstention is a research mechanism, not a validated clinical safety guarantee.

---

# 20. FAILURE ATTRIBUTION

Every failed case should be assigned a failure source.

Taxonomy:

INPUT_FAILURE
NORMALIZATION_FAILURE
PHENOTYPE_MAPPING_FAILURE
RETRIEVAL_FAILURE
GUIDELINE_MAPPING_FAILURE
CONFLICT_RESOLUTION_FAILURE
GENERATION_FAILURE
VERIFICATION_FAILURE
CITATION_FAILURE
TEMPORAL_FAILURE
UNKNOWN_FAILURE

Build an automatic first-pass attribution system.

Validate samples manually.

Final paper should report failure distribution.

Example:

30% retrieval failures
25% stale-knowledge failures
20% generation failures
...

Do not invent results.

---

# 21. PRIMARY METRICS

Recommendation quality:

Recommendation Exact Match
Action Concordance
Dose Action Accuracy
Alternative Drug Accuracy
Phenotype Accuracy

Evidence grounding:

Evidence Support Rate
Unsupported Recommendation Rate
Citation Precision
Citation Recall
Citation Correctness

Retrieval:

Recall@K
MRR
nDCG

Robustness:

Counterfactual Consistency
Missing-Input Robustness
Conflict Resolution Accuracy
Hard-Case Accuracy

Temporal:

Stale Recommendation Rate
Guideline Update Accuracy
Obsolete Recommendation Rate
Version Attribution Accuracy

Reliability:

Coverage
Risk
Abstention Rate
Unsafe Answer Rate

Failure analysis:

Failure type distribution

Do not use BLEU/ROUGE as the primary clinical correctness metric.

If used at all, treat them as secondary text-similarity measures.

---

# 22. STATISTICAL ANALYSIS

Use 95% confidence intervals.

Use paired evaluation whenever the same cases are evaluated across systems.

Use bootstrap resampling.

For benchmark cases derived from the same gene-drug pair or same counterfactual base case, consider cluster bootstrap by base scenario or gene-drug pair.

For paired binary correctness comparisons, consider:
- McNemar test
- paired bootstrap difference in accuracy

Report:
effect size
confidence interval
not only p-values

Correct for multiple comparisons when necessary.

Do not overstate significance in small datasets.

---

# 23. LLM MODELS

The project should be designed so results do not depend on one proprietary provider.

Preferred reproducible models:

- Llama 3.1 8B if licensing / compute permits
- Qwen family model around 7B/8B
- smaller open model for development/testing

For LoRA:
- use PEFT
- use QLoRA / 4-bit if needed
- train in Colab
- save adapters/checkpoints to Drive

Do not train large language models from scratch.

Do not spend weeks hyperparameter-searching.

Exact prior-paper model reproduction should be attempted only after the pipeline works.

---

# 24. COMPUTE STRATEGY

LOCAL DEBIAN:

Use for:
- coding
- parsing
- guideline ingestion
- retrieval
- benchmark generation
- unit tests
- deterministic rule engine
- statistical analysis
- lightweight model inference

COLAB GPU:

Use for:
- 7B/8B model inference where needed
- LoRA / QLoRA
- embedding generation if large
- evaluation runs

GOOGLE DRIVE:

Use for:
- model weights
- adapters
- cached corpora
- large experiment outputs

GITHUB:

Use for:
- code
- configs
- small benchmark metadata
- synthetic benchmark cases if licenses allow
- aggregate metrics
- documentation
- figures
- paper source

Never commit:
- credentials
- restricted data
- huge model weights
- API tokens

---

# 25. REPOSITORY STRUCTURE

Create:

pgxtrust/
|
|-- README.md
|-- CLAUDE.md
|-- LICENSE
|-- CITATION.cff
|-- pyproject.toml
|-- requirements.txt
|-- .gitignore
|
|-- configs/
|   |-- retrieval/
|   |-- models/
|   |-- experiments/
|
|-- docs/
|   |-- research_protocol.md
|   |-- novelty_audit.md
|   |-- literature_matrix.md
|   |-- data_sources.md
|   |-- experiment_registry.md
|   |-- failure_taxonomy.md
|   |-- benchmark_design.md
|   |-- temporal_protocol.md
|
|-- data/
|   |-- README.md
|
|-- src/
|   |-- pgxtrust/
|       |-- ingestion/
|       |-- normalization/
|       |-- phenotyping/
|       |-- rules/
|       |-- retrieval/
|       |-- conflicts/
|       |-- generation/
|       |-- verification/
|       |-- uncertainty/
|       |-- evaluation/
|       |-- statistics/
|       |-- provenance/
|       |-- utils/
|
|-- scripts/
|   |-- ingest_cpic.py
|   |-- ingest_clinpgx.py
|   |-- build_index.py
|   |-- build_benchmark.py
|   |-- run_baseline.py
|   |-- run_rag.py
|   |-- run_pgxtrust.py
|   |-- evaluate.py
|
|-- benchmarks/
|   |-- pgxhard/
|   |-- counterfactual/
|   |-- temporal/
|
|-- tests/
|   |-- test_normalization.py
|   |-- test_patient_scenarios.py
|   |-- test_rule_engine.py
|   |-- test_conflict_engine.py
|   |-- test_verification.py
|   |-- test_temporal.py
|
|-- notebooks/
|   |-- exploration only
|
|-- results/
|-- figures/
|-- paper/
|-- demo/

Core logic belongs in src/.

Notebooks are not the primary implementation.

---

# 26. SCIENTIFIC WORKFLOW

Use this experiment sequence.

P00 — NOVELTY AUDIT

Before major coding:
- identify closest related systems
- pharmacogenomics RAG
- PharmCAT
- CPIC CDS implementations
- neuro-symbolic medical RAG
- conflict-aware guideline reasoning
- temporal clinical RAG
- evidence-verifying RAG
- selective prediction in medical LLMs

Create:

docs/literature_matrix.md
docs/novelty_audit.md

For every relevant paper record:

title
year
authors
problem
dataset
knowledge source
model
retrieval method
rule engine?
multi-guideline?
temporal evaluation?
conflict handling?
verification?
abstention?
metrics
limitations
relation to PGxTrust

Do not claim novelty until P00 is complete.

P01 — SOURCE INGESTION

Implement versioned official data ingestion.

Capture:
- source
- source version
- retrieval date
- checksum/hash
- license
- original URL
- schema version

P02 — NORMALIZATION

Implement:
- gene normalization
- drug normalization
- allele normalization
- diplotype representation
- phenotype normalization

Add unit tests.

P03 — STRUCTURED RULE ENGINE

Implement deterministic recommendation retrieval.

First use CPIC.

Then integrate PharmCAT where appropriate.

Add DPWG if feasible.

Every recommendation object needs source/version/provenance.

P04 — ORIGINAL-PAPER BASELINES

Reproduce as reasonably as possible:
- base model
- RAG
- LoRA if feasible
- LoRA + RAG if feasible

Record deviations from the original paper.

P05 — RETRIEVAL BENCHMARK

Evaluate:
- BM25
- dense
- hybrid
- reranker if justified

Freeze retrieval configuration.

P06 — PGXHARD

Construct challenge benchmark from authoritative guideline rules.

No LLM-generated gold truth.

P07 — PGXTRUST V1

Structured recommendation
+
RAG evidence
+
LLM explanation

P08 — VERIFIER

Implement structured evidence/answer verification.

P09 — CROSS-GUIDELINE REASONING

Integrate disagreement engine.

P10 — COUNTERFACTUAL TESTING

Build paired scenarios.

P11 — TEMPORAL ROBUSTNESS

Build version-drift benchmark where documented historical changes exist.

P12 — UNCERTAINTY + ABSTENTION

Implement decomposed uncertainty and selective prediction.

P13 — FAILURE ATTRIBUTION

Classify system failures.

P14 — ABLATIONS

Compare:

PGxTrust without verifier
PGxTrust without rule engine
PGxTrust without conflict layer
PGxTrust without abstention
RAG only
rule engine only

Do not perform unnecessary architecture searches.

P15 — FINAL STATISTICS

Confidence intervals
paired comparisons
failure distributions
risk-coverage analysis

P16 — PAPER

Write complete manuscript.

---

# 27. EXPERIMENT REGISTRY

Every run must be recorded.

Create:

docs/experiment_registry.md

Each run must contain:

Experiment ID
Run ID
Date
Git commit SHA
Data/source version
Benchmark version
Model
Prompt version
Retrieval config
Rule-engine version
Guideline versions
Random seed
Temperature
Top-k
Verifier configuration
Metrics
Runtime
Compute
Artifact path
Failure notes
Interpretation
Next decision

Never delete failed runs.

---

# 28. VERSION EVERYTHING

Record:

CPIC version
ClinPGx version
PharmCAT version
DPWG source/version
FDA source date
embedding model
LLM model/version
prompt version
benchmark version
retrieval index hash
code commit SHA

Temporal reliability is impossible to study without version discipline.

---

# 29. PROMPT VERSIONING

Prompts are experimental artifacts.

Store them in:

configs/prompts/

Do not silently edit prompts.

Version them:

generator_v001.txt
verifier_v001.txt

Record prompt version in every run.

---

# 30. REPRODUCIBILITY

Every experiment should ideally be reproducible with:

python script.py --config configs/experiments/P07.yaml

Avoid hidden notebook state.

Set seeds.

Save outputs as JSON/JSONL/CSV.

Log:
- git commit
- config
- timestamp
- environment
- model
- source versions

---

# 31. CODE QUALITY

Python 3.11 or 3.12 unless library compatibility requires otherwise.

Use:
- pathlib
- dataclasses or Pydantic where helpful
- type hints
- docstrings
- pytest
- Ruff
- logging
- YAML configs

Prefer understandable code.

The user is learning.

Avoid unnecessary enterprise architecture.

---

# 32. TESTING REQUIREMENTS

Tests are mandatory for:

genotype normalization
drug normalization
phenotype mapping
rule selection
cross-guideline comparison
version handling
verification logic
benchmark loading
counterfactual pair identity
temporal source selection

Add regression tests whenever a bug is fixed.

---

# 33. SAFETY / MEDICAL RULES

This project must be labeled:

RESEARCH ONLY

Do not present outputs as prescriptions.

Do not provide real-person treatment recommendations.

Use synthetic patient cases.

Do not imply regulatory approval.

Do not imply clinical validation.

Do not claim that abstention guarantees safety.

Do not let an LLM-generated answer become gold truth.

---

# 34. PROVENANCE

Every final answer in the research system should be traceable.

Store:

input
normalized representation
phenotype
structured rule result
guideline source
guideline version
retrieved evidence IDs
generated explanation
verifier output
uncertainty
abstention decision

This is a core scientific contribution.

---

# 35. DEMO

Build a research demo only after the system works.

Possible Streamlit interface:

Input:
- gene
- drug
- diplotype/genotype
- optional phenotype

Output:

Normalized input
Phenotype
CPIC recommendation
DPWG recommendation
Conflict status
Evidence passages
Generated explanation
Verifier status
Uncertainty
Abstention status
Provenance chain

Display prominently:

FOR RESEARCH USE ONLY — NOT CLINICAL ADVICE

---

# 36. PAPER STRUCTURE

Prepare a paper in:

paper/

Suggested sections:

Abstract

1. Introduction
2. Related Work
3. Pharmacogenomic Knowledge Sources
4. PGxTrust Architecture
5. PGxHard Benchmark
6. Experimental Design
7. Results
8. Counterfactual Robustness
9. Temporal Robustness
10. Failure Attribution
11. Ablation Study
12. Discussion
13. Limitations
14. Ethics and Clinical Safety
15. Conclusion

Appendices:
- prompts
- benchmark construction
- guideline versions
- extra metrics
- failure examples

---

# 37. FINAL FIGURES

Aim for:

Figure 1:
PGxTrust architecture

Figure 2:
Baseline vs PGxTrust recommendation correctness

Figure 3:
Retrieval performance

Figure 4:
Evidence support / hallucination rate

Figure 5:
Cross-guideline conflict results

Figure 6:
Counterfactual consistency

Figure 7:
Temporal guideline update performance

Figure 8:
Risk-coverage curve

Figure 9:
Failure attribution distribution

Figure 10:
Example provenance chain

Never fabricate numbers.

---

# 38. FINAL TABLES

Table 1:
Knowledge sources

Table 2:
Benchmark composition

Table 3:
Baseline systems

Table 4:
Recommendation correctness

Table 5:
Grounding / citation results

Table 6:
Counterfactual robustness

Table 7:
Temporal robustness

Table 8:
Ablation study

Table 9:
Failure categories

Table 10:
Limitations / unresolved cases

---

# 39. DEFINITION OF A STRONG RESULT

Do not define success as:

“PGxTrust has the highest accuracy.”

A scientifically useful result could also be:

RAG performs well on easy cases but fails under guideline conflicts.

Or:

Rule engines outperform LLMs on recommendations but LLMs improve explanations.

Or:

Updated RAG still leaks stale model knowledge.

Or:

LLMs fail counterfactual consistency despite high QA accuracy.

Or:

PGxTrust abstention significantly reduces unsupported recommendations.

Negative findings are valid research findings.

---

# 40. WHAT NOT TO DO

Do NOT:

- train huge models from scratch
- spend weeks tuning embeddings
- build UI before evaluation
- use private patient data
- scrape websites illegally
- treat LLM output as ground truth
- report only accuracy
- hide failures
- change benchmarks after seeing results
- tune on final test set
- invent guideline recommendations
- make unsupported novelty claims
- use dozens of models without reason
- over-engineer infrastructure

---

# 41. PROJECT PRIORITY

If time becomes limited:

MUST HAVE:

P00 novelty audit
P01 official source ingestion
P02 normalization
P03 deterministic rule engine
P04 RAG baseline
P06 PGxHard
P07 PGxTrust core
P08 verifier
P10 counterfactual benchmark
P13 failure attribution
P15 statistics
paper draft

HIGH PRIORITY:

multi-guideline comparison
temporal robustness
abstention

OPTIONAL:

LoRA reproduction if compute becomes expensive
large model comparisons
complex UI
many rerankers
extensive hyperparameter sweeps

Scientific rigor is more important than number of features.

---

# 42. WORKING BEHAVIOR

Move quickly.

Do not ask:

“Should I create the file?”
“Would you like me to run tests?”
“Should I proceed?”

If the next step is obvious and safe:
do it.

Ask the user only when:

- credentials are needed
- an API key is required
- a license/terms decision requires user action
- a destructive operation is needed
- a major scientific endpoint choice is ambiguous
- access to a required resource is unavailable
- paid compute is required

Otherwise:

inspect
implement
test
document
commit
continue

---

# 43. ERROR HANDLING

When something fails:

1. read the complete error
2. identify root cause
3. make smallest correct fix
4. add regression test if appropriate
5. rerun tests
6. document important changes

Do not randomly reinstall everything.

---

# 44. GIT WORKFLOW

At start of session:

git status
git pull

At end of meaningful phase:

pytest
ruff check .
git diff
update docs
update experiment registry
commit
push

Use clear commits:

“Add CPIC versioned ingestion pipeline”

“Implement normalized PGx recommendation schema”

“Add counterfactual benchmark generator”

“Add cross-guideline conflict engine”

“Implement evidence verifier”

“Add temporal robustness evaluation”

Avoid giant vague commits.

---

# 45. LEARNING MODE

The user must understand the project.

When first using a concept, briefly explain:

RAG
LoRA
genotype
diplotype
phenotype
CPIC
DPWG
PharmCAT
BM25
embeddings
reranking
counterfactual consistency
calibration
abstention
provenance
bootstrap confidence interval
McNemar test
temporal drift

At major milestones, ask the user 3–5 short questions to confirm understanding.

Do not interrupt every coding step with quizzes.

---

# 46. FINAL USER PREPARATION

Before the project is considered complete, the user must be able to explain:

What problem the prior paper solved

What limitation PGxTrust addresses

Why a rule engine can be safer/more reproducible than pure LLM reasoning

Why RAG alone does not eliminate hallucination

What PharmCAT is

Why multiple guidelines may disagree

What temporal knowledge drift means

What counterfactual consistency means

How the verifier works

What abstention means

How failures are attributed

What the key results mean

What the project cannot claim

Why the project matters to biomedical AI

---

# 47. PROFESSOR-FACING DELIVERABLES

Produce:

1. polished GitHub repository
2. technical README
3. architecture diagram
4. benchmark description
5. complete results
6. reproducibility instructions
7. manuscript draft
8. two-page research brief
9. 8–10 slide presentation
10. 2–3 minute demo script
11. one-page project summary
12. future research proposal
13. professional email to Dr. Abedalrhman Alkhateeb

The email should not say:

“I beat your paper.”

It should say approximately:

“I reproduced and extended your recent pharmacogenomics decision-support work by investigating whether structured guideline execution, evidence verification, cross-guideline conflict handling, temporal robustness, and failure attribution can improve reliability beyond conventional RAG.”

---

# 48. FUTURE RESEARCH DIRECTION

If PGxTrust succeeds, future extensions can include:

EHR integration
SMART-on-FHIR
patient-specific medication context
additional genes
additional drug classes
multi-guideline international evaluation
clinician evaluation
prospective usability study
causal treatment reasoning
structured pharmacogenomics knowledge graphs

Do not implement these before the core paper is complete.

---

# 49. PHASE GATES

Do not skip gates.

GATE 1:
repository + environment

GATE 2:
novelty audit

GATE 3:
official knowledge-source ingestion

GATE 4:
normalization + deterministic rules

GATE 5:
baseline RAG

GATE 6:
PGxHard benchmark

GATE 7:
PGxTrust core

GATE 8:
verifier

GATE 9:
counterfactual testing

GATE 10:
cross-guideline conflict analysis

GATE 11:
temporal robustness

GATE 12:
uncertainty / abstention

GATE 13:
failure attribution

GATE 14:
ablation study

GATE 15:
statistics

GATE 16:
reproducibility audit

GATE 17:
paper

GATE 18:
demo + professor package

---

# 50. DEFINITION OF DONE

PGxTrust is NOT finished when:

“the chatbot works.”

It is finished only when:

- novelty audit is documented
- guideline sources are versioned
- deterministic rule system works
- benchmark is reproducible
- RAG baseline exists
- PGxTrust exists
- verifier exists
- counterfactual evaluation exists
- temporal evaluation exists where data permit
- conflict analysis exists
- uncertainty/abstention is evaluated
- failure attribution exists
- statistical confidence intervals are reported
- repository is reproducible
- limitations are explicit
- results are not cherry-picked
- paper draft is complete
- final presentation exists
- user understands the research
- professor-facing package is ready

---

# 51. FIRST ACTION NOW

Do NOT immediately start coding a chatbot.

First:

1. Create/inspect the repository.
2. Read this CLAUDE.md.
3. Create:
   docs/research_protocol.md
   docs/literature_matrix.md
   docs/novelty_audit.md
   docs/data_sources.md
   docs/experiment_registry.md
4. Perform P00 novelty audit.
5. Identify the exact prior Alkhateeb pharmacogenomics paper and document:
   - task
   - models
   - data sources
   - retrieval method
   - fine-tuning method
   - evaluation metrics
   - reported limitations
6. Study PharmCAT.
7. Study CPIC structured resources.
8. Search specifically for:
   - PGx RAG systems
   - neuro-symbolic PGx systems
   - guideline conflict resolution
   - temporal clinical RAG
   - evidence-verifying RAG
   - abstention in medical LLM systems
9. Produce a novelty matrix.
10. Recommend the smallest defensible core contribution before substantial implementation.

Do not assume our current idea is novel.

Verify it first.

Once P00 confirms a defensible contribution, freeze the primary research question and proceed to P01.

BEGIN.
