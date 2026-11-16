# Running the older-adult analysis on Kaggle

## Inputs (4 files, keep the Kaggle dataset PRIVATE)
| File | Cohort | Source |
|---|---|---|
| `PSG_cleaned_records_final.xlsx` | PLDC (India) | PSG IMSR, not public |
| `predictions_all_patients.csv` | PLDC patient list and order | PSG IMSR, not public |
| `osseus_dataset.csv` | HUOL (Brazil) | Zenodo, doi:10.5281/zenodo.14259374 |
| `patient_details.xlsx` | UPH (India) | Mendeley Data, doi:10.17632/fxjm8fb6mw.2 |

File names may carry a prefix (for example `1794400878491_predictions_all_patients.csv`); the runner finds them by name.

## Steps
1. Kaggle > Datasets > New dataset: upload the 4 files, name it `osteo-data`, visibility **Private**.
2. Kaggle > Datasets > New dataset: upload `clinical-classification-kaggle.zip` (this folder), name it `osteo-code`. Kaggle unzips it.
3. Kaggle > Code > New notebook. In the right panel: Add input > Your datasets > add `osteo-data` and `osteo-code`.
   Settings: Accelerator **None** (CPU), Internet **On**.
4. Run these three cells:
```
!pip install -q -U scikit-learn imbalanced-learn statsmodels openpyxl
```
```
!cp -r /kaggle/input/osteo-code/clinical-classification /kaggle/working/ 2>/dev/null || cp -r $(dirname $(find /kaggle/input -name kaggle_run.py | head -1)) /kaggle/working/clinical-classification
```
```
!python /kaggle/working/clinical-classification/kaggle_run.py
```
5. Run time is about 30-60 minutes on the free CPU. The last line says "Done".
6. Output panel (right, /kaggle/working): download **share.zip** only. It holds `older_adults_summary.json`
   and Figure_1-4, Figure_S1-S2 (aggregate numbers, no patient rows).
   Do NOT download or share `work/` (it holds the patient-level file and predictions).
7. Send share.zip back. Afterwards you may delete the notebook output or the private dataset.

## Quick test (2-4 minutes) before the full run
```
!python /kaggle/working/clinical-classification/kaggle_run.py --nboot 5
```
This checks that everything runs; its confidence intervals are not usable. Then run the full command above.
