# Architectural Changes Log

## Experiment 0

- architectural_change: `step0_baseline`
- parameter_delta: 0 params; baseline replay
- lines_touched: demonstration-only in-memory model variant
- gradient_flow_smoke: passed by successful training loop
- contribution_ratio_at_init: not applicable for synthetic demo
- observed_effect_post_tier1: BASELINE_COMPLETE at primary_metric=0.8551

## Experiment 1

- architectural_change: `temperature_scaling_head_after_linear4`
- parameter_delta: +1 temperature parameter after linear4
- lines_touched: demonstration-only in-memory model variant
- gradient_flow_smoke: passed by successful training loop
- contribution_ratio_at_init: not applicable for synthetic demo
- observed_effect_post_tier1: TIER1_DISCARD_NO_SIGNAL at primary_metric=0.8597

## Experiment 2

- architectural_change: `l1_reg=2e-2_on_mofnet1`
- parameter_delta: 0 params; l1_reg changed from 5e-3 to 2e-2
- lines_touched: demonstration-only in-memory model variant
- gradient_flow_smoke: passed by successful training loop
- contribution_ratio_at_init: not applicable for synthetic demo
- observed_effect_post_tier1: TIER1_DISCARD_NO_SIGNAL at primary_metric=0.8474

## Experiment 3

- architectural_change: `l1_reg=5e-2_on_mofnet1`
- parameter_delta: 0 params; l1_reg changed from 5e-3 to 5e-2
- lines_touched: demonstration-only in-memory model variant
- gradient_flow_smoke: passed by successful training loop
- contribution_ratio_at_init: not applicable for synthetic demo
- observed_effect_post_tier1: TIER1_DISCARD_METRIC_REGRESSION at primary_metric=0.8471

## Experiment 4

- architectural_change: `per_feature_gate_on_modality_a_and_t1`
- parameter_delta: +2 gate vectors for modality_a and t1
- lines_touched: demonstration-only in-memory model variant
- gradient_flow_smoke: passed by successful training loop
- contribution_ratio_at_init: not applicable for synthetic demo
- observed_effect_post_tier1: TIER1_KEEP_CONTROLLED_SIGNAL at primary_metric=0.8638

## Experiment 5

- architectural_change: `replay_of_exp_4`
- parameter_delta: 0 params; replay of exp 4 across seeds
- lines_touched: demonstration-only in-memory model variant
- gradient_flow_smoke: passed by successful training loop
- contribution_ratio_at_init: not applicable for synthetic demo
- observed_effect_post_tier1: TIER2_FAIL_HIGH_VARIANCE at primary_metric=0.8611
