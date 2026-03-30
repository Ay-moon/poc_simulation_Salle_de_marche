# CommandoQuant POC - Trading Quantitatif

## 📌 Objectif
POC d'un système quantitatif de `market-making` / backtest, basé sur Python + VBA/Excel. Ce repository vise à valoriser une approche finance quant pour candidature, profil LinkedIn, revue de code.

## 🚀 Contenus clés
- `var_engine.py` : moteur quant (core strategy / travail d'analyse de variance ou risk engine)
- `Tools/` : scripts utilitaires
- `CommandoQuant.xlsm` : sheet Excel contenant macros, interface et dataflows
- `var_results.xlsx` : résultats du backtest / simulation
- `runbook.html`, `architecture.html`, `workflow.html`, `datamodel.html`, `business.html`, `features.html`, `implementation.html`, `theory.html`, `usecase.html`, `vba-oop.html` : documentation projet

## 📁 Structure recommandée
- `src/` : code Python et scripts
- `data/` : exemples de données (CSV) et résultats
- `docs/` : documentation exploitable (HTML/MD)
- `tests/` : tests unitaires

## 🛠️ Installation (Linux/Mac/Windows)
1. `git clone <URL>`
2. `python -m venv .venv`
3. `.venv\Scripts\activate` (Windows) | `source .venv/bin/activate` (Linux/Mac)
4. `pip install -r requirements.txt`
5. `python src/run_demo.py`

## 🧪 Exemple d'exécution
```bash
python src/var_engine.py --input data/historic_sample.csv --output data/backtest_results.csv
```

## 📘 À faire après
- Transformer fichiers HTML actuels en docs Markdown
- Fournir un jeu de données public anonymisé
- Ajouter GitHub Actions (CI) : lint + tests
- Mettre à jour `README.md` en anglais + français

## 🏷️ Tags & visibilité
- keywords: `quantitative-finance`, `risk-management`, `python`, `vba`, `financial-engineering`, `market-making`
- utiliser GitHub Pages (branch `main`/`docs`) pour page projet

## 🤝 Contributions
1. Fork
2. Branch feature
3. PR
4. Code review

---
> Ce projet a pour but d'attester de compétences techniques et financières par un cas concret (simulation, analyse, documentation).