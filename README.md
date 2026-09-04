# Replication Package

**Characterizing Method-Level License Frictions in Open-Source Software Ecosystems**

Aminul Didar Islam, Slinger Jansen

This package reproduces every statistic, table, and figure reported in the
paper, from the processed corpus through to the final numbers.

---

## Contents

```
.
├── README.md
├── requirements.txt
├── verify_results.py                        # checks output against the paper
├── data/
│   ├── license_analysis_results_processed.csv   # the analysis corpus
│   └── DSR_engine.py                            # license mapping (dependency)
├── results/                                 # all generated CSVs
├── figures/                                 # generated figures
├── h1_license_reuse_analysis.ipynb
├── h1_poisson_vs_negbin_comparison.ipynb
├── h1a_truncation_robustness.ipynb
├── h2_concentration_analysis.ipynb
├── h3_license_family_analysis.ipynb
├── h4_language_analysis.ipynb
├── h5_ownership_analysis.ipynb
└── classifier_crossvalidation.ipynb
```

`data/` is read-only input. Everything in `results/` and `figures/` is
regenerable — delete both and rerun to reproduce from scratch.

---

## Requirements

```bash
pip install -r requirements.txt
```

Python 3.11. `statsmodels >= 0.13` is required: the truncation analysis uses
`TruncatedLFNegativeBinomialP`, which earlier versions do not provide.

---

## Running

Notebooks read and write through path constants defined in their first cell,
which resolve relative to this directory. Launch Jupyter from here.

**Order matters for the first three.** `h1_license_reuse_analysis` produces two
intermediate tables that later notebooks consume:

| # | Notebook | Depends on |
|---|---|---|
| 1 | `h1_license_reuse_analysis` | corpus |
| 2 | `h1_poisson_vs_negbin_comparison` | `results/h1_analysis_dataframe.csv` |
| 3 | `h1a_truncation_robustness` | `results/h1_analysis_dataframe.csv`, `results/h1a_analysis_dataframe.csv` |
| 4–8 | `h2`, `h3`, `h4`, `h5`, `classifier_crossvalidation` | corpus only — any order |

Restart the kernel before each notebook and run cells top to bottom.

---

## What each notebook does

### `h1_license_reuse_analysis` — H1 and H1a
Whether license declaration (H1) and license family (H1a) predict how often a
repository is reused as a provenance source, with repository age as a
covariate. Builds the repository-level tables both hypotheses use.

Reproduces: N = 17,368 (11,314 licensed / 6,054 unlicensed); Cliff's δ = 0.030;
age-controlled β = 0.014, p = .332. H1a: N = 11,252 (9,035 Permissive / 2,217
Reciprocal); IRR = 1.047, p = .029.

### `h1_poisson_vs_negbin_comparison`
Confirms Negative Binomial over Poisson for the count outcome.
Reproduces: ΔAIC = 5,523.98, ΔBIC = 5,516.22.

### `h1a_truncation_robustness`
`reuse_count` is ≥ 1 by construction, so an ordinary Negative Binomial places
mass on an impossible outcome. Four cells, in argument order: fit the truncated
model, compute marginal effects, check calibration, then use a stable
alternative.

Reproduces: the zero-truncated model's dispersion parameter diverging to the
boundary (α̂ ≈ 10³–10⁵ against 0.26 untruncated) and a 54% over-prediction of
the mean, which disqualify it; the shifted-outcome model (α̂ = 2.99) gives
p = .0015 (linear age) and p = .044 (log age).

### `h2_concentration_analysis` — H2
Concentration of compliance debt across projects, by Gini and Lorenz curve,
with bootstrap confidence intervals.

Reproduces: N = 10,337 projects (8,407 for the density measure); Gini = 0.9604
(actionable debt) and 0.7404 (density-normalised); 57.7% of projects with
resolved provenance carry zero actionable debt. Writes
`figures/h2_lorenz_curves.png`.

Also writes `results/h2_top10_category4_projects.csv`, the ten
highest-volume Category 4 projects, supporting the outlier-sensitivity
check in the paper's Threats to Validity. These ten account for 46% of
all 17,147 Category 4 instances, with no single project exceeding 9% —
so the Category 4 Gini (0.992) is sensitive to a handful of large
contributors, while the combined (0.960) and density-normalised (0.740)
measures are not.

### `h3_license_family_analysis` — H3
License family against violation subtype, restricted to Category 3. Category 4
is excluded because every Category 4 row carries an unresolved origin license,
making a cross-category test circular.

Reproduces: N = 66,136 (51.07% Permissive); χ²(1) = 30.06, p = 4.19e-08;
Cohen's h = 0.043 (negligible). Category 4: 0.00% with a resolved origin
license.

### `h4_language_analysis` — H4
Friction across six programming languages, plus a clustering robustness check
at the repository level.

Reproduces: N = 1,116,445; Cramér's V = 0.073; friction rates 8.19% (Java) to
17.13% (C#); odds ratios 0.524 (Java) and 1.213 (C#) against the C baseline.
Repository-level: 5,362 repositories, ε² = 0.020.

### `h5_ownership_analysis` — H5
Friction across ownership cohorts, plus cluster-robust and organization-level
robustness checks.

Reproduces: N = 868,369; friction rates 66.22% (Corporate), 75.51%
(Individual), 77.35% (OSS Foundation); χ²(2) = 11,179.39, V = 0.114.
Organization level: 52 organizations, U = 247.0, p = .17, Cliff's δ = −0.23.

### `classifier_crossvalidation`
Cross-validates the license classifier: exact dictionary lookup against a
keyword-matching implementation, across all 1,183,182 rows.

Reproduces: **0 disagreements**.

---

## Verifying

After regenerating, check the output against the values reported in the paper:

```bash
python3 verify_results.py
```

This reads `results/` and validates 40 quantities — sample sizes, group splits,
effect sizes, p-values, contingency cells, and post-hoc comparisons. It prints a
per-check pass/fail table and exits non-zero on any mismatch.

Two reported values are printed by notebooks but not written to CSV, so confirm
them in the notebook output: **Cohen's h = 0.0426** (H3) and **0 disagreements**
(classifier cross-validation).

---

## The dataset

`data/license_analysis_results_processed.csv` — **1,183,182 rows**, one per
deduplicated method-level provenance relationship, across 10,337 query
repositories and six languages.

Each row records: a method that was found in one repository (the **source**,
i.e. the origin) and reused in another (the **sink**), together with the
licensing context of both ends and the resulting LCD compliance category.

### Columns

| Column | Type | Description |
|---|---|---|
| `organization_name` | string | Owning organisation. Individual-maintainer repositories all share the literal value `Individual`, so this is **not** a distinct identifier for them. |
| `project_type` | int | Ownership cohort: **1 = Corporate, 2 = OSS Foundation, 3 = Individual**. |
| `method_hash` | string | Structural (AST-based) hash identifying the method. Part of the deduplication key. |
| `method_name` | string | Method identifier as it appears in source. |
| `language` | string | One of C, C++, C#, Java, JavaScript, Python. Some rows use `JS`; normalise to `JavaScript` before grouping. |
| `base_repository_url` | string | Canonical repository identity for the query project. Clean and populated across all categories — **use this for project-level grouping** rather than parsing the source/sink URLs. |
| `source_repository_url` | string | Repository the method originated from. |
| `sink_repository_url` | string | Repository the method was reused in. **Null for Category 0 rows** (see caveats). |
| `source_file_location` | string | Path of the file at the origin. |
| `sink_file_location` | string | Path of the file at the sink. |
| `source_version` | float | Commit timestamp (ms) of the origin. **Genuinely per-commit** — this is what repository age is derived from. |
| `sink_version` | float | **Project-level scan-time constant, not a per-method timestamp.** Do not use as a per-row covariate. |
| `source_file_license` | string | License of the origin **repository**. See caveats. |
| `sink_file_license` | string | License of the sink **repository**. See caveats. |
| `violation_lcd_category` | int | LCD category 0–5 (below). |
| `violation_text` | string | Human-readable verdict naming the licenses involved, e.g. `"Sink is following same license Apache-2.0"`, `"Undetermined: Apache-2.0 with the Unknown (Provenance Debt)"`, `"Observed Origin-no match found with SearchSECO database"`. Explanatory detail accompanying `violation_lcd_category`; not used as an analysis variable. |
| `relational_id` | string | Scan/run identifier (timestamp + hash), **constant across rows from the same extraction batch** — not a per-row key. Not used in any analysis. |

### LCD categories

| Value | Label | Meaning |
|---|---|---|
| 0 | No Match | No upstream provenance match; treated as project-original code. |
| 1 | Compliant (Identical) | Reused under the same license as the origin. |
| 2 | Compliant (Divergent) | Reused under a different but compatible license. |
| 3 | Procedural Incompatibility | Origin and sink licenses directly incompatible. |
| 4 | Structural / High Risk | High-probability boundary violation, e.g. unlicensed or unattributed code entering a proprietary sink. |
| 5 | Latent Debt | Missing or unresolvable licensing metadata prevents a verdict. |


### Working with this data

Practical notes for anyone building on this corpus. None of these are defects;
they are properties of how the data was extracted, and each one shapes how an
analysis should be written.

1. **License fields are repository-level.** Despite the `*_file_license`
   naming, these carry the license declared by the repository rather than one
   parsed from each individual file. This matches how licensing usually
   operates: most source files carry no header of their own, so the
   repository's declaration is the operative license for them. The construct
   was validated against human annotation — two researchers labelled 1,934
   method pairs following SPDX compatibility guidelines (inter-rater
   κ = 0.84), and the classification pipeline built on these fields reached a
   macro F1 of 95.0%. Repeated observations of the same repository agree
   99.90% of the time, the remainder reflecting license changes between scan
   snapshots. Analyses needing per-file resolution would require a different
   extraction step.

2. **Category 0 rows have source and sink reversed.** `sink_repository_url` is
   null and the project's identity sits in `source_repository_url`. Grouping by
   `base_repository_url` sidesteps this entirely.

3. **`sink_version` is a scan-time constant**, identical across every row of a
   project. Only `source_version` varies per commit, and it is what repository
   age is derived from.

4. **Deduplicate on `["method_hash", "source_repository_url",
   "sink_repository_url"]`.** The distributed corpus is already deduplicated —
   rerunning the step should remove 0 rows, which makes a useful sanity check.

5. **License strings are full spelled-out names**, e.g.
   `"GNU General Public License v2.0"`. Substring matching on abbreviations
   such as `"gpl"` will not match; classification uses exact lookup through
   `DSR_engine.py`.

6. **About 3.9% of URLs** do not match the canonical `github.com/org/repo`
   pattern (enterprise hosts, gists, unusual paths) and are dropped where
   project-identity resolution is required. The H1 notebook reports this count.

### Generated results

`results/` holds every CSV the notebooks produce. Most correspond
directly to a table or figure in the paper; two are supporting
material:

| File | Contents |
|---|---|
| `h2_top10_category4_projects.csv` | The ten projects with the most Category 4 (Structural/High Risk) instances, with each project's share of the 17,147 total. Supports the outlier-sensitivity discussion in Threats to Validity. |
| `h5_org_level_rates.csv` | Per-organization friction rate and relationship count for the 52 organizations retained in H5's clustering robustness check. |

Both are inputs to claims in the paper rather than headline results, and are included so those claims can be checked directly.

Note that the highest-volume Category 4 projects are predominantly large corporate repositories. This is consistent with H5: Corporate
repositories contribute high absolute instance counts by virtue of size while showing the lowest friction *rate* of the three cohorts.

---

## Notes on the data

`data/license_analysis_results_processed.csv` is the processed analysis corpus:
1,183,182 deduplicated method-level provenance relationships across 10,337
query repositories. It is derived from the SearchSECO provenance database
(~1M repositories, ~74M indexed methods); the full reference index is not
distributed here owing to its size. The processed corpus is sufficient to
reproduce every result in the paper.

**Two friction definitions are used, deliberately.** H2 and H4 count LCD
Categories 3 and 4 as friction. H5 uses the broader Categories 3, 4 and 5,
because unresolved licensing metadata is itself informative about the
organisational governance quality H5 investigates. Category 0 (no provenance
match) is excluded where friction status would be undefined. See the paper's
Study Design section.

---

## Citation

Please cite the paper. See the accompanying supplementary documents for the
methodological justification of each statistical choice
(`supplements/supplementary_validation_v1.pdf`) and for step-by-step derivations of every
reported statistic (`supplementary_validation_2.docx`).

---

## License

Code (notebooks, `DSR_engine.py`, `verify_results.py`) is released under the
MIT License; see `LICENSE`.

The processed corpus and generated results are released under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).