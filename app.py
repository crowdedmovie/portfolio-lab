"""PortfolioLab Streamlit dashboard."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from portfolio_engine import Settings, simulate, sensitivity

st.set_page_config(page_title="PortfolioLab", page_icon="📈", layout="wide")
st.title("PortfolioLab")
st.caption("Simulation d'allocation, de risque et d'évolution du patrimoine")

with st.sidebar:
    st.header("Paramètres")
    st.subheader("Portefeuille")
    capital = st.number_input("Capital initial (€)", min_value=1.0, value=100000.0, step=1000.0)
    mt = st.number_input("Allocation moyen terme (%)", min_value=0.0, max_value=100.0, value=65.0, step=1.0)
    ct = st.number_input("Allocation tactique (%)", min_value=0.0, max_value=100.0, value=25.0, step=1.0)
    st.metric("Liquidités résiduelles (%)", f"{100-mt-ct:.1f}")
    st.divider()
    st.subheader("Projection")
    months = st.number_input("Durée (mois)", min_value=1, max_value=600, value=60, step=1)
    deposit = st.number_input("Versement au début de chaque mois (€)", min_value=0.0, value=500.0, step=100.0)
    mt_return = st.number_input("Rendement moyen terme annuel (%)", min_value=-100.0, value=8.0, step=0.5)
    st.divider()
    st.subheader("Trading tactique")
    risk = st.number_input("Risque par trade (% portefeuille total)", min_value=0.01, value=0.4, step=0.05)
    opened = st.number_input("Risque simultané maximum (% portefeuille total)", min_value=0.0, value=2.0, step=0.25)
    rr = st.number_input("Risk / Reward", min_value=0.01, value=2.0, step=0.25)
    trades = st.number_input("Nombre total de trades par mois", min_value=1, value=20, step=1)
    target = st.number_input("Objectif mensuel (% poche tactique)", min_value=0.0, value=3.0, step=0.25)
    st.divider()
    st.subheader("Fiscalité simulée")
    tax = st.number_input("Flat tax annuelle sur bénéfices tactiques (%)", min_value=0.0, max_value=100.0, value=31.4, step=0.1)
    st.caption("Hypothèse simplifiée : impôt prélevé au mois 12, 24, etc., sur les gains tactiques positifs de chaque année.")

s = Settings(capital=capital, allocation_mt=mt, allocation_tactical=ct,
             months=months, monthly_deposit=deposit, mt_annual_return=mt_return,
             risk_per_trade=risk, simultaneous_risk=opened, risk_reward=rr,
             trades_per_month=trades, tactical_monthly_target=target, tax_rate=tax)
try:
    rows, m, warnings = simulate(s)
except ValueError as exc:
    st.error(str(exc))
    st.stop()

for warning in warnings:
    st.warning(warning)

def money(value):
    return f"{value:,.0f} €".replace(",", " ")

def rate(value):
    return f"{value:+.2f} %"

st.subheader("Projection patrimoniale")
a, b, c, d = st.columns(4)
a.metric("Patrimoine brut final", money(m["final_brut"]))
b.metric("Patrimoine net après impôt", money(m["final_net"]))
c.metric("Capital apporté", money(m["capital_apporte"]))
d.metric("Flat tax cumulée", money(m["tax_paid"]))

df = pd.DataFrame(rows)
fig = go.Figure()
for col, label, color in [
    ("patrimoine_brut", "Patrimoine brut", "#4f83ff"),
    ("patrimoine_net", "Patrimoine après flat tax", "#c26ace"),
    ("capital_apporte", "Capital apporté", "#dfa33d"),
]:
    fig.add_trace(go.Scatter(x=df["mois"], y=df[col], mode="lines",
                             name=label, line=dict(color=color, width=3),
                             hovertemplate="Mois %{x}<br>%{y:,.0f} €<extra>"+label+"</extra>"))
fig.update_layout(xaxis_title="Mois", yaxis_title="Montant (€)", hovermode="x unified",
                  margin=dict(l=10, r=10, t=15, b=10), legend=dict(orientation="h"))
st.plotly_chart(fig, use_container_width=True)

st.subheader("Allocation et trading")
left, right = st.columns(2)
with left:
    st.write("**Répartition cible**")
    st.dataframe(pd.DataFrame([
        {"Poche": "Moyen terme", "Allocation (%)": mt, "Capital initial (€)": capital*mt/100},
        {"Poche": "Tactique", "Allocation (%)": ct, "Capital initial (€)": capital*ct/100},
        {"Poche": "Liquidités", "Allocation (%)": 100-mt-ct, "Capital initial (€)": capital*(100-mt-ct)/100},
    ]), hide_index=True, use_container_width=True)
    st.metric("Contribution tactique mensuelle au portefeuille", rate(m["global_tactical_target_pct"]))
    st.metric("Objectif tactique mensuel en euros (sur capital initial)", money(capital*m["global_tactical_target_pct"]/100))
with right:
    p, q = st.columns(2)
    p.metric("Win rate d'équilibre", f'{m["break_even_win_rate"]:.1f} %')
    q.metric("Win rate requis", f'{m["required_win_rate"]:.1f} %' if m["feasible"] else "Impossible")
    p.metric("Trades gagnants requis", f'{m["required_wins"]} / {trades}' if m["feasible"] else "Impossible")
    q.metric("Trades simultanés (plafond)", str(m["simultaneous_slots"]))
    st.write(f'Risque par trade : **{money(capital*risk/100)}** · Gain gagnant : **{money(capital*risk*rr/100)}**')
    st.write("Rendement tactique avec trades entiers :",
             rate(m["realized_tactical_pct"]) if m["feasible"] else "Objectif non atteignable")

with st.expander("Scénarios de risque et sensibilité au win rate"):
    st.write(f"Plafond de risque ouvert sur capital initial : {money(capital*opened/100)}")
    st.write(f"10 pertes successives (risque initial fixe) : {-10*risk:.2f} % du capital initial")
    st.write(f"Tous les trades perdants sur {months} mois (addition théorique) : {-months*trades*risk:.2f} % du capital initial")
    st.dataframe(pd.DataFrame(sensitivity(s)).rename(columns={
        "win_rate": "Win rate (%)",
        "contribution_globale": "Contribution globale (%/mois)",
        "rendement_poche": "Rendement poche tactique (%/mois)",
    }), hide_index=True, use_container_width=True)

with st.expander("Hypothèses du modèle"):
    st.markdown("""
- Versement au début de chaque mois et rééquilibrage vers les allocations cibles.
- Rendement moyen terme annuel converti en taux mensuel équivalent, et rendement tactique cible supposé atteint chaque mois.
- Deux parcours capitalisés séparément, brut et après impôt. Prélèvement après chaque période **complète** de 12 mois, sur les gains tactiques nets positifs de cette période.
- Pas de taxation des gains moyen terme dans ce modèle, ni report des moins-values fiscales entre années ; pas de taxation pour l'année incomplète.
- Pas de frais, glissement, fiscalité réelle détaillée, limites de marge ou aléas de marché. Les courbes sont des **scénarios**, pas des prévisions ou conseils d'investissement.
""")
