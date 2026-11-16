#!/usr/bin/env bash
# Runs the full analysis. Assumes the three input files are in ./data (see data/README.md).
# Most of the run time is in steps 1, 2 and 5.
set -euo pipefail
cd "$(dirname "$0")"
for s in 01_main_analysis 02_two_class 03_permutation_importance 04_per_class_and_sex 05_master_analysis \
         06_matched_bootstrap_and_90rule 09_reviewer_analyses 10_shap_and_associations 12_class_balancing_comparison 13_hyperparameters_and_runtime 14_review_round3 15_huol_zscore_and_synthetic_bmi 07_build_results_workbook 08_make_figures; do
  echo "=== $s"
  python scripts/$s.py
done
echo "All outputs are in ./results"
