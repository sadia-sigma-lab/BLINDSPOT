# Attack Taxonomy

Six orthogonal axes classify every attack:

| Axis | Values |
|------|--------|
| Source | user, environment, tool, memory, agent, event, background_actor |
| Target | intent, plan, tool_selection, tool_arguments, authorization, observation, memory, knowledge, state_belief, recovery |
| Mechanism | direct_instruction, indirect_injection, social_engineering, decomposition, authority_spoofing, approval_laundering, output_spoofing, observation_poisoning, state_corruption, retrieval_poisoning, privilege_escalation, delayed_activation, race_manipulation, provenance_stripping, cross_agent_propagation |
| Temporal | one_shot, gradual, staged, delayed, persistent, cross_session, adaptive, opportunistic |
| Harm | confidentiality, integrity, availability, privacy, financial, compliance, privilege_escalation, resource_exhaustion, reputational, loss_of_control |
| Knowledge Tier | static, public_responses, tool_calls, partial_state, defense_aware, internal_reasoning |

View: `blindspot attacks taxonomy`
