# PGxTrust research protocol

- **Version:** 0.5 (2026-10-09; see §9 for changes since the P00 freeze)
- **Change rule:** any change after freezing gets a new version number, a dated entry in §9, and a
  reason. Changes made *after* seeing model outputs must be labelled "post hoc".

---

## 1. Background (one paragraph)

Arafin, Moniruzzaman & Alkhateeb (2026, doi:10.3390/app16189148) showed that LoRA + hybrid RAG
improves 8B LLM answers to PGx questions built from CPIC and ClinPGx. Their knowledge sources were
not version-pinned. Their evaluation used record-level splits with entity overlap and rule-normalised
three-class labels. They list abstention under conflicting evidence and DPWG/FDA coverage as future
work. Separately, Corpas et al. (2026, under revision) already show that executing structured CPIC
rules is more reliable than generating from retrieved prose. CPIC itself publishes 88 tagged,
machine-readable releases (2020–2026), so *what the guideline said on a given date* is exactly
recoverable. Details and evidence: `docs/novelty_audit.md`.

## 2. Frozen core question

> **When a CPIC recommendation has changed between guideline releases, do LLM-based PGx question
> answering systems give the recommendation that was valid on the date asked, and does attaching
> release-version metadata to retrieved evidence reduce version errors?**

The "correct" answer is always the recommendation in the CPIC release valid on the stated date, as
recovered from that release's SQL dump. **No LLM judge and no clinician labelling are needed for the
primary outcome.**

### Relation to the master programme (`README.md`)

The master primary question (§4: a full neuro-symbolic system with executable guidelines, conflict
modelling, verification and version tracking) is kept as the **long-term programme**. P00 found that
several of its parts are already published (`docs/novelty_audit.md` §5), so the **core paper** is
the slice that P00 judged defensible:

| Master item | Status in the core paper |
|---|---|
| H4 version-aware executable knowledge vs parametric/RAG/fine-tuning | **Primary** (this protocol's H1–H2) |
| §13 temporal robustness metrics (stale-recommendation rate, update accuracy, old-knowledge intrusion, version attribution) | Primary and secondary metrics (§4.4) |
| H1/H2 executable engine vs RAG | Reference arm only; framed as a replication of Corpas 2026, not a contribution |
| H5 counterfactual consistency | Instrument (§4.3: date counterfactuals) |
| H6 failure attribution | Descriptive secondary (§4.4) |
| H7 abstention | Secondary metric (abstention / "no recommendation" rate) |
| H3 cross-guideline conflict | Pivot (§6 G1b) and the planned follow-up paper |
| B1/B3 LoRA baselines | Optional arm A4 (§4.1), compute permitting |

### Explicitly out of scope for the core paper

- New retrieval architectures. The LoRA reproduction is optional (arm A4) and is not needed to test
  the question; the target paper already shows LoRA alone is insufficient.
- Genotype calling from VCF / PharmCAT end-to-end. Corpas 2026 covers the calling step.
- DPWG/FDA conflicts. This is the pre-registered **pivot** (§6, G1b) and a possible follow-up paper.
- Claim-level verification of free-text explanations (secondary at most).
- Any UI, EHR/FHIR integration or patient-facing output.

### Alternatives considered and rejected (P00)

| Candidate | Why not the core question |
|---|---|
| Full "trustworthy PGx assistant" (all 8 capabilities) | Integration with no single falsifiable claim; each part has prior art (audit §5) |
| Executable rules vs RAG | Already shown in PGx by Corpas 2026 |
| Failure attribution as headline | Already shown in PGx by Corpas 2026; RAGChecker/RAG-X in general |
| CPIC–DPWG conflict handling | Defensible, but ground truth needs ClinPGx licence/access and a softer "correct handling" definition → kept as pivot |
| Counterfactual genotype tests | Too thin alone; kept as an evaluation instrument (§4.3) |

## 3. Hypotheses (directional; finalise thresholds only after G1, before any model run)

Terms used below:
- **Changed item:** a (guideline, drug, gene-result lookup key) whose CPIC recommendation differs
  between two releases (definition in §5.2).
- **Matched unchanged item:** same guideline, same release pair, recommendation identical in both
  releases.
- **As-of date:** the date stated in the question. The gold answer comes from the latest release
  published on or before that date.

**H1 — drift penalty.** For LLM arms that do not see version metadata, accuracy on changed items is
lower than on matched unchanged items.
- Effect: `acc(unchanged) − acc(changed)`, with a 95% cluster-bootstrap CI (clusters = gene–drug
  pairs).
- H1 is supported if the lower CI bound is above 0 for the RAG-mixed arm.

**H2 — version-tagged evidence.** In the RAG-mixed arm, adding release tag and date metadata to each
retrieved chunk (plus the as-of date in the instruction) reduces the drift penalty compared with the
same retrieval without metadata.
- Effect: the paired difference in changed-item accuracy, with a cluster-bootstrap CI.

**Reference (not a hypothesis):** a version-pinned deterministic lookup against the as-of release
dump. It should reach ~1.0 by construction. It is used to validate items: any item it gets wrong is
an item-construction bug, which is fixed and logged *before* any model runs.

## 4. Design

### 4.1 Arms (each run on the identical frozen item set)

| Arm | Knowledge given to the model | Purpose |
|---|---|---|
| A0 `free` | none | Parametric staleness |
| A1 `rag_current` | retrieval over the latest pinned release only | Upper bound for RAG |
| A2 `rag_mixed` | retrieval over chunks from all releases in the study window, **no version metadata** | Realistic stale/mixed index |
| A3 `rag_mixed_tagged` | same index as A2, each chunk prefixed with `[CPIC vX.Y, released YYYY-MM-DD]` | H2 intervention |
| R `pinned_lookup` | deterministic SQL lookup in the as-of release | Executable reference / item validation (master B4) |
| A4 `lora_old` *(optional)* | Llama-3.1-8B + LoRA trained on records from an **older** release only, with and without A1 retrieval | Master §13 conditions B/D; direct continuity with the target paper's LoRA + RAG |

Models:
- At least one open 8B model from the target paper, **Llama-3.1-8B-Instruct**, for direct continuity
  with Alkhateeb 2026.
- One or two hosted frontier models.

The exact model IDs, decoding settings (temperature 0) and model training cut-off dates are frozen
at P02 and recorded in the registry.

### 4.2 Item format

- **Primary: forced choice, for deterministic scoring.** Question: "As of ⟨date⟩, according to
  CPIC, what is the recommendation for ⟨drug⟩ in a patient with ⟨gene result⟩?" Options:
  - the as-of recommendation;
  - the other version's recommendation;
  - up to two distractors from the same guideline;
  - "CPIC has no recommendation for this case".

  Option order is shuffled with a fixed seed.
- **Secondary:** free-text answer, mapped to an action class by a frozen rule set. Reported only
  as secondary.

### 4.3 Counterfactual date instrument

Every changed item is asked **twice**: once with an as-of date before the change and once after. The
gold answer flips between the two. A system that gives the same answer to both is *date-insensitive*.
Date-sensitivity rate is a secondary metric. Unchanged items asked at both dates must *not* flip
(a control).

### 4.4 Metrics

- **Primary:** version-correct accuracy on changed vs matched unchanged items (H1), and the A2 vs A3
  difference (H2).
- **Secondary:**
  - **stale-answer rate:** the system picks the other version's text;
  - **date-sensitivity rate:** see §4.3;
  - **"no recommendation" / abstention rate;**
  - **RAG failure attribution** for A2/A3, as a frequency of three categories: (i) as-of chunk not
    retrieved; (ii) both versions retrieved and stale chosen; (iii) as-of chunk retrieved and still
    wrong. This is a descriptive breakdown and not claimed as novel.
- **Statistics:** cluster bootstrap over gene–drug pairs, 10,000 resamples, seed 20261009. Paired
  comparisons use the same resampled clusters across arms.

### 4.5 Leakage and fairness rules

- The item set and its SHA-256 are frozen before any model call.
- No prompt or retrieval tuning on the evaluation items. Any tuning uses a separate dev set of
  guidelines that is disjoint by guideline.
- The retrieval index for each arm is built only from the releases defined for that arm.
- Model training cut-offs are recorded. Items are stratified by change date before vs after each
  model's cut-off (secondary analysis).

## 5. Data

### 5.1 Sources (all pinned)

- CPIC whole-DB SQL dumps: `files.cpicpgx.org/data/database/cpic_db_dump-v<X>.sql.gz`. Record tag,
  URL, download date and SHA-256 in `data/README.md`. Dumps are never committed.
- The CPIC API is used only for spot checks, never as ground truth: it serves "latest", and its
  `recommendation.version` field is not a change history.

### 5.2 Change definition (frozen before G1 is run)

For consecutive releases r_i → r_j, the key is (guideline name, drug RxNorm ID, normalised lookup key
JSON). Normalised means whitespace collapsed, case-folded and punctuation-stripped.

| Type | Definition | Pool |
|---|---|---|
| **M (modified)** | Key present in both releases; normalised `drugrecommendation` differs **or** `classification` differs | Primary |
| **A (added)** | Key absent in r_i, present in r_j, for a gene–drug pair that existed in r_i | Primary |
| **N (new pair)** | Gene–drug pair absent in r_i | Secondary only |
| **R (removed)** | Key present in r_i, absent in r_j | Primary if the pair still exists in r_j |

**Substantive filter:** an M item is substantive if `classification` changed, **or** the action
class changed under a frozen keyword map:
- avoid / not recommended
- use alternative
- reduce dose / decrease
- increase dose
- standard / label-recommended dosing
- consider / no action
- no recommendation

Text-only edits that keep the action class and the classification are logged but excluded from the
primary pool.

## 6. Research gates

### G0 — literature completion (must pass before writing any paper text)

- Read the full texts of the PGx rows marked `unknown` on `temporal_updates` or
  `multi_guideline_conflict` in `literature/literature_matrix.csv`: zack2025pgxj, zack2026npj,
  borishetty2025pgxrag, jeon2026hrag, murugan2024, rector2025sherpa, keat2025pgxqa. Update the rows.
- Run a bioRxiv/medRxiv search for: CPIC version, guideline update, outdated, knowledge cutoff,
  pharmacogenomic LLM.
- **Pass:** no PGx work evaluates LLM answers against real CPIC version changes.
- **Fail:** if one does, record it and re-scope (for example, to H2 only, or pivot to G1b).

### G1 — CPIC release-diff feasibility (the next research gate)

Download the release dumps covering the study window, parse the `recommendation` table, and apply
§5.2 to every consecutive pair. Thresholds are frozen here, before looking at the data.

**Pass if all three hold:**
1. ≥ **40** substantive primary items (M + A + R);
2. spread over ≥ **4** distinct guidelines;
3. ≥ **15** of them introduced in releases dated **≥ 2025-01-01**, so they are plausibly after the
   training cut-off of the 8B open models.

Plus a sanity check: on a random sample of 20 substantive items (seed 20261009), the
version-pinned lookup R reproduces both versions exactly, and the researcher's manual read agrees
the action changed in ≥ 16/20.

**G1 outputs:**
- `results/p01/cpic_changes.csv` (item table, no copyrighted prose beyond CPIC's own fields);
- `results/p01/g1_summary.json`;
- a registry entry.

**If G1 fails → G1b pivot to candidate B (CPIC–DPWG disagreement).**
- Confirm ClinPGx access and licence.
- Pass if ≥ 40 gene–drug–phenotype triples have a discordant action class between CPIC and DPWG
  across ≥ 4 genes.
- If G1b also fails, stop and re-plan with the researcher.

### G2 — power check (after G1, before any model run)

With the actual item count, simulate the bootstrap CI width for H1 assuming a 15-point drift
penalty. If the expected half-width is > 10 points, expand the item pool before running models:
add phenotype variants per key, or widen the release window.

## 7. Planned phases

Phase numbers follow the master instructions (`README.md` §26). Only the phases the core paper needs
are scheduled now. The others (P05 retrieval benchmark, P08 verifier, P09 cross-guideline, P12
abstention engine, P14 ablations) are deferred until the core result exists.

| Master phase | Core-paper content | Gate |
|---|---|---|
| P00 | Novelty audit, protocol, matrix | done |
| P01 | Versioned CPIC ingestion (release dumps, hashes, licence) + G0 literature completion + G1 release diff | **G0, G1 (next)** |
| P02–P03 | Normalisation of lookup keys / drugs; version-pinned deterministic lookup R | G2 |
| P04 | Baselines A0–A2 (and optional A4 LoRA) on the frozen items | — |
| P11 | Temporal benchmark: frozen item set (changed + matched unchanged, date counterfactuals); A3 intervention | — |
| P13 / P15 | Failure attribution (descriptive), cluster-bootstrap statistics for H1, H2 | — |
| P16 | Paper draft | — |

## 8. Reporting commitments

- Report every arm and model run, including failures and API errors. API errors are recorded
  separately from model abstentions; see Corpas 2026's rate-limit lesson.
- No "first" or "novel" in the paper unless G0 passes. Even then, write "to our knowledge, based on
  searches of ⟨databases⟩ up to ⟨date⟩".
- The paper's claim is limited to "matches the CPIC release valid on the stated date". No clinical
  safety claims.

## 9. Change log

| Version | Date | Change | Reason |
|---|---|---|---|
| 0.1 | 2026-10-09 | Initial freeze at end of P00 | — |
| 0.5 | 2026-10-09 | **Researcher decision after G2 failed (post hoc, before any model run):** the primary item pool = "changed" items (substantive M/A/R, re-keyings removed; 228 items, 16 gene–drug clusters) **plus** "appeared" items (N: gene–drug pairs that had no CPIC recommendation before a release; gold as-of answer before = "CPIC has no recommendation"; 629 items). Total 857 items, 80 pair clusters, 12 guidelines (`primary_pool`, `drift_type`). H1 is estimated on the pooled set, and **also reported separately by drift type**. The "changed"-only estimate is underpowered (simulated half-width ≈ 0.13) and is labelled exploratory. Guideline-level clustering (12 clusters, half-width 0.12 at penalty_sd = 1.0) is reported as a sensitivity analysis. | G2 strict model: 16 clusters were too few (half-width 0.129). Adding N items gives 80 clusters (half-width 0.068, P = 0.99). |
| 0.4 | 2026-10-09 | **Post hoc** (after seeing G1 counts): (a) R/A pairs in the same release and gene–drug pair with identical recommendation text are treated as re-keyings and dropped (`drop_rekeyings`); (b) the "≥15 recent items" criterion uses the net diff from the last pre-2025 release to the latest, so transient edits that are later reverted count once. Both changes are conservative: they can only reduce item counts. | Raw counts were inflated by 771 re-keying pairs (mostly v1.21.0) and by a v1.54.0 → v1.55.0 round trip. |
| 0.3 | 2026-10-09 | §5.2 clarified before any diff was run: (a) item key also includes the normalised `population` field, because CPIC can give separate recommendations per population for one lookup key; (b) the keyword map treats "recommended/desired/normal starting dose" as `standard` and "n/a"/"none" as `no_recommendation`; (c) sentence full stops are ignored when comparing text, decimals are kept. Recommendation text stays out of git until the CPIC licence is verified. | Found while smoke-testing the parser on the v1.54.0 dump (recommendation texts only; no change counts or model outputs seen). |
| 0.2 | 2026-10-09 | Added the master-programme mapping (§2) and optional arm A4 (LoRA on an older release); renamed phases to the master numbering (§7) | The master instructions (README.md in the GitHub repo) were found after v0.1 was drafted. No data or model outputs had been seen. |
