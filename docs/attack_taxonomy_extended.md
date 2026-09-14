# Extended Attack Taxonomy (19 families, Skill 14)

## Paper sources and new families

| Attack | Family | Source | Mechanism | Knowledge Tier |
|--------|--------|--------|-----------|----------------|
| benign-control | control | Skill 04 | none | static |
| task-injection | task_injection | Skill 04 | indirect_injection | tool_calls |
| tool-chaining | tool_chaining | Skill 04 | decomposition | tool_calls |
| objective-drift | objective_drift | Skill 04 | observation_poisoning | public_responses |
| memory-poisoning-stub | memory_poisoning | Skill 04 | retrieval_poisoning | tool_calls |
| delayed-trigger-stub | delayed_trigger | Skill 04 | delayed_activation | static |
| cross-tenant-exfiltration | cross_tenant | Skill 13 | privilege_escalation | partial_state |
| prompt-reinjection | prompt_reinjection | Skill 13 | output_spoofing | tool_calls |
| stale-approval-reuse | stale_approval | Skill 13 | approval_laundering | tool_calls |
| mass-enumeration | mass_enumeration | Skill 13 | retrieval_poisoning | public_responses |
| silent-rollback-bypass | silent_rollback | Skill 13 | state_corruption | partial_state |
| **intent-hijacking** | intent_hijacking | **AgentLAB** | social_engineering | public_responses |
| **objective-drifting-v2** | objective_drifting | **AgentLAB** | observation_poisoning | tool_calls |
| **memory-poisoning** | memory_poisoning | **AgentLAB** | retrieval_poisoning | tool_calls |
| **compliance-drift** | compliance_drift | **Boiling the Frog** | social_engineering | public_responses |
| **role-drift** | role_drift | **Boiling the Frog** | authority_spoofing | public_responses |
| **false-context-injection** | false_context | **Boiling the Frog** | indirect_injection | partial_state |
| **parametric-trap** | parametric_trap | **ToolFailBench** | output_spoofing | tool_calls |
| **malicious-skill-injection-v2** | malicious_skill | **WildClawBench** | indirect_injection | partial_state |

## Key insights per new family

- **Intent Hijacking**: Succeeds in ~4.6 turns. More turns > more optimization per turn.
- **Compliance Drift**: Slow-boil is most universally dangerous across all model families.
- **Memory Poisoning**: Only attack family that persists across sessions. Two-phase required.
- **Parametric Trap**: Tests faithfulness — does agent USE tool output or revert to memory?
- **Malicious Skill Injection**: Supply-chain vector; entirely absent from other benchmarks.
