# PortfolioLab — Streamlit

La migration conserve l'ancien `index.html` pour référence et ajoute une application Python.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate  # Windows : .venv\\Scripts\\activate
pip install -r requirements.txt
streamlit run app.py
```

Le navigateur affiche un tableau de bord Streamlit avec paramètres dans la sidebar, graphique Plotly, métriques et scénarios.

## Tests

```bash
python -m unittest discover -s tests -v
```

Les tests du moteur ne nécessitent pas Streamlit.

## Calcul

Les versements arrivent au début de chaque mois et le portefeuille est rééquilibré mensuellement. Le rendement moyen terme annuel est converti en taux mensuel équivalent, tandis que le rendement tactique mensuel s'applique à la poche tactique.

Une version brute et une version après flat tax progressent en parallèle. Le taux fiscal est configurable (31,4 % par défaut). Chaque année simulée complète (mois 12, 24, etc.), le modèle prélève la taxe sur les gains tactiques nets positifs de la trajectoire après impôt. Aucun impôt n'est prélevé pour une année incomplète, les moins-values ne sont pas reportées fiscalement, et les gains MT ne sont pas taxés.

**Attention :** la taxation des gains réellement imposables et l'échéancier de paiement réels peuvent différer. Les rendements constants sont des hypothèses de simulation, pas des prévisions.
