# Baseline Registry

## Model Of Record

- Model: MoFNet v1.1.0
- Checkpoint: published baseline
- Commit: v1.1.0
- Config: hidden2=96, hidden3=16, dropout=0.5, l1_reg=5e-3

## Baseline Metrics

| Metric | Direction | Seed list | Mean | Std | Source |
| --- | --- | --- | --- | --- | --- |
| test_auc | higher | 66, 1, 7 | 0.8937 | 0.0031 | run_autoresearch.py output |
| test_ece | lower | 66, 1, 7 | 0.1243 | 0.0071 | run_autoresearch.py output |

## Provenance Notes

- Source: synthetic ROS/MAP-shaped multi-omic data, seed=42 for data generation
- Note: demonstration only, not real ROS/MAP
