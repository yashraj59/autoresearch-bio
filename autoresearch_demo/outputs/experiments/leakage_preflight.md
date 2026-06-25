# Leakage Pre-Flight

- Dataset: deterministic synthetic ROS/MAP-shaped demo data (`seed=42`).
- Search split: validation split only.
- Held-out split: test split, used for reporting and plots only.
- Selection rule: Tier 1 and Tier 2 decisions use validation AUC/ECE and IG stability.
- Leakage guard: `PASS_NO_TEST_SELECTION` for every row in `results.tsv`.
