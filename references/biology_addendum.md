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
- present model output as experimentally validated biology without appropriate evidence.

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
