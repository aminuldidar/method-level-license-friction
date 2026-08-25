"""
Verify regenerated results against the manuscript
--------------------------------------------------------------------------
Reads every CSV in results/ and checks the values the paper actually reports.
Running without error proves the code executes; this proves it reproduces.

    python verify_results.py

Exit code 0 if everything matches, 1 otherwise.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path.cwd()
ROOT = ROOT if (ROOT / "results").exists() else ROOT.parent
RESULTS = ROOT / "results"

checks, failures = [], []


def check(label, got, want, tol=None):
    """tol=None -> exact match; otherwise absolute tolerance."""
    if got is None:
        ok = False
        shown = "MISSING"
    elif tol is None:
        ok = got == want
        shown = got
    else:
        ok = abs(float(got) - float(want)) <= tol
        shown = round(float(got), 6)
    checks.append((ok, label, shown, want))
    if not ok:
        failures.append(label)


def load(name):
    p = RESULTS / name
    if not p.exists():
        return None
    return pd.read_csv(p)


# ------------------------------------------------------------------ H1
df = load("h1_analysis_dataframe.csv")
if df is None:
    check("h1_analysis_dataframe.csv exists", None, "present")
else:
    check("H1 N repositories", len(df), 17368)
    check("H1 licensed", int(df.has_license.astype(bool).sum()), 11314)
    check("H1 unlicensed", int((~df.has_license.astype(bool)).sum()), 6054)
    check("H1 min reuse_count (zero-truncation)", int(df.reuse_count.min()), 1)
    check("H1 zero-valued rows", int((df.reuse_count == 0).sum()), 0)

mw = load("h1_mannwhitney_summary.csv")
if mw is not None and "cliffs_delta" in mw.columns:
    check("H1 Cliff's delta", mw["cliffs_delta"].iloc[0], 0.0304, tol=0.002)

# ------------------------------------------------------------------ H1a
da = load("h1a_analysis_dataframe.csv")
if da is None:
    check("h1a_analysis_dataframe.csv exists", None, "present")
else:
    check("H1a N repositories", len(da), 11252)
    fam = da["license_family"] if "license_family" in da.columns else None
    if fam is not None:
        check("H1a Permissive", int((fam == "Permissive").sum()), 9035)
        check("H1a Reciprocal", int((fam == "Reciprocal").sum()), 2217)
    check("H1a min reuse_count", int(da.reuse_count.min()), 1)

nb = load("h1a_negbin_summary.csv")
if nb is not None:
    col0 = nb.columns[0]
    row = nb[nb[col0].astype(str).str.contains("is_permissive", na=False)]
    if len(row):
        check("H1a coefficient", row["coef"].iloc[0], 0.0462, tol=0.0005)
        check("H1a IRR", row["IRR"].iloc[0], 1.0473, tol=0.0005)
        check("H1a p-value", row["p_value"].iloc[0], 0.02938, tol=0.0005)

sh = load("h1a_shifted_nb_comparison.csv")
if sh is not None and "model" in sh.columns:
    s = sh[sh["model"].str.contains("shifted", case=False, na=False)]
    if len(s) >= 2:
        ps = sorted(float(x) for x in s["p"])
        check("H1a shifted-NB p (linear)", ps[0], 0.001459, tol=0.0005)
        check("H1a shifted-NB p (log-age)", ps[1], 0.04361, tol=0.002)

# ------------------------------------------------------------------ H2
g = load("h2_gini_bootstrap_ci.csv")
if g is None:
    check("h2_gini_bootstrap_ci.csv exists", None, "present")
else:
    want = {"Category 3": 0.9613, "Category 4": 0.9923,
            "Combined": 0.9604, "density": 0.7404}
    for key, val in want.items():
        row = g[g["measure"].str.contains(key, case=False, na=False)]
        check(f"H2 Gini ({key})",
              row["gini"].iloc[0] if len(row) else None, val, tol=0.002)
    dens = g[g["measure"].str.contains("density", case=False, na=False)]
    if len(dens):
        check("H2 density panel N", int(dens["n"].iloc[0]), 8407)

# ------------------------------------------------------------------ H4
h4 = load("h4_language_summary.csv")
if h4 is None:
    check("h4_language_summary.csv exists", None, "present")
else:
    check("H4 total relationships", int(h4["total_methods"].sum()), 1116445)
    rates = dict(zip(h4["language"], h4["friction_rate_pct"]))
    for lang, val in [("C#", 17.13), ("Java", 8.19), ("C", 14.56)]:
        check(f"H4 friction rate {lang}", rates.get(lang), val, tol=0.05)

orr = load("h4_logit_odds_ratios.csv")
if orr is not None:
    col0 = orr.columns[0]
    for lang, val in [("Java", 0.524), ("C#", 1.213)]:
        row = orr[orr[col0].astype(str).str.contains(lang, na=False, regex=False)]
        check(f"H4 odds ratio {lang}",
              row["Odds Ratio"].iloc[0] if len(row) else None, val, tol=0.01)

rl = load("h4_repo_level_rates.csv")
if rl is not None:
    check("H4 repositories (>=5 rel.)", len(rl), 5362)

# ------------------------------------------------------------------ H5
h5 = load("h5_contingency_table.csv")
if h5 is None:
    check("h5_contingency_table.csv exists", None, "present")
else:
    tot = int(h5["Non-Friction"].sum() + h5["Friction"].sum())
    check("H5 N relationships", tot, 868369)
    for coh, nf, fr in [("Corporate", 131117, 256999),
                        ("Individual", 61308, 188995),
                        ("OSS Foundation", 52086, 177864)]:
        r = h5[h5["cohort"] == coh]
        check(f"H5 {coh} non-friction",
              int(r["Non-Friction"].iloc[0]) if len(r) else None, nf)
        check(f"H5 {coh} friction",
              int(r["Friction"].iloc[0]) if len(r) else None, fr)

ph = load("h5_posthoc_pairwise.csv")
if ph is not None:
    for pair, val in [("Corporate vs OSS Foundation", 0.117811),
                      ("Corporate vs Individual", 0.098823),
                      ("Individual vs OSS Foundation", 0.021620)]:
        r = ph[ph["comparison"] == pair]
        check(f"H5 V ({pair})",
              r["cramers_v"].iloc[0] if len(r) else None, val, tol=0.001)

og = load("h5_org_level_rates.csv")
if og is not None:
    check("H5 organizations retained", len(og), 52)
    if "cohort" in og.columns:
        vc = og["cohort"].value_counts()
        check("H5 Corporate orgs", int(vc.get("Corporate", 0)), 32)
        check("H5 OSS Foundation orgs", int(vc.get("OSS Foundation", 0)), 20)

# ------------------------------------------------------------------ report
print("=" * 78)
print(f"VERIFYING {RESULTS}")
print("=" * 78)
print(f"{'':4}{'check':46}{'got':>13}{'expected':>13}")
print("-" * 78)
for ok, label, got, want in checks:
    print(f"{'ok  ' if ok else 'FAIL'}{label:46}{str(got):>13}{str(want):>13}")

print("-" * 78)
n_ok = sum(1 for c in checks if c[0])
print(f"{n_ok}/{len(checks)} checks passed")
if failures:
    print("\nFAILED:")
    for f in failures:
        print(f"  - {f}")
    print("\nA failure means the regenerated output differs from the manuscript.")
    print("Investigate before shipping -- do not update the paper to match.")
    sys.exit(1)
print("\nAll reported values reproduce. Package is consistent with the paper.")
sys.exit(0)
