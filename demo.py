#!/usr/bin/env python3
# ================================================================
# demo.py - CommandoQuant Standalone Demo
# ================================================================
# Runs the full VaR pipeline WITHOUT SQL Server.
# Uses sample positions from data/sample_positions.csv.
#
# Usage:
#   python demo.py
#   python demo.py --output results/my_var_report.xlsx
#
# Requirements: pip install openpyxl
# Optional:     pip install pandas  (for richer CSV loading)
# ================================================================

import csv
import math
import os
import sys
import argparse
import random


# ----------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------
DEFAULT_INPUT  = os.path.join(os.path.dirname(__file__), "data", "sample_positions.csv")
DEFAULT_OUTPUT = os.path.join(os.path.dirname(__file__), "var_results_demo.xlsx")

CONFIDENCE = 0.95
N_SIMUL    = 10000
VOL_DAILY  = 0.015    # ~25% annualized / sqrt(252)


# ----------------------------------------------------------------
# 1. Load positions from CSV (no SQL Server needed)
# ----------------------------------------------------------------
def load_positions(csv_path: str) -> list:
    """
    Loads option positions from a CSV file.

    Expected columns:
      underlying, option_type, strike, spot, vol, prix,
      delta, gamma, vega, notional

    Returns a list of dicts — same structure as lire_positions()
    in var_engine.py (SQL mode).
    """
    positions = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            positions.append({
                "underlying":  row["underlying"],
                "option_type": row["option_type"],
                "strike":      float(row["strike"]),
                "spot":        float(row["spot"]),
                "vol":         float(row["vol"]),
                "prix":        float(row["prix"]),
                "delta":       float(row["delta"]),
                "gamma":       float(row["gamma"]),
                "vega":        float(row["vega"]),
                "notional":    float(row["notional"]),
            })

    print(f"[OK] {len(positions)} positions loaded from {csv_path}")
    return positions


# ----------------------------------------------------------------
# 2. VaR Parametric (Delta method)
# ----------------------------------------------------------------
def var_parametrique(positions: list, confidence: float = 0.95) -> float:
    """
    Parametric VaR — 1st order Taylor approximation via Delta.

    Formula:  VaR = z * sqrt( sum( (Delta * nb * sigma_spot)^2 ) )
    z(95%)  = 1.6449

    Fast but ignores convexity (Gamma).
    """
    z = 1.6449
    variance = 0.0

    for p in positions:
        if p["spot"] <= 0:
            continue
        nb         = p["notional"] / p["spot"]
        sigma_spot = p["spot"] * VOL_DAILY
        contrib    = p["delta"] * nb * sigma_spot
        variance  += contrib ** 2

    var = z * math.sqrt(variance)
    print(f"  [Parametric VaR 95%]   {var:>12,.2f} EUR")
    return var


# ----------------------------------------------------------------
# 3. VaR Monte Carlo (Delta + Gamma)
# ----------------------------------------------------------------
def var_monte_carlo(positions: list, n_simul: int = 10000,
                    confidence: float = 0.95, seed: int = None):
    """
    Monte Carlo VaR — N random market scenarios.

    dP_i = Delta * dS_i + 0.5 * Gamma * dS_i^2
    dS_i = spot * vol_daily * epsilon_i  (epsilon ~ N(0,1))

    More accurate than parametric: captures convexity via Gamma.
    Returns (var, pnl_list).
    """
    if seed is not None:
        random.seed(seed)

    pnl_list = []

    for _ in range(n_simul):
        pnl = 0.0
        for p in positions:
            if p["spot"] <= 0:
                continue
            nb = p["notional"] / p["spot"]

            # Box-Muller transform → N(0,1)
            u1 = random.random() or 1e-10
            u2 = random.random()
            eps = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)

            dS  = p["spot"] * VOL_DAILY * eps
            dP  = (p["delta"] * dS + 0.5 * p["gamma"] * dS ** 2) * nb
            pnl += dP

        pnl_list.append(pnl)

    pnl_list.sort()
    idx = int((1.0 - confidence) * n_simul)
    var = -pnl_list[idx]

    print(f"  [Monte Carlo VaR 95%]  {var:>12,.2f} EUR  ({n_simul:,} simulations)")
    return var, pnl_list


# ----------------------------------------------------------------
# 4. VaR Historical (real crisis shocks)
# ----------------------------------------------------------------
def var_historique(positions: list, confidence: float = 0.95):
    """
    Historical VaR — replay real market crisis shocks.

    Scenario set includes: COVID-19, Lehman Brothers, Flash Crash,
    European debt crisis, Brexit, Ukraine war, SVB collapse.

    Returns (var, [(shock_pct, pnl), ...]).
    """
    shocks = [
        (-0.120, "COVID-19 March 2020"),
        (-0.095, "Lehman Brothers Sept 2008"),
        (-0.072, "Flash Crash May 2010"),
        (-0.068, "EU Sovereign Debt 2011"),
        (-0.055, "Brexit June 2016"),
        (-0.048, "Russia-Ukraine Feb 2022"),
        (-0.042, "SVB Collapse March 2023"),
        (-0.035, "Stress -3.5%"),
        (-0.028, "Stress -2.8%"),
        (-0.022, "Stress -2.2%"),
        (-0.018, "Stress -1.8%"),
        (-0.015, "Normal -1.5%"),
        (-0.012, "Normal -1.2%"),
        (-0.010, "Normal -1.0%"),
        (-0.008, "Normal -0.8%"),
        (-0.006, "Normal -0.6%"),
        ( 0.005, "Recovery +0.5%"),
        ( 0.010, "Recovery +1.0%"),
        ( 0.015, "Recovery +1.5%"),
        ( 0.020, "Rebound +2.0%"),
        ( 0.030, "Rebound +3.0%"),
        ( 0.045, "Bull Run +4.5%"),
        ( 0.060, "Bull Run +6.0%"),
        ( 0.075, "Strong Rally +7.5%"),
        ( 0.085, "Post-COVID Rebound"),
    ]

    results = []
    for choc, label in shocks:
        pnl = 0.0
        for p in positions:
            if p["spot"] <= 0:
                continue
            nb  = p["notional"] / p["spot"]
            dS  = p["spot"] * choc
            dP  = (p["delta"] * dS + 0.5 * p["gamma"] * dS ** 2) * nb
            pnl += dP
        results.append((choc * 100, pnl, label))

    results.sort(key=lambda x: x[1])
    idx = int((1.0 - confidence) * len(results))
    var = -results[idx][1]

    print(f"  [Historical VaR 95%]   {var:>12,.2f} EUR  ({len(shocks)} scenarios)")
    return var, results


# ----------------------------------------------------------------
# 5. Export to Excel (styled report)
# ----------------------------------------------------------------
def export_excel(positions, var_param, var_mc, pnl_mc,
                 var_histo, pnl_histo, output_path: str):
    """
    Generates a styled Excel report with 3 sheets:
      - VaR Summary   : comparison of 3 methods + position breakdown
      - Monte Carlo   : first 200 simulated P&L scenarios
      - Historical    : all crisis stress test results
    """
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment
    except ImportError:
        print("[WARN] openpyxl not installed. Skipping Excel export.")
        print("       Run: pip install openpyxl")
        return

    # CommandoQuant color palette
    DARK  = "0B1426"
    AMBER = "D4880A"
    GOLD  = "F0B429"
    GREEN = "00C853"
    RED   = "E53935"
    NAVY  = "0D2040"
    NAVY2 = "112855"
    WHITE = "FFFFFF"

    def hdr(cell, bg=NAVY, fg=GOLD):
        cell.font      = Font(bold=True, color=fg, size=10)
        cell.fill      = PatternFill("solid", fgColor=bg)
        cell.alignment = Alignment(horizontal="center", vertical="center")

    def title(cell):
        cell.font      = Font(bold=True, color=GOLD, size=14)
        cell.fill      = PatternFill("solid", fgColor=DARK)
        cell.alignment = Alignment(horizontal="center", vertical="center")

    wb = Workbook()

    # ---- Sheet 1: VaR Summary ----
    ws = wb.active
    ws.title = "VaR Summary"
    ws.row_dimensions[1].height = 36

    ws.merge_cells("A1:F1")
    title(ws["A1"])
    ws["A1"] = "CommandoQuant  —  Value-at-Risk Report  (Demo Mode)"

    ws.merge_cells("A2:F2")
    ws["A2"] = (
        f"Portfolio: {len(positions)} positions  |  "
        f"Confidence: {int(CONFIDENCE*100)}%  |  Horizon: 1 day  |  "
        f"Vol: {VOL_DAILY*100:.2f}%/day"
    )
    ws["A2"].font      = Font(italic=True, color="B0BEC5", size=9)
    ws["A2"].fill      = PatternFill("solid", fgColor=DARK)
    ws["A2"].alignment = Alignment(horizontal="center")

    for col, h in enumerate(["Method", "VaR 95% (EUR)", "Description", "Reliability"], 1):
        hdr(ws.cell(4, col, h))

    rows_var = [
        ("Parametric (Delta)",       round(var_param, 2),
         "Analytical formula — Delta sensitivity only",   "Fast / ignores Gamma"),
        ("Monte Carlo (10,000 sim)", round(var_mc,    2),
         f"10,000 random market scenarios (Delta+Gamma)", "Accurate / heavier"),
        ("Historical (crisis shocks)",round(var_histo, 2),
         "COVID, Lehman, Flash Crash, Brexit, Ukraine…",  "Realistic / known crises only"),
    ]

    for i, (method, val, desc, rel) in enumerate(rows_var):
        r = 5 + i
        ws.cell(r, 1, method)
        c = ws.cell(r, 2, val)
        c.font = Font(bold=True, color=RED, size=11)
        ws.cell(r, 3, desc)
        ws.cell(r, 4, rel)
        bg = NAVY if i % 2 == 0 else NAVY2
        for col in range(1, 5):
            ws.cell(r, col).fill = PatternFill("solid", fgColor=bg)
            if col != 2:
                ws.cell(r, col).font = Font(color=WHITE)

    ws.merge_cells("A9:F9")
    hdr(ws["A9"], bg=AMBER, fg=DARK)
    ws["A9"] = "PORTFOLIO POSITIONS"

    for col, h in enumerate(
        ["Underlying", "Type", "Strike", "Spot", "Delta", "VaR Contribution (EUR)"], 1
    ):
        hdr(ws.cell(10, col, h))

    for i, p in enumerate(positions):
        r   = 11 + i
        nb  = p["notional"] / p["spot"] if p["spot"] > 0 else 0
        con = abs(p["delta"] * nb * p["spot"] * VOL_DAILY * 1.6449)
        ws.cell(r, 1, p["underlying"])
        ws.cell(r, 2, p["option_type"])
        ws.cell(r, 3, round(p["strike"],  2))
        ws.cell(r, 4, round(p["spot"],    2))
        ws.cell(r, 5, round(p["delta"],   4))
        ws.cell(r, 6, round(con,          2))
        bg = NAVY if i % 2 == 0 else NAVY2
        for col in range(1, 7):
            ws.cell(r, col).fill = PatternFill("solid", fgColor=bg)
            ws.cell(r, col).font = Font(color=WHITE)

    ws.column_dimensions["A"].width = 16
    ws.column_dimensions["B"].width = 8
    ws.column_dimensions["C"].width = 10
    ws.column_dimensions["D"].width = 10
    ws.column_dimensions["E"].width = 10
    ws.column_dimensions["F"].width = 22

    # ---- Sheet 2: Monte Carlo distribution ----
    ws2 = wb.create_sheet("Monte Carlo")
    ws2.merge_cells("A1:B1")
    title(ws2["A1"])
    ws2["A1"] = "P&L Distribution — Monte Carlo (first 200)"
    for col, h in enumerate(["Scenario #", "P&L (EUR)"], 1):
        hdr(ws2.cell(3, col, h))
    for i, pnl in enumerate(pnl_mc[:200]):
        r = 4 + i
        ws2.cell(r, 1, i + 1)
        c = ws2.cell(r, 2, round(pnl, 2))
        c.font = Font(color=RED if pnl < 0 else GREEN, bold=True)
        bg = NAVY if i % 2 == 0 else NAVY2
        for col in (1, 2):
            ws2.cell(r, col).fill = PatternFill("solid", fgColor=bg)
        ws2.cell(r, 1).font = Font(color=WHITE)
    ws2.column_dimensions["A"].width = 14
    ws2.column_dimensions["B"].width = 16

    # ---- Sheet 3: Historical stress ----
    ws3 = wb.create_sheet("Historical")
    ws3.merge_cells("A1:C1")
    title(ws3["A1"])
    ws3["A1"] = "Historical Stress Tests — Real Crisis Scenarios"
    for col, h in enumerate(["Spot Shock (%)", "Portfolio P&L (EUR)", "Event"], 1):
        hdr(ws3.cell(3, col, h))
    for i, (choc, pnl, label) in enumerate(pnl_histo):
        r = 4 + i
        ws3.cell(r, 1, f"{choc:+.1f}%")
        c = ws3.cell(r, 2, round(pnl, 2))
        c.font = Font(color=RED if pnl < 0 else GREEN, bold=True)
        ws3.cell(r, 3, label)
        bg = NAVY if i % 2 == 0 else NAVY2
        for col in (1, 2, 3):
            ws3.cell(r, col).fill = PatternFill("solid", fgColor=bg)
            if col != 2:
                ws3.cell(r, col).font = Font(color=WHITE)
    ws3.column_dimensions["A"].width = 16
    ws3.column_dimensions["B"].width = 24
    ws3.column_dimensions["C"].width = 30

    wb.save(output_path)
    print(f"\n[OK] Report saved: {output_path}")


# ----------------------------------------------------------------
# Main entry point
# ----------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="CommandoQuant — Standalone VaR Demo (no SQL Server required)"
    )
    parser.add_argument(
        "--input", default=DEFAULT_INPUT,
        help=f"CSV file with positions (default: {DEFAULT_INPUT})"
    )
    parser.add_argument(
        "--output", default=DEFAULT_OUTPUT,
        help=f"Output Excel report path (default: {DEFAULT_OUTPUT})"
    )
    parser.add_argument(
        "--simulations", type=int, default=N_SIMUL,
        help=f"Number of Monte Carlo simulations (default: {N_SIMUL})"
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed for Monte Carlo reproducibility (default: 42)"
    )
    args = parser.parse_args()

    print("=" * 60)
    print("  CommandoQuant — VaR Engine  (Demo / Standalone Mode)")
    print("=" * 60)

    if not os.path.exists(args.input):
        print(f"[ERROR] Input file not found: {args.input}")
        sys.exit(1)

    positions = load_positions(args.input)

    if not positions:
        print("[ERROR] No valid positions found in CSV.")
        sys.exit(1)

    print(f"\nPositions loaded ({len(positions)}):")
    for p in positions:
        print(f"  {p['underlying']:<8} {p['option_type']:<5} "
              f"K={p['strike']:>7.2f}  S={p['spot']:>7.2f}  "
              f"Delta={p['delta']:>+.4f}")

    print("\n--- VaR Calculation ---")
    var_p              = var_parametrique(positions)
    var_mc, pnl_mc     = var_monte_carlo(positions, args.simulations, seed=args.seed)
    var_h, pnl_h       = var_historique(positions)

    print("\n--- Exporting Report ---")
    export_excel(positions, var_p, var_mc, pnl_mc, var_h, pnl_h, args.output)

    print("\n" + "=" * 60)
    print("  RESULTS SUMMARY")
    print("=" * 60)
    print(f"  Parametric VaR  95% : {var_p:>12,.2f} EUR")
    print(f"  Monte Carlo VaR 95% : {var_mc:>12,.2f} EUR")
    print(f"  Historical VaR  95% : {var_h:>12,.2f} EUR")
    print("=" * 60)
    print("  Done.")


if __name__ == "__main__":
    main()
