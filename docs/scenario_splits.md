# Scenario Splits

## Split values

`train`, `validation`, `test`, `challenge`, `hidden_test`, `community`

## Leakage checks

`SplitLeakageChecker` detects:
- Safe twins in train paired with unsafe in hidden_test
- Same template used in both hidden_test and train
- Attack families in both train and hidden_test

## CLI

```bash
blindspot scenario split-report --config split_config.yaml
```
