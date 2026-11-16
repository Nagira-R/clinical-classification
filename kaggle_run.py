"""Run the older-adult analysis on Kaggle (or any machine) in one go.

Usage (Kaggle notebook cell):   !python /kaggle/working/clinical-classification/kaggle_run.py
Finds the four input files anywhere under /kaggle/input (or under the folder given with --input), prepares the
de-identified PLDC file, runs step 20 (analysis) and step 21 (figures), and writes /kaggle/working/share.zip with
aggregate results only (summary JSON + figures). Patient-level files stay in /kaggle/working/work and must not be shared.
"""
import argparse, glob, os, shutil, subprocess, sys, time
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument('--input', default='/kaggle/input'); ap.add_argument('--work', default='/kaggle/working/work')
ap.add_argument('--nboot', default='1000')
a = ap.parse_args()
ROOT = Path(__file__).resolve().parent


def find(pattern):
    hits = sorted(glob.glob(os.path.join(a.input, '**', pattern), recursive=True))
    if not hits:
        sys.exit(f'Input file not found under {a.input}: {pattern}')
    return hits[0]


records = find('*PSG*cleaned*records*final*.xlsx'); preds = find('*predictions*all*patients*.csv')
huol = find('*osseus*dataset*.csv'); uph = find('*patient*details*.xlsx')
print('inputs:\n ', records, '\n ', preds, '\n ', huol, '\n ', uph)
data = Path(a.work) / 'data'; res = Path(a.work) / 'results'; data.mkdir(parents=True, exist_ok=True)
shutil.copy(huol, data / 'osseus_dataset.csv'); shutil.copy(uph, data / 'uph_patient_details.xlsx')
env = dict(os.environ, OSTEO_DATA_DIR=str(data), OSTEO_RESULTS_DIR=str(res), OSTEO_NB=a.nboot, MPLBACKEND='Agg')
t0 = time.time()
for cmd in ([sys.executable, 'scripts/00_prepare_psg.py', '--records', records, '--predictions', preds],
            [sys.executable, 'scripts/20_older_adults.py'], [sys.executable, 'scripts/21_older_adults_figures.py']):
    print('\n>>>', ' '.join(cmd[1:2]), flush=True)
    subprocess.run(cmd, cwd=ROOT, env=env, check=True)
share = res / 'share'
shutil.make_archive('/kaggle/working/share' if a.input.startswith('/kaggle') else str(Path(a.work) / 'share'), 'zip', share)
print(f'\nDone in {(time.time() - t0) / 60:.0f} min. Download share.zip (aggregate results only) and send it back.')
