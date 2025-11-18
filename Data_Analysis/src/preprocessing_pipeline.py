from functools import reduce
from itertools import groupby
from operator import itemgetter
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

def run_preprocessing(df):
    # Data Preparation using functional programming
    df_processed = (df
        .pipe(parse_dates)
        .pipe(add_derived_columns)
        .pipe(categorize_order_size)
    )
    print("Data processed successfully!")
    print(f"Total Records: {len(df_processed):,}")
    print(f"\nNew columns added: {['Profit Margin', 'Shipping Days', 'Order Year', 'Order Month', 'Order Quarter', 'Order Size']}")
    print(f"\nDate range: {df_processed['Order Date'].min()} to {df_processed['Order Date'].max()}")

# Define transformation functions
def parse_dates(df):
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['Ship Date'] = pd.to_datetime(df['Ship Date'])
    return df

def add_derived_columns(df):
    df['Profit Margin'] = df.apply(lambda row: (row['Profit'] / row['Sales'] * 100) if row['Sales'] > 0 else 0, axis=1)
    df['Shipping Days'] = df.apply(lambda row: (row['Ship Date'] - row['Order Date']).days, axis=1)
    df['Order Year'] = df['Order Date'].apply(lambda x: x.year)
    df['Order Month'] = df['Order Date'].apply(lambda x: x.month)
    df['Order Quarter'] = df['Order Date'].apply(lambda x: f"Q{x.quarter}")
    return df

def categorize_order_size(df):
    df['Order Size'] = df['Sales'].apply(
        lambda x: 'Small' if x < 100 else 'Medium' if x < 500 else 'Large' if x < 2000 else 'Extra Large'
    )
    return df



