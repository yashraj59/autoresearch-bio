# Research Journal

<!-- node: id=0 type=experiment experiment=true -->
## Node 0: baseline

- Status: `BASELINE_COMPLETE`
- Parent experiments: `none`
- Branch type: `root`
- Primary validation metric: 0.8551
- Protected summary: val_ece=0.0965, val_prec@spec90=1.000, report_only_test_auc=0.8937
- Notes: Published MoFNet v1.1.0 baseline, 3 seeds, synthetic ROS/MAP

<!-- node: id=1 type=experiment experiment=true -->
## Node 1: calibration

- Status: `TIER1_DISCARD_NO_SIGNAL`
- Parent experiments: `0`
- Branch type: `linear`
- Primary validation metric: 0.8597
- Protected summary: val_ece=0.0882, val_prec@spec90=1.000, report_only_test_auc=0.9004
- Notes: Add learnable temperature parameter (Family 1 smallest mechanism); paired no-mechanism control is exp 0 baseline

<!-- node: id=2 type=experiment experiment=true -->
## Node 2: sparsity

- Status: `TIER1_DISCARD_NO_SIGNAL`
- Parent experiments: `0`
- Branch type: `fork`
- Primary validation metric: 0.8474
- Protected summary: val_ece=0.0856, val_prec@spec90=1.000, report_only_test_auc=0.8850
- Notes: Higher L1 sparsity (Family 2, fork from baseline); paired no-mechanism control is exp 0 baseline

<!-- node: id=3 type=experiment experiment=true -->
## Node 3: sparsity

- Status: `TIER1_DISCARD_METRIC_REGRESSION`
- Parent experiments: `0`
- Branch type: `fork`
- Primary validation metric: 0.8471
- Protected summary: val_ece=0.0916, val_prec@spec90=1.000, report_only_test_auc=0.8844
- Notes: Even higher L1 (Family 2 second fork)

<!-- node: id=4 type=experiment experiment=true -->
## Node 4: gating

- Status: `TIER1_KEEP_CONTROLLED_SIGNAL`
- Parent experiments: `0`
- Branch type: `linear`
- Primary validation metric: 0.8638
- Protected summary: val_ece=0.0862, val_prec@spec90=1.000, report_only_test_auc=0.8965
- Notes: Cross-omic gating before concat (Family 3); paired no-mechanism control is exp 0 baseline

<!-- node: id=5 type=experiment experiment=true -->
## Node 5: gating

- Status: `TIER2_FAIL_HIGH_VARIANCE`
- Parent experiments: `4`
- Branch type: `replay`
- Primary validation metric: 0.8611
- Protected summary: 3 seeds, mean val_ece=0.1196
- Notes: Tier 2 multi-seed replay of Tier 1 keep from exp 4

<!-- node: id=AUDIT01 type=audit experiment=false -->
## Audit 01: Quarter-Budget Check

- The run reached six registered nodes under a 25-experiment cap.
- No candidate reached Tier 3; no model-of-record promotion is allowed.
- The held-out test split remained reporting-only after the leakage pre-flight.
