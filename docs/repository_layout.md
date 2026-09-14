# Repository Layout

```
blindspot/
├── src/blindspot/              # Core benchmark library
│   ├── agents/                 # Target-agent adapters (multi-provider)
│   ├── attacks/                # Attack family framework (registry, taxonomy)
│   ├── attacks_builtin/        # 22 built-in attack family implementations
│   ├── cleaning/               # Trajectory adjudication pipeline
│   ├── core/                   # Environment, tools, policies, actors, state
│   ├── domains/                # 7 domain plugins
│   │   ├── minimal_workspace/  # Controlled + Collaborative Workspace
│   │   ├── finance/
│   │   ├── software_ops/
│   │   ├── customer_service/
│   │   ├── ecommerce/
│   │   ├── governance/
│   │   └── cross_domain/
│   ├── dual_agent/             # UserAgent + TargetAgent simulation loop
│   ├── judge/                  # LLM-based semantic adjudication
│   └── scenarios/              # Registry and 65 scenario definitions
├── data/
│   ├── datasets/               # Curated train/val/test splits (JSONL)
│   ├── trajectories/           # 250 sample full trajectories (50 per outcome)
│   └── scenarios/              # scenarios.json — all 65 scenario definitions
├── figures/                    # Benchmark figures
├── docs/                       # Architecture and authoring guides
├── prompts/                    # Prompt templates (judge, user-agent, attacker)
│   ├── target_agent/           # Target agent system prompts
│   ├── user_agent/             # Benign and adversarial shared prompts
│   ├── attacker_simulator/     # Per-family attack turn templates (22 families)
│   ├── judges/                 # Semantic judge prompts
│   ├── approver_simulator/     # Approver response prompts
│   └── monitor_simulator/      # Safety monitor prompts
├── schemas/                    # JSON schemas
│   ├── scenarios/              # FullScenarioSpec, metadata, outcomes, actors
│   ├── attacks/                # AttackMetadata, AttackConfig, taxonomy axes
│   ├── shared/                 # Trajectory, judge verdict, tool spec, policy
│   └── domains/                # Domain-specific entity schemas
├── configs/                    # Configuration files
├── scripts/                    # User-facing scripts
│   ├── generate_trajectories.py
│   ├── run_minimal_example.py
│   └── validate_repo.py
├── examples/                   # Minimal domain walkthrough
└── tests/unit/                 # Unit test suite
```

## Key directories

| Path | Contents |
|------|----------|
| `src/blindspot/domains/` | One subdirectory per domain: tools, schemas, fixtures, policies, scenario definitions |
| `src/blindspot/attacks_builtin/` | 22 `.py` files, one per attack family (see paper Table 16) |
| `prompts/attacker_simulator/` | 22 `.txt` templates matching the 22 attack families |
| `data/datasets/` | `train.jsonl` (2,122), `validation.jsonl` (451), `test.jsonl` (451) |
| `data/scenarios/scenarios.json` | All 65 scenario definitions exported as JSON |
