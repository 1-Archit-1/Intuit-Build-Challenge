import pytest
import pandas as pd
import numpy as np
from datetime import timedelta
from utils import calculate_profitability_metrics, calculate_rfm, calculate_product_metrics


@pytest.fixture
def sample_df():
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    
    return pd.DataFrame({
        'Order Date': dates,
        'Ship Date': dates + timedelta(days=2),
        'Region': np.random.choice(['West', 'East', 'South', 'North'], 100),
        'Category': np.random.choice(['Technology', 'Furniture', 'Office'], 100),
        'Sub-Category': np.random.choice(['Phones', 'Chairs', 'Laptop', 'Storage'], 100),
        'Customer ID': np.random.choice([f'C-{i}' for i in range(20)], 100),
        'Customer Name': np.random.choice([f'Customer {i}' for i in range(20)], 100),
        'Segment': np.random.choice(['Consumer', 'Corporate', 'Home'], 100),
        'Sales': np.random.uniform(10, 1000, 100),
        'Profit': np.random.uniform(-50, 300, 100),
        'Profit Margin': np.random.uniform(-10, 30, 100),
        'Quantity': np.random.randint(1, 10, 100),
        'Discount': np.random.uniform(0, 0.3, 100),
        'Product ID': np.random.choice([f'PID-{i}' for i in range(30)], 100)
    })


def test_calculate_profitability_metrics(sample_df):
    result = calculate_profitability_metrics(sample_df)
    
    assert 'Total_Sales' in result
    assert 'Total_Profit' in result
    assert 'Order_Count' in result
    assert result['Order_Count'] == len(sample_df)
    assert result['Total_Sales'] == sample_df['Sales'].sum()


def test_calculate_rfm(sample_df):
    reference_date = sample_df['Order Date'].max() + pd.Timedelta(days=1)
    customer_data = sample_df[sample_df['Customer ID'] == sample_df['Customer ID'].iloc[0]]
    
    result = calculate_rfm(customer_data, reference_date)
    
    assert 'Recency' in result
    assert 'Frequency' in result
    assert 'Monetary' in result
    assert result['Frequency'] == len(customer_data)
    assert result['Monetary'] == customer_data['Sales'].sum()


def test_calculate_product_metrics(sample_df):
    result = calculate_product_metrics(sample_df)
    
    assert 'Revenue' in result
    assert 'Profit' in result
    assert 'Units_Sold' in result
    assert result['Revenue'] == sample_df['Sales'].sum()
    assert result['Units_Sold'] == sample_df['Quantity'].sum()


def test_handles_negative_profits():
    loss_data = pd.DataFrame({
        'Sales': [100, 200],
        'Profit': [-50, -30],
        'Profit Margin': [-50, -15],
        'Quantity': [1, 2],
        'Discount': [0.5, 0.4],
        'Customer ID': ['C1', 'C2']
    })
    
    result = calculate_profitability_metrics(loss_data)
    assert result['Total_Profit'] < 0
    assert result['Profitable_Orders_Pct'] == 0


def test_profit_margin_with_zero_sales():
    zero_sales = pd.DataFrame({
        'Sales': [0],
        'Profit': [0],
        'Quantity': [0],
        'Customer ID': ['C1']
    })
    
    result = calculate_product_metrics(zero_sales)
    assert result['Profit_Margin'] == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
