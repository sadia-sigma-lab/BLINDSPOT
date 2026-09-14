"""Unit tests for split metadata and leakage checks."""

import pytest
from blindspot.scenarios.splits import ScenarioSplitMetadata, SplitLeakageChecker
from blindspot.scenarios.exceptions import ScenarioLeakageError


def test_valid_split_metadata():
    s = ScenarioSplitMetadata(split="train", template_family="workspace:share-file-base@1.0.0")
    assert s.split == "train"


def test_twin_leakage_detected():
    checker = SplitLeakageChecker()
    with pytest.raises(ScenarioLeakageError):
        checker.check_twin_leakage("hidden_test", "train")


def test_valid_twin_pairing():
    checker = SplitLeakageChecker()
    # safe twin in challenge, unsafe in test — allowed
    checker.check_twin_leakage("test", "challenge")  # should not raise


def test_template_leakage_warning():
    checker = SplitLeakageChecker()
    scenarios = [
        ("s1", "tmpl_A", "hidden_test"),
        ("s2", "tmpl_A", "train"),
    ]
    warnings = checker.check_template_leakage(scenarios)
    assert len(warnings) > 0


def test_no_leakage_when_templates_disjoint():
    checker = SplitLeakageChecker()
    scenarios = [
        ("s1", "tmpl_A", "hidden_test"),
        ("s2", "tmpl_B", "train"),
    ]
    warnings = checker.check_template_leakage(scenarios)
    assert len(warnings) == 0
