# Point of No Return

## Definition

The PONR is the earliest step after which no registered, scenario-valid intervention branch can prevent the target harm within the allowed budget.

## Current implementation

Without full branch search, the PONR is estimated conservatively as the **last precursor step before the first harm**. This is an early (conservative) estimate.

`branch_search_complete: false` is always set until full branch enumeration is implemented.

## Uncertainty

`uncertainty` reflects search completeness. With only precursor-based estimation, uncertainty is 0.4.

## Recoverability after PONR

Steps after the PONR may still allow partial recovery (e.g., revoking access after unauthorized sharing). `RecoverabilityResult.partial_recovery_possible` captures this.

## Interfaces for Skill 09

- `PointOfNoReturnResult.preventable_before` — steps usable for RL intervention policies
- `RecoverabilityResult.required_intervention_ids` — recovery actions for reward shaping
- `StepRiskLabel.time_to_harm` — survival-analysis target for risk predictor training
