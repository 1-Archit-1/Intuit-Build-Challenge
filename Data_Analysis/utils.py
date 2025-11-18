
import pandas as pd
def calculate_profitability_metrics(group_df):
    return pd.Series({
        'Total_Sales': group_df['Sales'].sum(),
        'Total_Profit': group_df['Profit'].sum(),
        'Avg_Profit_Margin': group_df['Profit Margin'].mean(),
        'Order_Count': len(group_df),
        'Avg_Order_Value': group_df['Sales'].mean(),
        'Total_Quantity': group_df['Quantity'].sum(),
        'Profitable_Orders_Pct': (group_df['Profit'] > 0).sum() / len(group_df) * 100,
        'Avg_Discount': group_df['Discount'].mean() * 100
    })

def calculate_rfm(customer_df, reference_date):
    return pd.Series({
        'Recency': (reference_date - customer_df['Order Date'].max()).days,
        'Frequency': len(customer_df),
        'Monetary': customer_df['Sales'].sum(),
        'Avg_Order_Value': customer_df['Sales'].mean(),
        'Total_Profit': customer_df['Profit'].sum(),
        'Lifetime_Quantity': customer_df['Quantity'].sum(),
        'Avg_Discount': customer_df['Discount'].mean()
    })


def calculate_product_metrics(product_df, total_sales=None):
    product_sales = product_df['Sales'].sum()
    
    # If total_sales not provided, calculate from current df (will be 100%)
    if total_sales is None:
        total_sales = product_sales
    
    return pd.Series({
        'Revenue': product_sales,
        'Revenue_Share': (product_sales / total_sales * 100) if total_sales > 0 else 0,
        'Profit': product_df['Profit'].sum(),
        'Units_Sold': product_df['Quantity'].sum(),
        'Orders': len(product_df),
        'Avg_Price': product_df['Sales'].mean(),
        'Profit_Margin': (product_df['Profit'].sum() / product_sales * 100) if product_sales > 0 else 0,
        'Return_Rate': ((product_df['Profit'] < 0).sum() / len(product_df)) * 100 if len(product_df) > 0 else 0,
        'Unique_Customers': product_df['Customer ID'].nunique()
    })

import kagglehub
def fetch_data(dataset):
    # Download latest version
    path = kagglehub.dataset_download("vivek468/superstore-dataset-final", force_download=True)

    # Copy path files to local dir
    import os
    os.makedirs("data", exist_ok=True)
    for file in os.listdir(path):
        print(file)
        os.replace(os.path.join(path, file), os.path.join("data", file))

    return path