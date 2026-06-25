# Baseline Registry

## Model Of Record

- Model: MoFNet v1.1.0
- Checkpoint: published baseline
- Commit: v1.1.0
- Config: hidden2=48, hidden3=12, dropout=0.5, l1_reg=5e-3 for the synthetic demo

## Baseline Metrics

| Metric | Direction | Seed list | Mean | Std | Source |
| --- | --- | --- | --- | --- | --- |
| val_auc | higher | 66, 1, 7 | 0.8551 | 0.0071 | run_autoresearch.py output |
| val_ece | lower | 66, 1, 7 | 0.0965 | 0.0168 | run_autoresearch.py output |
| test_auc | higher | 66, 1, 7 | 0.8937 | 0.0031 | held-out reporting only |

## Per-Seed Provenance

- seed 66: val_auc=0.8563, val_ece=0.0789, test_auc=0.8976
- seed 1: val_auc=0.8459, val_ece=0.1191, test_auc=0.8900
- seed 7: val_auc=0.8632, val_ece=0.0915, test_auc=0.8934

## Provenance Notes

- Source: synthetic ROS/MAP-shaped multi-omic data, seed=42 for data generation
- Note: demonstration only, not real ROS/MAP
