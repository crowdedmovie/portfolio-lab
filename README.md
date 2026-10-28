# Portfolio-Lab

**An interactive investment portfolio simulator built with Python, Streamlit, and Plotly.**

PortfolioLab helps investors explore portfolio allocations, manage trading risk, and simulate long-term wealth growth through investment returns and recurring contributions.

## Features

### Portfolio Allocation
Split your portfolio into three components:
- **Medium-Term Investments:** Assets with an expected annual return.
- **Tactical Trading:** Short-term positions with configurable risk parameters.
- **Cash:** Uninvested capital for liquidity.

### Trading & Risk Management
- Risk per trade and maximum simultaneous exposure.
- Risk/reward ratio and monthly trading frequency.
- Target monthly return on the tactical allocation.
- Automatic break-even win rate and required winning trades.
- Risk scenarios and win-rate sensitivity analysis.

### Wealth Projection
- Configurable simulation period (1–600 months).
- Initial capital and recurring monthly deposits.
- Monthly compounding and portfolio rebalancing.
- Interactive chart comparing gross portfolio value, after-tax portfolio value, and contributed capital.

### Tax Simulation
- Configurable flat-tax rate (31.4% by default).
- Simulated annual taxation of positive net tactical trading profits.
- Taxes deducted from portfolio value, affecting future compounding.

*Tax calculations are simplified and do not cover all applicable fiscal rules.*

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Financial simulation |
| Streamlit | Interactive dashboard |
| Plotly | Performance charts |
| Pandas | Data processing |
| unittest | Unit testing |

## Getting Started

**1. Clone the repository**

```bash
git clone https://github.com/crowdedmovie/portfolio-lab.git
cd portfolio-lab
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Run the application**

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

## Project Structure

```text
portfolio-lab/
├── app.py                  # Streamlit dashboard
├── portfolio_engine.py     # Simulation engine
├── index.html              # Original HTML version
├── requirements.txt        # Dependencies
├── tests/                  # Unit tests
├── STREAMLIT.md            # Additional documentation
└── README.md
```

## Running Tests

```bash
python -m unittest discover -s tests -v
```

## Roadmap

- [ ] Monte Carlo simulations
- [ ] Drawdown and risk-of-ruin analysis
- [ ] Historical backtesting
- [ ] Dynamic portfolio rebalancing
- [ ] Trading fees and transaction costs
- [ ] Advanced tax modeling

## Disclaimer

PortfolioLab is an educational simulation tool, **not financial advice**. Results are based on simplified assumptions, including constant returns, monthly rebalancing, and no transaction costs. Actual investment performance and taxation may differ.

## License

See the [LICENSE](LICENSE) file for details.

---

Developed with assistance from **OpenAI ChatGPT / Codex**.
