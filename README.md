# Clinical-only osteoporosis classification in three cohorts

Analysis code for the article *Machine learning of three-class osteoporosis classification in adults using clinical variables* (Nagira Rajahussain, Sarathambekai Subramaniam, Umamaheswari Kandaswamy, Arun Prasad Ramaswamy; submitted to Archives of Gerontology and Geriatrics).

The study asks how well five routinely recorded variables (age, sex, height, weight and body mass index)
classify bone status into the three WHO classes (normal, osteopenia, osteoporosis), whether machine learning
improves on the OSTA screening formula, whether models transfer between cohorts, and how much of the apparent
performance comes from the age mix of a cohort.

- **PLDC** (PSG Lumbar DXA Cohort, India, n = 388, lumbar-spine DXA): development cohort, not public.
- **HUOL** (Brazil, n = 669, DXA, lowest of four sites): public.
- **UPH** (India, n = 237, quantitative-ultrasound T-scores): public, exploratory.

BMD, T-scores and Z-scores are **never** used as predictors.

## Primary analysis: adults aged 50 or more (current article)

`scripts/20_older_adults.py` runs every analysis of the article in PLDC and HUOL patients aged 50 or more, with the
whole cohorts and UPH as sensitivity analyses, and writes `results/older_adults_summary.json` (aggregate numbers only).
`scripts/21_older_adults_figures.py` draws Figures 1-4 and Figs. A.1-A.2 (Appendix A) from that file. `kaggle_run.py` runs both in one go;
see `KAGGLE_README.md`.
`scripts/22_review_extras.py` adds the review analyses (final model coefficients, uniform shrinkage and log-loss tuning, the
multinomial sample-size check, selected hyperparameters, single-repeat confusion matrices and package versions) and writes
`results/share/review_extras.json`; `notebooks/review_extras_kaggle.ipynb` runs it on Kaggle. Step 21 draws Fig. 2 from
that file when it is present. Figures are written as PNG (300 dpi) and vector PDF; `results/paper` holds the published
figures and tables (CSV; Tables 1-6 and Appendix A Tables A.1-A.9) and the two aggregate JSON files. Steps 01-15 below reproduce the earlier whole-cohort analysis.

## Repository layout

```
osteo/                 shared code
  config.py            paths (override with OSTEO_DATA_DIR / OSTEO_RESULTS_DIR) and global settings
  data.py              cohort loaders: the five common predictors, extended sets, labels
  modelling.py         models and tuning grids, metrics, outer folds, bootstrap helpers
scripts/               run in numerical order
  00_prepare_psg.py    data custodians only: builds the de-identified PLDC file from hospital records
  01_main_analysis.py  nested CV (5 models, 3 classes), baselines, external validation, strata, learning curves, decision curves
  02_two_class.py      dedicated two-class models with Youden cut-offs chosen inside training parts
  03_permutation_importance.py
  04_per_class_and_sex.py
  05_master_analysis.py  repeat-averaged predictions, paired bootstrap, age matching, calibration, operating points, external CIs
  06_matched_bootstrap_and_90rule.py  bootstrap CIs for age-matched AUCs, 90%-sensitivity referral rule
  09_reviewer_analyses.py  ordinal model, results by gender, decision curves with CIs, transported operating points,
                       matching balance and age+gender matching, FRAX-type and extended predictor sets (run before step 07)
  10_shap_and_associations.py  baseline tests, predictor correlations and VIF, odds ratios, out-of-fold SHAP
                       (logistic regression; random forest check), participant-flow and SHAP figures (run before step 07)
  13_hyperparameters_and_runtime.py   settings selected in each outer fold and fit/predict times per algorithm
  14_review_round3.py  ordinal-error summary and prevalence-adjusted rule, calibration CIs, external intercept update,
                       LR on age and weight, 90%-sensitivity rule for age alone (writes results/review3.xlsx)
  15_huol_zscore_and_synthetic_bmi.py  HUOL without the 60 Z-score patients; BMI consistency of SMOTE-NC synthetic patients
  12_class_balancing_comparison.py   no correction vs class weights vs SMOTE-NC vs ADASYN, all models and cohorts
  11_huol_boosting_and_extended_sets.py  optional, HUOL only: XGBoost, LightGBM, CatBoost, extra trees, ensembles,
                       21 clinical + engineered + device variables (the slowest step)
  07_build_results_workbook.py  writes results/master_results.xlsx (every number in the paper)
  08_make_figures.py   writes results/figures/ (working file names; the published figures and tables are in results/paper/)
figures_code/          one file per group of figures, plus shared plot style
data/README.md         where to obtain each input file and the expected columns
run_all.sh             runs all steps in order (01-06, 09, 10, 12, 13, 14, 07, 08)
```

## How to run

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# place the input files in ./data (see data/README.md)
./run_all.sh                                          # or run the scripts one by one
```

Outputs go to `./results` (pickled predictions and metrics, `master_results.xlsx`, `figures/`).
The published tables (CSV) and figures (PNG) are in `results/paper/`; see `results/README.md` for the index.
All analyses were run on a laptop CPU (no GPU); most of the run time is in steps 1, 2 and 5.

Without the PLDC file, the HUOL and UPH analyses can still be inspected, but the scripts as written expect
all three cohorts; the PLDC data can be requested from the corresponding author (see `data/README.md`).

## Validation design (summary)

- **Internal validation:** nested cross-validation. Imputation (median; missing height or weight imputed and BMI recomputed from them), scaling, tuning (inner 3-fold grid search),
  recalibration and threshold selection are fitted inside each outer training part only.
  All three cohorts use stratified 5-fold cross-validation repeated three times (seed 42).
- **Class balancing:** SMOTE-NC (imbalanced-learn) inside every training part only, after imputation and before
  scaling; gender is treated as categorical. Set `OSTEO_BALANCE=weights|none|adasyn` to change it (default `smotenc`).
- **Three logistic models:** (1) three-class with SMOTE-NC (three-class results);
  (2) two-class with SMOTE-NC and a Youden cut-off (two-class results and paired comparisons);
  (3) two-class without class balancing (calibration, Brier score, fixed-risk operating points, 90%-sensitivity rule).
- **OSTA:** 0.2 × (weight − age). The continuous score is used for AUC; the integer score (decimals truncated)
  is used with the published cut-offs (below +1, −1 or lower, below −4).
- **Uncertainty:** SD across repeats, and 1,000 patient-level bootstrap resamples of repeat-averaged predictions;
  paired bootstrap for model differences.
- **Age matching:** equal cases and non-cases within 5-year age bands (500 draws); CIs from 1,000 patient
  bootstrap resamples, each followed by a fresh matched draw.
- **External validation:** train on one full cohort, test on each other cohort; thresholds fixed in the
  training cohort; leave-one-cohort-out pooling.
- **Decision curves:** net benefit from the unweighted models' repeat-averaged risks, thresholds 5-50%,
  1,000 patient bootstrap resamples for CIs, compared with referring everyone or no one.
- **Ordinal model:** proportional-odds logistic regression (statsmodels OrderedModel) on the same folds.

## Where each result comes from

`07_build_results_workbook.py` collects every number into `results/master_results.xlsx`, and `08_make_figures.py`
draws the figures from the saved results. Sheet and figure file names follow the analysis scripts and an earlier
draft, so they do not always match the published numbering. The published Tables 1–10, Figs. 1–4,
Tables S1–S18 and Figs. S1–S7 are in `results/paper/`, indexed in `results/README.md`.

Gender is used as recorded in the source records (male or female). Internally the code keeps the column name `sex_male`;
all outputs (workbook and figures) label it as gender.

## Data protection

No patient-level data, images or identifiers are included in this repository, and `.gitignore` blocks data
and generated result files. `results/paper/` holds only summary tables and figures. The PLDC analysis file contains only the variables listed in `data/README.md`.

## Ethics

The PLDC study was approved by the Institutional Human Ethics Committee of PSG Institute of Medical Sciences &
Research, Coimbatore, India (Ref. No. PSG/IHEC/2026/Appr/Exp/052), with a waiver of informed consent.
HUOL and UPH are public, de-identified datasets.

## Citation and licence

Please cite the article (see `CITATION.cff`). Code released under the MIT licence.
