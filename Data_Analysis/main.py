import pandas as pd
from utils import fetch_data
from preprocessing_pipeline import run_preprocessing
import analysis
import os

if __name__ == "__main__":
    path = fetch_data("vivek468/superstore-dataset-final")
    df = pd.read_csv(f'data/Sample - Superstore.csv', encoding='latin1')
    # Create summary file  as well
    summary_path = os.path.join("data", "summary.txt")
    with open(summary_path, "w") as summary_file:
        run_preprocessing(df)
        analysis.profitability_metrics(df, summary_file)
        analysis.RFM_Analysis(df, summary_file)
        analysis.product_analysis(df, summary_file)