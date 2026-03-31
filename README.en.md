# CommandoQuant

**A rapid-deployment, multi-stack equity derivatives risk engine** — built as a lightweight alternative to Murex / Bloomberg MARS for trading desks that need quantitative pricing and VaR capabilities fast.

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-30%20passed-brightgreen?logo=pytest)](tests/test_var_engine.py)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-informational)](https://YOUR_USERNAME.github.io/CommandoQuant/)
[![Stack](https://img.shields.io/badge/stack-Python%20%7C%20VBA%20%7C%20C%23%20%7C%20SQL%20Server-blueviolet)]()

> **[Lire ce document en français](README.md)**

---

## What is CommandoQuant?

CommandoQuant is a proof-of-concept **quantitative trading floor system** for **equity derivatives**. It covers the full lifecycle from trade capture to risk reporting:

- **Option pricing** — Black-Scholes (European), Binomial trees (American), Monte Carlo (path-dependent)
- **Greeks** — Delta, Gamma, Vega, Theta, Rho
- **Value-at-Risk** — 3 methods: Parametric, Monte Carlo (10,000 scenarios), Historical (real crisis shocks)
- **Stress testing** — COVID-19, Lehman Brothers, Flash Crash, Brexit, Ukraine war, SVB collapse
- **Excel interface** — VBA blotter, deal ticket, Greeks dashboard, PDF/CSV reports

The project demonstrates **production-grade multi-stack proficiency** across a 4-layer architecture: VBA (UI) → C# (pricing engine) → Python (analytics) → SQL Server (data).

---

## Quick Start (no SQL Server required)

```bash
git clone https://github.com/YOUR_USERNAME/CommandoQuant.git
cd CommandoQuant
python -m venv .venv && .venv\Scripts\activate   # Windows
pip install openpyxl                              # minimal install
python demo.py
```

This generates `var_results_demo.xlsx` — a styled VaR report from the bundled sample positions.

**Full install** (all features):
```bash
pip install -r requirements.txt
```

**Run the tests:**
```bash
pytest tests/ -v
# 30 passed in 0.2s
```

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  UI Layer          Excel VBA — Blotter, Deal Ticket, Reports │
├──────────────────────────────────────────────────────────────┤
│  Domain Layer      C# / VB.NET — Black-Scholes, Binomial,   │
│                    Greeks, COM Interop                        │
├──────────────────────────────────────────────────────────────┤
│  Analytics Layer   Python — VaR Engine (3 methods),          │
│                    Monte Carlo, Stress Testing, xlwings       │
├──────────────────────────────────────────────────────────────┤
│  Data Layer        SQL Server — 11 tables, ADO.NET, pyodbc   │
└──────────────────────────────────────────────────────────────┘
```

| Layer | Technology | Key Libraries |
|-------|-----------|---------------|
| UI | Excel VBA | ADODB, Scripting.Dictionary |
| Pricing Engine | C# + VB.NET | .NET 4.8, SqlClient, COM Interop |
| Analytics | Python 3.9+ | pyodbc, openpyxl, numpy, scipy |
| Data | SQL Server | Windows Authentication (no plaintext passwords) |
| Interop | xlwings | VBA ↔ Python bridge |

---

## VaR Methods

### 1. Parametric (Delta method)
```
VaR = z(95%) × √Σ(Δᵢ × Nᵢ × σ_spot)²
```
Fast analytical formula. Assumes normal distribution. Ignores convexity.

### 2. Monte Carlo (Delta + Gamma)
```
dPᵢ = Δ × dSᵢ + ½ × Γ × dSᵢ²    where  dSᵢ = S × σ_daily × εᵢ,  εᵢ ~ N(0,1)
```
10,000 scenarios via Box-Muller. Captures non-linearity (Gamma convexity).

### 3. Historical (real crisis shocks)

| Scenario | Shock |
|----------|-------|
| COVID-19 (March 2020) | -12.0% |
| Lehman Brothers (Sept 2008) | -9.5% |
| Flash Crash (May 2010) | -7.2% |
| EU Sovereign Debt (2011) | -6.8% |
| Brexit (June 2016) | -5.5% |
| Russia-Ukraine (Feb 2022) | -4.8% |
| SVB Collapse (March 2023) | -4.2% |

---

## Repository Structure

```
CommandoQuant/
├── demo.py                    # Standalone VaR demo — no SQL Server needed
├── var_engine.py              # Production engine — connects to SQL Server
├── CommandoQuant.xlsm         # Excel VBA interface (blotter + dashboard)
├── var_results.xlsx           # Sample VaR report output
├── requirements.txt
├── data/
│   └── sample_positions.csv   # 10 sample CAC 40 option positions
├── tests/
│   └── test_var_engine.py     # 30 unit tests (pytest)
└── docs/                      # Documentation site (GitHub Pages)
    ├── index.html             # Project overview
    ├── theory.html            # Black-Scholes, Greeks, VaR — full derivation
    ├── business.html          # Products: vanilla, American, barriers, Asians...
    ├── architecture.html      # 4-layer design + class catalog
    ├── datamodel.html         # SQL schema — 11 tables
    ├── implementation.html    # Code patterns per language
    ├── features.html          # 5 end-to-end feature specs
    ├── usecase.html           # Trader & risk manager workflows
    ├── runbook.html           # Installation & deployment guide
    └── vba-oop.html           # OOP principles in VBA
```

---

## Documentation

The `docs/` folder is a complete **10-page documentation site** covering theory, architecture, data model, and deployment. Enable it as GitHub Pages to get a live site.

| Page | Content |
|------|---------|
| [Theory](docs/theory.html) | Black-Scholes derivation, Greeks formulas, VaR methodology |
| [Business](docs/business.html) | 6 derivative types, pricing models, volatility surface |
| [Architecture](docs/architecture.html) | 4-layer design, class diagrams, sequence flows |
| [Data Model](docs/datamodel.html) | 11-table SQL schema with constraints and examples |
| [Implementation](docs/implementation.html) | VBA, C#, Python code patterns |
| [Features](docs/features.html) | 5 feature specs with business rules |
| [Use Cases](docs/usecase.html) | Trader and risk manager end-to-end workflows |
| [Runbook](docs/runbook.html) | Step-by-step deployment guide |

---

## Running the Demo

```bash
# Default: loads data/sample_positions.csv, writes var_results_demo.xlsx
python demo.py

# Custom input/output
python demo.py --input data/my_positions.csv --output reports/var_report.xlsx

# More Monte Carlo scenarios
python demo.py --simulations 50000

# Fixed random seed for reproducibility
python demo.py --seed 123
```

**Sample output:**
```
============================================================
  CommandoQuant — VaR Engine  (Demo / Standalone Mode)
============================================================
[OK] 10 positions loaded from data/sample_positions.csv

Positions loaded (10):
  TTE.PA   CALL  K=  60.00  S=  62.50  Delta=+0.6312
  TTE.PA   PUT   K=  55.00  S=  62.50  Delta=-0.2845
  ...

--- VaR Calculation ---
  [Parametric VaR 95%]      12,847.32 EUR
  [Monte Carlo VaR 95%]     13,215.67 EUR  (10,000 simulations)
  [Historical VaR 95%]      18,934.11 EUR  (25 scenarios)

============================================================
  RESULTS SUMMARY
============================================================
  Parametric VaR  95% :    12,847.32 EUR
  Monte Carlo VaR 95% :    13,215.67 EUR
  Historical VaR  95% :    18,934.11 EUR
============================================================
```

---

## SQL Server Mode (Production)

The full production engine (`var_engine.py`) connects to a SQL Server instance and reads live Greeks from `tbl_Greeks`.

**Prerequisites:** SQL Server 2019+, ODBC Driver 17, Python pyodbc, Windows Authentication.

See [docs/runbook.html](docs/runbook.html) for the complete 8-step setup guide.

---

## Product Scope

| In Scope (V1) | Out of Scope (V2+) |
|---------------|-------------------|
| European & American vanilla options | Himalaya, Rainbow exotics |
| Black-Scholes & Binomial pricing | Heston stochastic volatility |
| Greeks: Δ Γ ν θ ρ | CVA / DVA / XVA |
| VaR: parametric, MC, historical | Real-time Bloomberg/Reuters feeds |
| Stress testing (7 crisis scenarios) | Full FRTB IMA reporting |
| Excel blotter + reports | CCP clearing automation |

---

## Contributing

See [CONTRIBUTING.en.md](CONTRIBUTING.en.md) for guidelines.

---

## License

[MIT](LICENSE) — free to use, fork, and adapt.

---

> **CommandoQuant** — *Deploy quantitative risk capabilities fast, where industrial systems are too slow or unavailable.*
