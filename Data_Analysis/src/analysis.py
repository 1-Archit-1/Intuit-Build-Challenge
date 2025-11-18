import pandas as pd
import numpy as np
from .utils import calculate_profitability_metrics, calculate_rfm, calculate_product_metrics


def profitability_metrics(df, summary_file):
    # Calculate profitability metrics by Region, Category, and Sub-Category
    profit_analysis = (df
        .groupby(['Region', 'Category', 'Sub-Category'])
        .apply(calculate_profitability_metrics, include_groups=False)
        .reset_index()
        .sort_values('Total_Profit', ascending=False)
    )
    profit_analysis['Performance_Tier'] = pd.cut(
        profit_analysis['Total_Profit'],
        bins=[-np.inf] + profit_analysis['Total_Profit'].quantile([0.25, 0.50, 0.75]).tolist() + [np.inf],
        labels=['Needs Improvement', 'Average', 'Good', 'Top']
    )

    print("===== Profitability Analysis By Region, Category & Sub-Category =====")
    print("\nTop 10 Most Profitable Product Lines:")
    print(profit_analysis.head(10).to_string(index=False))

    print("\n\nBottom 10 Least Profitable Product Lines:")
    print(profit_analysis.tail(10).to_string(index=False))

    #Write to file
    summary_file.write("===== Profitability Analysis By Region, Category & Sub-Category =====\n")
    summary_file.write("\nTop 10 Most Profitable Product Lines:\n")
    summary_file.write(profit_analysis.head(10).to_string(index=False))
    summary_file.write("\n\nBottom 10 Least Profitable Product Lines:\n")
    summary_file.write(profit_analysis.tail(10).to_string(index=False))

    tier_summary = (profit_analysis
        .groupby('Performance_Tier')
        .agg({'Total_Profit': 'sum', 'Total_Sales': 'sum', 'Sub-Category': 'count'})
        .rename(columns={'Sub-Category': 'Count'})
    )
    print(f"\n\nPerformance Tier Summary:\n{tier_summary}")
    summary_file.write(f"\n\nPerformance Tier Summary:\n{tier_summary.to_string()}\n")

def RFM_Analysis(df, summary_file):
    # Calculate RFM metrics for each customer
    reference_date = df['Order Date'].max() + pd.Timedelta(days=1)
    
    rfm_data = (df
        .groupby(['Customer ID', 'Customer Name', 'Segment'])
        .apply(calculate_rfm, reference_date=reference_date, include_groups=False)
        .reset_index()
    )

    rfm_data['R_Score'] = pd.cut(
        rfm_data['Recency'], 
        bins=[-1, 90, 180, 365, 730, np.inf],
        labels=[5, 4, 3, 2, 1]
    ).astype(int)
    
    rfm_data['F_Score'] = pd.cut(
        rfm_data['Frequency'],
        bins=[0, 1, 4, 9, 19, np.inf],
        labels=[1, 2, 3, 4, 5]
    ).astype(int)
    
    rfm_data['M_Score'] = pd.cut(
        rfm_data['Monetary'],
        bins=[0, 499, 1999, 4999, 9999, np.inf],
        labels=[1, 2, 3, 4, 5]
    ).astype(int)
    
    rfm_data['RFM_Score'] = rfm_data['R_Score'] + rfm_data['F_Score'] + rfm_data['M_Score']

    segment_customer = lambda row: (
        'Champions' if row['RFM_Score'] >= 13
        else 'Loyal Customers' if row['RFM_Score'] >= 10 and row['R_Score'] >= 4
        else 'Big Spenders' if row['RFM_Score'] >= 10
        else 'Frequent Buyers' if row['F_Score'] >= 4
        else 'Recent Customers' if row['R_Score'] >= 4
        else 'Potential Loyalists' if row['RFM_Score'] >= 7
        else 'At Risk' if row['R_Score'] <= 2
        else 'Needs Attention'
    )
    
    rfm_data['Customer_Segment'] = rfm_data.apply(segment_customer, axis=1)

    print("===== RFM Customer Analysis ======")

    segment_summary = (rfm_data
        .groupby('Customer_Segment')
        .agg({
            'Customer ID': 'count',
            'Monetary': ['sum', 'mean'],
            'Total_Profit': ['sum', 'mean'],
            'Frequency': 'mean',
            'Recency': 'mean'
        })
        .round(2)
    )
    segment_summary.columns = ['Customer_Count', 'Total_Revenue', 'Avg_Revenue', 
                            'Total_Profit', 'Avg_Profit', 'Avg_Frequency', 'Avg_Recency']
    segment_summary = segment_summary.sort_values('Total_Revenue', ascending=False)

    print(f"\nCustomer Segment Summary:\n{segment_summary}")
    summary_file.write(f"\nCustomer Segment Summary:\n{segment_summary.to_string()}\n")

    print("\n\nTop 10 Most Valuable Customers:")
    top_customers = rfm_data.nlargest(10, 'Monetary')[
        ['Customer Name', 'Segment', 'Customer_Segment', 'Monetary', 'Total_Profit', 
        'Frequency', 'Recency', 'RFM_Score']
    ]
    print(top_customers.to_string(index=False))
    summary_file.write("\n\nTop 10 Most Valuable Customers:\n")
    summary_file.write(top_customers.to_string(index=False))

def product_analysis(df, summary_file):
    # Calculate total sales for revenue share calculation
    total_sales = df['Sales'].sum()
    
    # Analyze product performance and classify using BCG matrix
    product_analysis = (df
        .groupby(['Category', 'Sub-Category'])
        .apply(calculate_product_metrics, total_sales=total_sales, include_groups=False)
        .reset_index()
        .sort_values('Revenue', ascending=False)
    )

    median_growth = product_analysis['Revenue_Share'].median()
    median_margin = product_analysis['Profit_Margin'].median()

    conditions = [
        (product_analysis['Revenue_Share'] > median_growth) & (product_analysis['Profit_Margin'] > median_margin),
        (product_analysis['Revenue_Share'] <= median_growth) & (product_analysis['Profit_Margin'] > median_margin),
        (product_analysis['Revenue_Share'] > median_growth) & (product_analysis['Profit_Margin'] <= median_margin)
    ]
    choices = ['Star', 'Question Mark', 'Cash Cow']
    product_analysis['BCG_Category'] = np.select(conditions, choices, default='Dog')
    print("\n===== Product Analysis =====")
    print("\nTop 10 Categories by Revenue:")
    print(product_analysis.head(10).to_string(index=False))
    
    summary_file.write("\n===== Product Analysis =====\n")
    summary_file.write("\nTop 10 Categories by Revenue:\n")
    summary_file.write(product_analysis.head(10).to_string(index=False))
    
    bcg_summary = (product_analysis
        .groupby('BCG_Category')
        .agg({'Revenue': 'sum', 'Profit': 'sum', 'Sub-Category': 'count', 'Profit_Margin': 'mean'})
        .rename(columns={'Sub-Category': 'Product_Count'})
        .round(2)
    )
    print(f"\n\nBCG Matrix Classification:")
    print(bcg_summary)
    summary_file.write(f"\n\nBCG Matrix Classification:\n{bcg_summary.to_string()}\n")
    print("\n\nProduct Concentration:")
    total_profit = product_analysis['Profit'].sum()
    
    list(map(
        lambda n: print(f"Top {n} products: "
                       f"{product_analysis.head(n)['Revenue_Share'].sum():.2f}% revenue, "
                       f"{product_analysis.head(n)['Profit'].sum() / total_profit * 100:.2f}% profit"),
        [3, 5, 10]
    ))
    summary_file.write("\n\nProduct Concentration:\n")
    list(map(
        lambda n: summary_file.write(f"Top {n} products: "
                       f"{product_analysis.head(n)['Revenue_Share'].sum():.2f}% revenue, "
                       f"{product_analysis.head(n)['Profit'].sum() / total_profit * 100:.2f}% profit\n"),
        [3, 5, 10]
    ))