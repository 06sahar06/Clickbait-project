# Dataset folder (data/)

This repository contains CSV datasets used for the Clickbait project. Large CSV files are stored in Git LFS to avoid hitting GitHub's normal file-size limits.

Location
- All dataset CSV files are in the `data/` directory at the repository root.

Key notes
- Git LFS is enabled and the repository tracks `*.csv` with Git LFS. When you clone the repository, run `git lfs pull` to download the actual CSV content.
- Some files are large (multi-hundred MB / multiple GB). Be mindful of your local disk space and Git LFS quotas.

Quick start

1. Clone the repository:

```powershell
git clone https://github.com/06sahar06/Clickbait-project.git
cd "Clickbait project\Dataset"
```

2. Install Python dependencies (recommended inside a virtualenv):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

3. Pull LFS objects (download large CSV files):

```powershell
git lfs install
git lfs pull
```

4. Use the helper script `explore_data.py` to interactively explore CSVs without loading the entire file into memory.

Examples

List CSVs in `data/`:

```powershell
python explore_data.py --list
```

Show the first 10 rows of a file:

```powershell
python explore_data.py --head data/titles.csv --n 10
```

Reservoir-sample 500 rows from a large file (safe for memory):

```powershell
python explore_data.py --sample data/sponsorTimes.csv --n 500
```

If you are collaborating, remind teammates to run `git fetch` and `git lfs pull` after cloning or after any large-file changes.

Contact
- If you need the raw dataset hosted elsewhere (cloud bucket, releases), let me know and I can prepare scripts to upload and replace the in-repo copies with download pointers.
