# CommandoQuant

**Moteur de risque sur dérivés actions multi-stack à déploiement rapide** — conçu comme une alternative légère à Murex / Bloomberg MARS pour les salles de marché qui ont besoin de capacités de pricing quantitatif et de VaR rapidement.

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-30%20passed-brightgreen?logo=pytest)](tests/test_var_engine.py)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-informational)](https://YOUR_USERNAME.github.io/CommandoQuant/)
[![Stack](https://img.shields.io/badge/stack-Python%20%7C%20VBA%20%7C%20C%23%20%7C%20SQL%20Server-blueviolet)]()

> **[Read this document in English](README.en.md)**

---

## Qu'est-ce que CommandoQuant ?

CommandoQuant est un proof-of-concept de **système de trading quantitatif** pour les **dérivés actions**. Il couvre le cycle de vie complet depuis la saisie des trades jusqu'au reporting des risques :

- **Pricing d'options** — Black-Scholes (européennes), arbres binomiaux (américaines), Monte Carlo (path-dependent)
- **Grecques** — Delta, Gamma, Vega, Theta, Rho
- **Value-at-Risk** — 3 méthodes : Paramétrique, Monte Carlo (10 000 scénarios), Historique (chocs de crises réelles)
- **Stress testing** — COVID-19, Lehman Brothers, Flash Crash, Brexit, guerre Ukraine, crise SVB
- **Interface Excel** — blotter VBA, deal ticket, tableau de bord Grecques, rapports PDF/CSV

Le projet démontre une **maîtrise multi-stack de niveau production** sur une architecture 4 couches : VBA (UI) → C# (moteur de pricing) → Python (analytique) → SQL Server (données).

---

## Démarrage rapide (sans SQL Server)

```bash
git clone https://github.com/YOUR_USERNAME/CommandoQuant.git
cd CommandoQuant
python -m venv .venv && .venv\Scripts\activate   # Windows
pip install openpyxl                              # installation minimale
python demo.py
```

Cela génère `var_results_demo.xlsx` — un rapport VaR stylisé à partir des positions exemples incluses.

**Installation complète** (toutes les fonctionnalités) :
```bash
pip install -r requirements.txt
```

**Lancer les tests :**
```bash
pytest tests/ -v
# 30 passed in 0.2s
```

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  Couche UI          Excel VBA — Blotter, Deal Ticket, Rapports│
├──────────────────────────────────────────────────────────────┤
│  Couche Domaine     C# / VB.NET — Black-Scholes, Binomial,   │
│                     Grecques, COM Interop                     │
├──────────────────────────────────────────────────────────────┤
│  Couche Analytique  Python — Moteur VaR (3 méthodes),        │
│                     Monte Carlo, Stress Testing, xlwings      │
├──────────────────────────────────────────────────────────────┤
│  Couche Données     SQL Server — 11 tables, ADO.NET, pyodbc  │
└──────────────────────────────────────────────────────────────┘
```

| Couche | Technologie | Bibliothèques clés |
|--------|------------|-------------------|
| UI | Excel VBA | ADODB, Scripting.Dictionary |
| Moteur de pricing | C# + VB.NET | .NET 4.8, SqlClient, COM Interop |
| Analytique | Python 3.9+ | pyodbc, openpyxl, numpy, scipy |
| Données | SQL Server | Authentification Windows (aucun mot de passe en clair) |
| Interop | xlwings | Pont VBA ↔ Python |

---

## Méthodes de calcul VaR

### 1. Paramétrique (méthode Delta)
```
VaR = z(95%) × √Σ(Δᵢ × Nᵢ × σ_spot)²
```
Formule analytique rapide. Suppose une distribution normale. Ignore la convexité.

### 2. Monte Carlo (Delta + Gamma)
```
dPᵢ = Δ × dSᵢ + ½ × Γ × dSᵢ²    avec  dSᵢ = S × σ_journalière × εᵢ,  εᵢ ~ N(0,1)
```
10 000 scénarios via Box-Muller. Capture la non-linéarité (convexité Gamma).

### 3. Historique (chocs de crises réelles)

| Scénario | Choc |
|----------|------|
| COVID-19 (mars 2020) | -12,0% |
| Lehman Brothers (sept. 2008) | -9,5% |
| Flash Crash (mai 2010) | -7,2% |
| Crise dettes souveraines EU (2011) | -6,8% |
| Brexit (juin 2016) | -5,5% |
| Russie-Ukraine (fév. 2022) | -4,8% |
| Crise SVB (mars 2023) | -4,2% |

---

## Structure du dépôt

```
CommandoQuant/
├── demo.py                    # Démo VaR autonome — sans SQL Server
├── var_engine.py              # Moteur de production — connecté à SQL Server
├── CommandoQuant.xlsm         # Interface Excel VBA (blotter + tableau de bord)
├── var_results.xlsx           # Exemple de rapport VaR généré
├── requirements.txt
├── data/
│   └── sample_positions.csv   # 10 positions d'options CAC 40 exemples
├── tests/
│   └── test_var_engine.py     # 30 tests unitaires (pytest)
└── docs/                      # Site de documentation (GitHub Pages)
    ├── index.html             # Vue d'ensemble du projet
    ├── theory.html            # Black-Scholes, Grecques, VaR — dérivations complètes
    ├── business.html          # Produits : vanilla, américaines, barrières, asiatiques...
    ├── architecture.html      # Architecture 4 couches + catalogue de classes
    ├── datamodel.html         # Schéma SQL — 11 tables
    ├── implementation.html    # Patterns de code par langage
    ├── features.html          # 5 spécifications de fonctionnalités
    ├── usecase.html           # Workflows trader et risk manager
    ├── runbook.html           # Guide d'installation et de déploiement
    └── vba-oop.html           # Principes OOP en VBA
```

---

## Documentation

Le dossier `docs/` est un **site de documentation complet en 10 pages** couvrant la théorie, l'architecture, le modèle de données et le déploiement. Activez-le comme GitHub Pages pour obtenir un site en ligne.

| Page | Contenu |
|------|---------|
| [Théorie](docs/theory.html) | Dérivation Black-Scholes, formules des Grecques, méthodologie VaR |
| [Business](docs/business.html) | 6 types de dérivés, modèles de pricing, surface de volatilité |
| [Architecture](docs/architecture.html) | Architecture 4 couches, diagrammes de classes, flux de séquence |
| [Modèle de données](docs/datamodel.html) | Schéma SQL 11 tables avec contraintes et exemples |
| [Implémentation](docs/implementation.html) | Patterns de code VBA, C#, Python |
| [Fonctionnalités](docs/features.html) | 5 spécifications de fonctionnalités avec règles métier |
| [Cas d'usage](docs/usecase.html) | Workflows trader et risk manager de bout en bout |
| [Runbook](docs/runbook.html) | Guide de déploiement étape par étape |

---

## Lancer la démo

```bash
# Par défaut : charge data/sample_positions.csv, génère var_results_demo.xlsx
python demo.py

# Fichiers d'entrée/sortie personnalisés
python demo.py --input data/mes_positions.csv --output rapports/var_report.xlsx

# Plus de scénarios Monte Carlo
python demo.py --simulations 50000

# Graine aléatoire fixe pour la reproductibilité
python demo.py --seed 123
```

**Sortie exemple :**
```
============================================================
  CommandoQuant — Moteur VaR  (Mode Demo / Autonome)
============================================================
[OK] 10 positions chargees depuis data/sample_positions.csv

Positions chargees (10) :
  TTE.PA   CALL  K=  60.00  S=  62.50  Delta=+0.6312
  TTE.PA   PUT   K=  55.00  S=  62.50  Delta=-0.2845
  ...

--- Calcul VaR ---
  [VaR Parametrique 95%]      12 847,32 EUR
  [VaR Monte Carlo  95%]      13 215,67 EUR  (10 000 simulations)
  [VaR Historique   95%]      18 934,11 EUR  (25 scenarios)

============================================================
  RESUME DES RESULTATS
============================================================
  VaR Parametrique 95% :    12 847,32 EUR
  VaR Monte Carlo  95% :    13 215,67 EUR
  VaR Historique   95% :    18 934,11 EUR
============================================================
```

---

## Mode SQL Server (Production)

Le moteur de production complet (`var_engine.py`) se connecte à une instance SQL Server et lit les Grecques en temps réel depuis `tbl_Greeks`.

**Prérequis :** SQL Server 2019+, ODBC Driver 17, Python pyodbc, Authentification Windows.

Voir [docs/runbook.html](docs/runbook.html) pour le guide de configuration complet en 8 étapes.

---

## Périmètre du produit

| En scope (V1) | Hors scope (V2+) |
|---------------|-----------------|
| Options vanilla européennes & américaines | Exotiques Himalaya, Rainbow |
| Pricing Black-Scholes & Binomial | Volatilité stochastique Heston |
| Grecques : Δ Γ ν θ ρ | CVA / DVA / XVA |
| VaR : paramétrique, MC, historique | Flux Bloomberg/Reuters temps réel |
| Stress testing (7 scénarios de crise) | Reporting FRTB IMA complet |
| Blotter Excel + rapports | Automatisation clearing CCP |

---

## Contribuer

Voir [CONTRIBUTING.md](CONTRIBUTING.md) pour les directives.

---

## Licence

[MIT](LICENSE) — libre d'utilisation, de fork et d'adaptation.

---

> **CommandoQuant** — *Déployez des capacités de risque quantitatif rapidement, là où les systèmes industriels sont trop lents ou indisponibles.*
