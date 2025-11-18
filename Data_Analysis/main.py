import pandas as pd
import src
import os

if __name__ == "__main__":
    path = src.fetch_data("vivek468/superstore-dataset-final")
    df = pd.read_csv(f'data/Sample - Superstore.csv', encoding='latin1')
    # Create summary file  as well
    summary_path = os.path.join("data", "summary.txt")
    with open(summary_path, "w") as summary_file:
        src.run_preprocessing(df)
        src.profitability_metrics(df, summary_file)
        src.RFM_Analysis(df, summary_file)
        src.product_analysis(df, summary_file)