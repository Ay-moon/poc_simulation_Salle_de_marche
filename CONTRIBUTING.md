# Contribuer à CommandoQuant

> **[Read this document in English](CONTRIBUTING.en.md)**

Merci de votre intérêt pour contribuer à ce projet.

## Façons de contribuer

- **Rapports de bugs** — ouvrez une issue en décrivant le problème et les étapes pour le reproduire
- **Suggestions de fonctionnalités** — ouvrez une issue avec le label `enhancement`
- **Pull requests** — améliorations du code, nouvelles méthodes VaR, cas de tests supplémentaires

## Configuration de l'environnement de développement

```bash
git clone https://github.com/YOUR_USERNAME/CommandoQuant.git
cd CommandoQuant
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
pytest tests/ -v              # les 30 tests doivent passer
```

## Processus de pull request

1. Forkez le dépôt
2. Créez une branche de fonctionnalité : `git checkout -b feature/nom-de-votre-fonctionnalite`
3. Effectuez vos modifications
4. Assurez-vous que tous les tests passent : `pytest tests/ -v`
5. Ouvrez une pull request avec une description claire

## Style de code

- Python : suivre PEP 8, conserver le style des docstrings existantes
- Tests : ajouter au moins un test par nouvelle fonction
- Commentaires : expliquer le *pourquoi*, pas seulement le *quoi* — surtout pour les formules financières

## Idées pour la feuille de route (V2)

- Modèle de volatilité stochastique Heston
- Matrice de corrélation multi-actifs pour la VaR de portefeuille
- CI GitHub Actions (lint + tests au push)
- Notebook Jupyter de présentation
- Approche basée sur les sensibilités FRTB SA
