"""Run with: python -m unittest discover -s tests -v"""
import unittest
from portfolio_engine import Settings, simulate, sensitivity

class PortfolioEngineTests(unittest.TestCase):
    def test_no_return_only_deposits(self):
        s = Settings(capital=1000, allocation_mt=0, allocation_tactical=0,
                     mt_annual_return=0, tactical_monthly_target=0,
                     months=24, monthly_deposit=100)
        rows, m, warnings = simulate(s)
        self.assertEqual(len(rows), 25)
        self.assertAlmostEqual(m["final_brut"], 3400)
        self.assertAlmostEqual(m["final_net"], 3400)
        self.assertAlmostEqual(m["tax_paid"], 0)

    def test_tax_applies_at_twelfth_month_only(self):
        s = Settings(capital=1000, allocation_mt=0, allocation_tactical=100,
                     mt_annual_return=0, tactical_monthly_target=1, tax_rate=30,
                     months=13, monthly_deposit=0)
        rows, m, _ = simulate(s)
        self.assertEqual(rows[11]["impot_paye"], 0)
        self.assertGreater(rows[12]["impot_paye"], 0)
        self.assertEqual(rows[13]["impot_paye"], 0)
        self.assertLess(rows[12]["patrimoine_net"], rows[12]["patrimoine_brut"])
        self.assertGreater(rows[13]["patrimoine_brut"], rows[13]["patrimoine_net"])

    def test_zero_tax_identical_paths(self):
        s = Settings(tax_rate=0, months=36)
        rows, m, _ = simulate(s)
        self.assertAlmostEqual(m["final_brut"], m["final_net"])
        self.assertEqual(m["tax_paid"], 0)

    def test_win_rate_equilibrium(self):
        _, m, _ = simulate(Settings())
        self.assertAlmostEqual(m["break_even_win_rate"], 100 / 3)
        self.assertEqual(m["required_wins"], 8)

    def test_impossible_target(self):
        _, m, warnings = simulate(Settings(tactical_monthly_target=999))
        self.assertFalse(m["feasible"])
        self.assertTrue(warnings)

    def test_invalid_allocation(self):
        with self.assertRaises(ValueError):
            simulate(Settings(allocation_mt=90, allocation_tactical=40))

    def test_sensitivity(self):
        rows = sensitivity(Settings())
        self.assertTrue(any(row["win_rate"] == 50 for row in rows))

if __name__ == "__main__":
    unittest.main()
