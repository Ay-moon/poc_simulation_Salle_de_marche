# Contributing to CommandoQuant

> **[Lire ce document en français](CONTRIBUTING.md)**

Thank you for your interest in contributing.

## Ways to contribute

- **Bug reports** — open an issue describing the problem and steps to reproduce
- **Feature suggestions** — open an issue with the `enhancement` label
- **Pull requests** — code improvements, new VaR methods, additional test cases

## Development setup

```bash
git clone https://github.com/YOUR_USERNAME/CommandoQuant.git
cd CommandoQuant
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
pytest tests/ -v              # all 30 tests must pass
```

## Pull request process

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Ensure all tests pass: `pytest tests/ -v`
5. Open a pull request with a clear description

## Code style

- Python: follow PEP 8, keep docstrings in the existing style
- Tests: add at least one test per new function
- Comments: explain *why*, not just *what* — especially for financial formulas

## Roadmap ideas (V2)

- Heston stochastic volatility model
- Multi-asset correlation matrix for portfolio VaR
- GitHub Actions CI (lint + tests on push)
- Jupyter notebook walkthrough
- FRTB SA sensitivity-based approach
