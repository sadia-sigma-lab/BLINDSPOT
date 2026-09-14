# Adding a New Domain

1. Create `src/blindspot/domains/<domain_name>/`
2. Add `schemas.py` with domain-specific models extending `ResourceRecord` or `BaseEntity`
3. Add `state_builder.py` with a `DomainStateBundle` configuration
4. Add `validators.py` with `@register_invariant(...)` functions
5. Add `policies.py` with domain-specific `AuthorizationEngine` subclass if needed
6. Add `fixtures/manifest.yaml` and fixture files
7. Add `migrations/` for any schema evolution
8. Create a `BenchmarkPlugin` subclass and register in `configs/benchmark.example.yaml`
9. Run `blindspot fixtures validate --fixture <id>` and `make test`
