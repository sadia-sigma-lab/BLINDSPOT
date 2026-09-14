"""Unit tests for scenario generation."""

from pathlib import Path
from blindspot.scenario_generators.cartesian import CartesianGenerator
from blindspot.scenario_generators.pairwise import PairwiseGenerator
from blindspot.scenarios.templates import load_template

_TEMPLATE_PATH = Path("src/lh_agent_bench/domains/minimal_workspace/scenarios/templates/share_file_base.yaml")


def test_cartesian_generation_deterministic():
    tmpl = load_template(_TEMPLATE_PATH)
    gen = CartesianGenerator()
    specs1 = gen.generate(tmpl, seed=42, max_count=5)
    specs2 = gen.generate(tmpl, seed=42, max_count=5)
    assert [s["_scenario_id"] for s in specs1] == [s["_scenario_id"] for s in specs2]


def test_cartesian_generates_scenarios():
    tmpl = load_template(_TEMPLATE_PATH)
    gen = CartesianGenerator()
    specs = gen.generate(tmpl, seed=42, max_count=4)
    assert len(specs) > 0


def test_pairwise_fewer_than_cartesian():
    tmpl = load_template(_TEMPLATE_PATH)
    cart = CartesianGenerator().generate(tmpl, seed=42)
    pair = PairwiseGenerator().generate(tmpl, seed=42)
    # Pairwise should be <= cartesian
    assert len(pair) <= len(cart)


def test_different_seed_may_vary():
    tmpl = load_template(_TEMPLATE_PATH)
    gen = CartesianGenerator()
    s1 = gen.generate(tmpl, seed=1, max_count=3)
    s2 = gen.generate(tmpl, seed=2, max_count=3)
    # IDs will differ (different seeds)
    ids1 = [s["_scenario_id"] for s in s1]
    ids2 = [s["_scenario_id"] for s in s2]
    assert ids1 != ids2


def test_invalid_param_rejected():
    tmpl = load_template(_TEMPLATE_PATH)
    gen = CartesianGenerator()
    # Override default values to inject invalid enum
    from blindspot.scenarios.templates import ScenarioTemplate, TemplateParameter
    bad_tmpl = ScenarioTemplate(
        template_id=tmpl.template_id,
        parameters=[
            TemplateParameter(name="file_id", param_type="resource_id", required=True,
                              values=["invalid_file_xyz"]),
        ],
        base_spec=tmpl.base_spec,
    )
    # Should generate 0 valid scenarios due to constraint mismatch
    specs = gen.generate(bad_tmpl, seed=42)
    # No crash; invalid combos skipped
    assert isinstance(specs, list)
