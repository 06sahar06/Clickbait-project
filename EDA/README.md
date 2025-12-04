# EDA (Exploratory Data Analysis)

This folder contains the exploratory data analysis for the Clickbait project.

## Files

- **general_EDA.ipynb**: Comprehensive notebook with per-file analysis of all CSV datasets
  - Imports and loads all CSV files from the `data/` folder
  - Provides statistical summaries (shape, dtypes, missing values, duplicates, memory usage)
  - Generates distribution plots for numeric and categorical columns
  - Includes a QUICK_RUN mode to sample rows (default: 200 rows) for faster iteration

## Usage

1. Open `general_EDA.ipynb` in Jupyter Notebook
2. Set `QUICK_RUN = True` for quick iteration on sampled data
3. Set `QUICK_RUN = False` to analyze the entire dataset (slower)
4. Run the cells sequentially for a comprehensive analysis of each CSV file

## Data Path

The notebook expects the `data/` folder to be located at:
```
c:\Users\Sahar\Desktop\Clickbait_git\Clickbait-project\data
```

You may need to adjust this path based on your local setup.

## Analysis Includes

- Data shape and dimensions
- Column names and data types
- Missing values detection
- Duplicate row detection
- Basic statistical summaries
- Memory usage estimates
- Distribution plots for numeric columns
- Frequency distributions for categorical columns
