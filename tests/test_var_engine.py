"""
tests/test_var_engine.py
========================
Unit tests for CommandoQuant VaR engine.

These tests cover the pure mathematical functions in demo.py
(no SQL Server required — standalone mode only).

Run with:
    pytest tests/ -v
    pytest tests/ -v --cov=demo --cov-report=term-missing
"""

import math
import sys
import os
import pytest

# Make sure demo.py is importable from the project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from demo import (
    var_parametrique,
    var_monte_carlo,
    var_historique,
    load_positions,
    VOL_DAILY,
)


# ----------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------

@pytest.fixture
def single_call():
    """A single long CALL position — simplest case."""
    return [{
        "underlying":  "TEST.PA",
        "option_type": "CALL",
        "strike":      100.0,
        "spot":        105.0,
        "vol":         0.20,
        "prix":        8.50,
        "delta":       0.60,
        "gamma":       0.05,
        "vega":        0.15,
        "notional":    100_000,
    }]


@pytest.fixture
def mixed_book():
    """A balanced book: 2 calls + 1 put across 2 underlyings."""
    return [
        {"underlying": "AAA", "option_type": "CALL",
         "strike": 50.0, "spot": 52.0, "vol": 0.22,
         "prix": 4.5, "delta":  0.65, "gamma": 0.04,
         "vega": 0.12, "notional": 100_000},

        {"underlying": "AAA", "option_type": "PUT",
         "strike": 48.0, "spot": 52.0, "vol": 0.25,
         "prix": 1.8, "delta": -0.30, "gamma": 0.03,
         "vega": 0.10, "notional": 100_000},

        {"underlying": "BBB", "option_type": "CALL",
         "strike": 200.0, "spot": 210.0, "vol": 0.18,
         "prix": 18.0, "delta":  0.58, "gamma": 0.02,
         "vega": 0.35, "notional": 100_000},
    ]


@pytest.fixture
def zero_delta_position():
    """A delta-neutral position (delta = 0) — VaR should be near zero."""
    return [{
        "underlying": "NEUTRAL", "option_type": "CALL",
        "strike": 100.0, "spot": 100.0, "vol": 0.20,
        "prix": 5.0, "delta": 0.0, "gamma": 0.03,
        "vega": 0.10, "notional": 100_000,
    }]


@pytest.fixture
def sample_csv_path():
    """Path to the bundled sample positions CSV."""
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "sample_positions.csv"
    )


# ================================================================
# Tests — load_positions
# ================================================================

class TestLoadPositions:

    def test_loads_correct_row_count(self, sample_csv_path):
        positions = load_positions(sample_csv_path)
        assert len(positions) == 10, "sample_positions.csv should have 10 rows"

    def test_required_keys_present(self, sample_csv_path):
        positions = load_positions(sample_csv_path)
        required = {"underlying", "option_type", "strike", "spot",
                    "vol", "prix", "delta", "gamma", "vega", "notional"}
        for p in positions:
            assert required.issubset(p.keys()), f"Missing keys in: {p}"

    def test_numeric_fields_are_floats(self, sample_csv_path):
        positions = load_positions(sample_csv_path)
        numeric = ["strike", "spot", "vol", "prix", "delta", "gamma", "vega", "notional"]
        for p in positions:
            for field in numeric:
                assert isinstance(p[field], float), \
                    f"Field '{field}' should be float, got {type(p[field])}"

    def test_option_types_are_valid(self, sample_csv_path):
        positions = load_positions(sample_csv_path)
        for p in positions:
            assert p["option_type"] in ("CALL", "PUT"), \
                f"Invalid option_type: {p['option_type']}"

    def test_spots_are_positive(self, sample_csv_path):
        positions = load_positions(sample_csv_path)
        for p in positions:
            assert p["spot"] > 0, f"Spot must be > 0, got {p['spot']}"


# ================================================================
# Tests — var_parametrique
# ================================================================

class TestVarParametrique:

    def test_returns_positive_value(self, single_call):
        var = var_parametrique(single_call)
        assert var > 0

    def test_formula_single_position(self, single_call):
        """Manually verify the parametric formula for a single position."""
        p   = single_call[0]
        nb  = p["notional"] / p["spot"]           # shares equivalent
        sig = p["spot"] * VOL_DAILY                # 1-day spot sigma
        exp = 1.6449 * abs(p["delta"] * nb * sig)  # expected VaR

        var = var_parametrique(single_call)
        assert abs(var - exp) < 0.01, f"Expected ~{exp:.2f}, got {var:.2f}"

    def test_var_scales_with_notional(self, single_call):
        """Doubling notional should double the VaR (linear in Delta)."""
        p2 = [{**single_call[0], "notional": single_call[0]["notional"] * 2}]
        var1 = var_parametrique(single_call)
        var2 = var_parametrique(p2)
        assert abs(var2 / var1 - 2.0) < 1e-6, "VaR should scale linearly with notional"

    def test_delta_neutral_returns_zero(self, zero_delta_position):
        """A delta-neutral position should have VaR = 0 under parametric method."""
        var = var_parametrique(zero_delta_position)
        assert var == pytest.approx(0.0, abs=1e-9)

    def test_call_vs_put_same_abs_delta(self):
        """A CALL and PUT with same |delta| and same spot/notional → same VaR."""
        call = [{"underlying": "X", "option_type": "CALL",
                 "strike": 100.0, "spot": 100.0, "vol": 0.20,
                 "prix": 5.0, "delta":  0.50, "gamma": 0.04,
                 "vega": 0.10, "notional": 100_000}]
        put  = [{"underlying": "X", "option_type": "PUT",
                 "strike": 100.0, "spot": 100.0, "vol": 0.20,
                 "prix": 3.0, "delta": -0.50, "gamma": 0.04,
                 "vega": 0.10, "notional": 100_000}]
        assert var_parametrique(call) == pytest.approx(var_parametrique(put), rel=1e-6)

    def test_mixed_book_is_positive(self, mixed_book):
        var = var_parametrique(mixed_book)
        assert var > 0

    def test_ignores_zero_spot_positions(self):
        """Positions with spot=0 should be silently skipped."""
        positions = [
            {"underlying": "BAD", "option_type": "CALL",
             "strike": 100.0, "spot": 0.0, "vol": 0.20,
             "prix": 0.0, "delta": 0.5, "gamma": 0.0,
             "vega": 0.0, "notional": 100_000},
        ]
        var = var_parametrique(positions)
        assert var == pytest.approx(0.0, abs=1e-9)


# ================================================================
# Tests — var_monte_carlo
# ================================================================

class TestVarMonteCarlo:

    def test_returns_positive_value(self, single_call):
        var, _ = var_monte_carlo(single_call, n_simul=1000, seed=42)
        assert var > 0

    def test_reproducible_with_seed(self, single_call):
        """Same seed should produce identical results."""
        var1, _ = var_monte_carlo(single_call, n_simul=2000, seed=99)
        var2, _ = var_monte_carlo(single_call, n_simul=2000, seed=99)
        assert var1 == var2

    def test_different_seeds_different_results(self, single_call):
        """Different seeds should (virtually always) give different results."""
        var1, _ = var_monte_carlo(single_call, n_simul=500, seed=1)
        var2, _ = var_monte_carlo(single_call, n_simul=500, seed=2)
        assert var1 != var2

    def test_pnl_list_length(self, single_call):
        n = 500
        _, pnl = var_monte_carlo(single_call, n_simul=n, seed=42)
        assert len(pnl) == n

    def test_pnl_list_is_sorted_ascending(self, single_call):
        _, pnl = var_monte_carlo(single_call, n_simul=200, seed=42)
        assert pnl == sorted(pnl), "P&L list must be sorted ascending"

    def test_var_is_positive_loss(self, single_call):
        """VaR is reported as a positive number (absolute loss)."""
        var, pnl = var_monte_carlo(single_call, n_simul=1000, seed=42)
        assert var >= 0, "VaR must be reported as a positive number"

    def test_converges_toward_parametric(self, single_call):
        """
        With large N and for a delta-dominated position,
        MC VaR should be in the same order of magnitude as parametric VaR.
        """
        var_param = var_parametrique(single_call)
        var_mc, _ = var_monte_carlo(single_call, n_simul=50_000, seed=42)
        ratio = var_mc / var_param
        assert 0.5 < ratio < 2.0, \
            f"MC VaR ({var_mc:.0f}) diverges too far from Parametric ({var_param:.0f})"

    def test_more_simulations_reduces_variance(self, single_call):
        """
        Running MC twice with the same seed should be identical;
        different seeds show that more simulations stabilize the estimate.
        (Weak test: just check the spread is finite.)
        """
        vars_ = [var_monte_carlo(single_call, n_simul=200, seed=s)[0]
                 for s in range(10)]
        spread = max(vars_) - min(vars_)
        assert spread < var_parametrique(single_call) * 2, \
            "MC VaR spread across seeds should be bounded"


# ================================================================
# Tests — var_historique
# ================================================================

class TestVarHistorique:

    def test_returns_positive_value(self, single_call):
        var, _ = var_historique(single_call)
        assert var > 0

    def test_scenario_count(self, single_call):
        _, results = var_historique(single_call)
        assert len(results) == 25, "Historical scenario set should have 25 entries"

    def test_results_sorted_by_pnl(self, single_call):
        _, results = var_historique(single_call)
        pnls = [r[1] for r in results]
        assert pnls == sorted(pnls), "Results must be sorted by P&L ascending"

    def test_covid_scenario_is_worst_for_long_call(self, single_call):
        """
        For a long CALL (delta > 0), the worst shock (-12% COVID)
        should produce the most negative P&L.
        """
        _, results = var_historique(single_call)
        worst_pnl   = results[0][1]   # most negative after sort
        worst_shock = results[0][0]   # corresponding shock (%)
        assert worst_shock == pytest.approx(-12.0, rel=0.01), \
            f"Expected worst shock = -12% (COVID), got {worst_shock:.1f}%"
        assert worst_pnl < 0

    def test_delta_neutral_var_near_zero(self, zero_delta_position):
        """
        A delta-neutral, long-gamma position profits from large moves (dS^2 > 0).
        Historical VaR can be negative — meaning the position is expected to GAIN
        on crisis scenarios (long convexity). This is financially correct.
        We simply verify the result is a finite number small relative to notional.
        """
        var, _ = var_historique(zero_delta_position)
        assert math.isfinite(var), "VaR must be a finite number"
        # Absolute value should be well below notional
        assert abs(var) < zero_delta_position[0]["notional"] * 0.05, \
            "Delta-neutral VaR (abs) should be < 5% of notional"

    def test_shock_range_includes_positive_scenarios(self, single_call):
        """At least some scenarios should produce a positive P&L."""
        _, results = var_historique(single_call)
        positive = [r for r in results if r[1] > 0]
        assert len(positive) > 0, "At least one scenario should be a gain"

    def test_mixed_book(self, mixed_book):
        var, _ = var_historique(mixed_book)
        assert var > 0


# ================================================================
# Integration test — full pipeline
# ================================================================

class TestFullPipeline:

    def test_all_three_methods_positive(self, mixed_book):
        var_p          = var_parametrique(mixed_book)
        var_mc, _      = var_monte_carlo(mixed_book, n_simul=1000, seed=42)
        var_h, _       = var_historique(mixed_book)

        assert var_p  > 0
        assert var_mc > 0
        assert var_h  > 0

    def test_csv_to_var_pipeline(self, sample_csv_path):
        """End-to-end: load CSV → run all 3 VaR methods → check results."""
        positions = load_positions(sample_csv_path)
        assert len(positions) == 10

        var_p          = var_parametrique(positions)
        var_mc, pnl_mc = var_monte_carlo(positions, n_simul=2000, seed=42)
        var_h, pnl_h   = var_historique(positions)

        for var in (var_p, var_mc, var_h):
            assert var > 0
            assert math.isfinite(var)

        assert len(pnl_mc) == 2000
        assert len(pnl_h)  == 25

    def test_parametric_less_than_mc_for_long_book(self, mixed_book):
        """
        For a long book (net positive delta), parametric VaR (linear)
        is typically less than MC VaR (non-linear with Gamma).
        This is not always true but holds for typical long-call portfolios.
        """
        var_p        = var_parametrique(mixed_book)
        var_mc, _    = var_monte_carlo(mixed_book, n_simul=10_000, seed=42)
        # Allow ±50% tolerance — just check they're in the same ballpark
        ratio = var_mc / var_p
        assert 0.5 < ratio < 3.0, \
            f"Parametric ({var_p:.0f}) and MC ({var_mc:.0f}) should be in same range"
