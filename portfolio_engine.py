"""Pure portfolio simulation calculations; rates entered as percentages."""
from dataclasses import dataclass
import math

@dataclass(frozen=True)
class Settings:
    capital: float = 100000
    allocation_mt: float = 65
    allocation_tactical: float = 25
    months: int = 60
    monthly_deposit: float = 500
    mt_annual_return: float = 8
    risk_per_trade: float = 0.4
    simultaneous_risk: float = 2
    risk_reward: float = 2
    trades_per_month: int = 20
    tactical_monthly_target: float = 3
    tax_rate: float = 31.4

    @property
    def cash_allocation(self) -> float:
        return 100 - self.allocation_mt - self.allocation_tactical

def validate(s: Settings) -> None:
    values = [v for v in vars(s).values()]
    if not all(math.isfinite(float(x)) for x in values):
        raise ValueError("Les valeurs doivent être finies.")
    if (s.capital <= 0 or s.allocation_mt < 0 or s.allocation_tactical < 0
        or s.cash_allocation < 0 or s.months < 1 or s.months > 600
        or int(s.months) != s.months or s.monthly_deposit < 0
        or s.mt_annual_return < -100 or s.risk_per_trade <= 0
        or s.simultaneous_risk < 0 or s.risk_reward <= 0
        or s.trades_per_month < 1 or int(s.trades_per_month) != s.trades_per_month
        or s.tactical_monthly_target < 0 or not 0 <= s.tax_rate <= 100):
        raise ValueError("Vérifiez les allocations, le risque et les autres paramètres.")

def simulate(s: Settings):
    """Returns list of monthly records, metrics and warnings.

    Annual tax is charged at months 12, 24, ... on positive net tactical
    gains of the respective simulation year on the after-tax path.
    Incomplete years are not taxed, and tax losses are not carried forward.
    """
    validate(s)
    mt_rate = math.pow(1 + s.mt_annual_return / 100, 1 / 12) - 1
    tactical_rate = s.allocation_tactical / 100 * s.tactical_monthly_target / 100
    monthly_rate = s.allocation_mt / 100 * mt_rate + tactical_rate
    global_target_pct = s.allocation_tactical * s.tactical_monthly_target / 100
    wins = max(0, math.ceil((global_target_pct / s.risk_per_trade +
                             s.trades_per_month) / (s.risk_reward + 1) - 1e-10))
    feasible = (s.allocation_tactical > 0 and
                s.simultaneous_risk >= s.risk_per_trade and
                wins <= s.trades_per_month)
    warnings = []
    if not feasible:
        warnings.append("La cible tactique n'est pas réalisable avec ces contraintes de trades et de risque.")
    if s.simultaneous_risk > s.allocation_tactical:
        warnings.append("Le risque simultané excède la poche tactique.")
    if s.risk_per_trade > s.allocation_tactical:
        warnings.append("Le risque par trade excède la poche tactique.")
    if monthly_rate <= -1:
        warnings.append("La variation mensuelle du capital atteint ou dépasse une perte de 100 %.")
    wealth = after_tax = contributed = s.capital
    annual_tactical_net = total_tax = 0.0
    rows = [dict(mois=0, patrimoine_brut=wealth, patrimoine_net=after_tax,
                 capital_apporte=contributed, impot_paye=0.0)]
    for month in range(1, s.months + 1):
        contributed += s.monthly_deposit
        wealth = (wealth + s.monthly_deposit) * (1 + monthly_rate)
        starting_net = after_tax + s.monthly_deposit
        annual_tactical_net += starting_net * tactical_rate
        after_tax = starting_net * (1 + monthly_rate)
        tax = 0.0
        if month % 12 == 0:
            tax = min(max(0.0, after_tax), max(0.0, annual_tactical_net) * s.tax_rate / 100)
            after_tax -= tax
            total_tax += tax
            annual_tactical_net = 0.0
        rows.append(dict(mois=month, patrimoine_brut=wealth,
                         patrimoine_net=after_tax, capital_apporte=contributed,
                         impot_paye=tax))
    metrics = dict(
        monthly_rate=monthly_rate, mt_monthly_rate=mt_rate,
        global_tactical_target_pct=global_target_pct,
        break_even_win_rate=100 / (1 + s.risk_reward),
        required_wins=wins, required_win_rate=100 * wins / s.trades_per_month,
        feasible=feasible,
        realized_tactical_pct=(100 * s.risk_per_trade *
                              (wins * s.risk_reward - (s.trades_per_month - wins)) /
                              s.allocation_tactical if feasible else None),
        simultaneous_slots=math.floor(s.simultaneous_risk / s.risk_per_trade),
        tax_paid=total_tax, final_brut=wealth, final_net=after_tax,
        capital_apporte=contributed, net_gain=after_tax-contributed,
    )
    return rows, metrics, warnings

def sensitivity(s: Settings):
    validate(s)
    threshold = 100 / (1 + s.risk_reward)
    rates = sorted(set([0, 20, 30, 40, 50, 60, 70, 80, 100, round(threshold, 3)]))
    return [dict(win_rate=p,
                 contribution_globale=s.trades_per_month*s.risk_per_trade*
                     (p/100*(s.risk_reward+1)-1),
                 rendement_poche=(s.trades_per_month*s.risk_per_trade*
                     (p/100*(s.risk_reward+1)-1)*100/s.allocation_tactical
                     if s.allocation_tactical > 0 else None)) for p in rates]
