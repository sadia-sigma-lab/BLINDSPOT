# Contributing

1. Fork the repository and create a feature branch.
2. Install dev dependencies: `pip install -e ".[dev]"`.
3. Run `make lint && make typecheck && make test` before submitting.
4. Add or update tests for any new functionality.
5. Register new components via plugins — do not modify core registries directly.
