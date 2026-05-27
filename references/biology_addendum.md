# Biology-Specific Addendum

Use this optional reference when the model predicts biological outcomes such as cell state, perturbation response, protein function, drug response, disease progression, variant effect, or multi-omics profiles. Non-bio projects should skip these biology-specific requirements and instead define their own protected domain metrics in the core protocol.

Biology has structure that broad distributional metrics alone do not capture: direction-of-effect, pathways, cell types, developmental stages, regulatory networks, cross-species/protocol consistency, and domain governance.

---

## Safety And Compliance Boundary

This skill supports computational model evaluation and research planning only.

Do not:

- provide wet-lab protocols, operational experimental steps, or optimization instructions for biological manipulation;
- make clinical, diagnostic, treatment, or patient-specific recommendations;
- claim biological validity from Tier 1 or Tier 2 results;
- process protected health information unless the user confirms authorization and de-identification;
- recommend deployment-facing biological claims without human domain review;
- present model output as experimentally validated biology without appropriate evidence;
- claim a benchmark improvement based on the same split that drove selection. "Improvement over baseline on the selection split" is exploratory and must be reported as such. A benchmark claim requires one of: (a) a fresh held-out split not seen during search, (b) nested cross-validation with selection isolated per outer fold, or (c) an external cohort under documented preprocessing. Prefer wording such as "candidate `EXP_X` improved over the Step 0 baseline on the validation split; external confirmation pending" over any phrasing that implies a public-benchmark beat.

For sensitive biological domains, require:

- data provenance;
- consent/IRB or equivalent governance status when relevant;
- license and usage restrictions;
- organism, tissue, assay, and protocol metadata;
- expert review before external biological claims.

---

## Minimum Biological Evaluation Stack

Use layered evaluation. Do not rely on a single scalar metric.

1. **Distributional metrics:** Wasserstein, MMD, E-distance, KL, MSE, MAE, correlation, energy distance.
2. **Direction metrics:** delta cosine, signed differential-expression agreement, direction-aware Common-DEGs, sign concordance.
3. **Marker/program metrics:** per-marker capture, multi-marker joint capture, program coherence, pathway/module enrichment consistency.
4. **Population metrics:** cluster coverage, cell-type/fate composition, diversity/spread, rare-state preservation.
5. **Manifold metrics:** PCA/UMAP centroid shift, neighborhood overlap, local density preservation.
6. **Mode-collapse metrics:** weighted MSE, weighted delta R², technical duplicate ceiling, source-as-target/null baselines, variance-shrunk prediction baselines.
7. **Generalization metrics:** held-out perturbations, held-out donors, held-out cell types, held-out protocols, held-out species, or held-out time points when available.

For direction-aware metrics, a gene that overlaps but moves in the wrong direction is a biological failure, not a partial success.

---

## Biological No-Regression Gates

A candidate must not degrade protected biological behavior even if a headline metric improves.

Common no-regression gates:

- direction-of-effect agreement does not drop beyond threshold;
- known marker/program capture remains within gate;
- population diversity and cluster coverage do not collapse;
- held-out perturbations or conditions do not regress;
- pathway/program outputs remain biologically coherent;
- null baselines do not match or beat the candidate;
- cross-species/protocol interpretation is downgraded when ortholog or assay coverage is insufficient.

---

## Avoid Gene-Name-Specific Losses

Losses, masks, and architectural priors should be parameterized by evidence categories, pathways, annotations, or conserved programs, not by hand-picked gene names, unless the experiment explicitly tests a diagnostic hypothesis.

Prefer:

- Reactome/MSigDB/GO pathway membership;
- transcription-factor category membership;
- surface-marker category membership;
- organism-aware ortholog mapping;
- evidence categories;
- assay-specific quality annotations.

Avoid:

- “force gene X up at time Y” as a promoted mechanism;
- dataset-specific marker hacks;
- unlogged symbol-resolution assumptions;
- marker-only wins that damage distributional or validator metrics.

If named markers are used for evaluation or diagnostic losses, run a marker-resolution check:

```text
requested markers
resolved genes in dataset A
resolved genes in dataset B
missing genes
exact-symbol vs suffix vs ortholog mapping
coverage percentage
interpretation downgrade if coverage is low
```

---

## External Baseline Reproduction Provenance

Comparing your model against an external baseline imports the external's hygiene into your project. The MoFNet POC reimplemented moBRCA-net from scratch (237 lines of from-scratch TF1-style code with "Compatibility fixes: Python3 range/division and corrected miRNA slicing" in the file) and logged the canonical upstream GitHub URL as `source_repo`. A reader skimming `external_public_baselines.tsv` would assume upstream code was run unchanged. That is a claim-integrity failure independent of any leakage.

Every row of `external_public_baselines.tsv` (or the equivalent comparator TSV) must declare:

- **`reproduction_mode`** — one of:
  - `upstream_unchanged` — cloned the published repo at a recorded commit, ran the published entrypoint with the published config, no edits to model code or data preprocessing;
  - `upstream_patched` — ran the published repo with a documented patch (Python 3 compat, dependency pin, dtype fix, etc.). The patch diff must be saved at `external_baselines/<name>/upstream.patch` and referenced from the TSV row;
  - `full_reimplementation` — the model code in this repo is the agent's or author's own implementation, not upstream code. The file path of the reimplementation must be cited.
- **`claim_strength`** — the wording that may appear in `final_report.md` / blog posts / plots:
  - `upstream_unchanged` → "reproduced upstream `<commit>`";
  - `upstream_patched` → "reproduced upstream `<commit>` with documented patch";
  - `full_reimplementation` → **"compat-equivalent reimplementation, not a reproduction of the published numbers"**. The published number must still be cited separately, with the gap (if any) reported openly.
- **`upstream_commit_or_release`** — the exact commit hash, tag, or release the comparison is against. If `full_reimplementation`, this is still required and refers to the version the reimplementation was modeled on.
- **`metric_selection_policy`** — as recorded under `core_protocol.md §3.5 "External Baseline Metric-Selection Policy"`.

A `full_reimplementation` row may not be claimed as a benchmark-reproduction win. Any plot, PDF, or blog generator that displays an `external_public_baselines.tsv` comparator must read these columns and label `full_reimplementation` rows visibly as such (legend, footnote, or table column).

### External Baseline Split Parity

Reproduction provenance is necessary but not sufficient. The MoFNet POC also showed that running an external baseline on its own native preprocessed split (MOGONET BRCA, 875 samples, 1000 features per omic) and comparing against the project's model on the project's split (MLOmics GS-BRCA, 671 samples, Top-selected features) produces a comparison that looks like a head-to-head but is not one. Different samples, different features, different train/test partitions. The comparison is in the same upstream cohort ballpark but is not a benchmark claim.

Every row of `external_public_baselines.tsv` (or equivalent) must therefore also declare:

- **`eval_split`** — the role from `split_manifest.json` the score was computed on, exactly one of `train`, `validation`, `locked_test`, `legacy_test`, `external_cohort_<name>`, or `native_external_split_<name>`. The first four mean "this external was trained on this project's `train` indices and evaluated on the named held-out role"; `external_cohort_*` means a separate cohort the project pre-registered; `native_external_split_*` means the external was run on its own native preprocessed split (not the project's split) and the comparison is therefore loose.
- **`split_parity`** — one of:
  - `same_train_same_eval` — the external was trained on the project's `train` indices and evaluated on the project's held-out indices (the apples-to-apples case);
  - `same_train_different_eval` — same train, different held-out (rare; document why);
  - `different_train_different_eval` — the external used its own native split; comparison is ballpark only.
- **`split_manifest_sha256`** — the SHA-256 of the project's `split_manifest.json` at the time the external was trained. Pins which version of the split parity holds. Empty for `different_train_different_eval` rows.

`split_parity = different_train_different_eval` rows may not be cited as evidence in any "the model beats X" claim. They are documentary context. Plots and reports rendering them must label them as "different-split reference comparison" or equivalent.

The autoresearch-bio recommended workflow for externals is: write a script that loads your `split_manifest.json`, trains each external on the `train` indices using the external's documented default hyperparameters, evaluates the trained model separately on each held-out role (`validation`, `locked_test`, `legacy_test`), and writes one row per `(external, eval_split)` pair with `split_parity = same_train_same_eval`. The mofnet_poc repository at `scripts/run_externals_same_mlomics_split.py` is the worked example this rule was extracted from.

---

## External Biological Resources

Track all external resources in `external_resources.md` with URLs, versions, organism IDs, confidence thresholds, and license notes.

Common resources:

- Reactome;
- KEGG;
- MSigDB;
- Gene Ontology;
- STRING;
- BioGRID;
- OmniPath;
- DoRothEA/TRRUST;
- Ensembl/UCSC;
- ChEMBL/DrugBank for drug tasks;
- scGPT/Geneformer/ESM2 embeddings as priors, with caveats.

For cross-species use, log ortholog coverage and abort or downgrade interpretation if coverage is too low for the conclusion.

---

## Domain Expert Report After A True Tier 3 Win

After a true Tier 3 win, produce a domain-expert report, not just ML metrics.

Include:

- model of record and promoted candidate;
- marker trajectories;
- pathway/program capture;
- population/fate distribution;
- prediction vs reference plots;
- uncertainty/confidence indicators;
- cross-condition generalization status;
- known failure modes;
- provenance and license caveats;
- practical QC recommendations;
- clear statement that the report supports computational review, not clinical or deployment claims.

Do not produce deployment-facing biological claims from Tier 1 or Tier 2 near-misses.
