# Superstore Data Analysis

A Python-based data analysis project demonstrating functional programming techniques with pandas on retail sales data.

## Dataset

**Source**: [Kaggle - Superstore Dataset](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final)

**Choice Reason**: 
- Transactional data with multiple dimensions (region, category, customer, time)
- Suitable for complex aggregation and multi-level analysis
- Real-world business metrics (sales, profit, discount)

## Key Assumptions

1. **Data Quality**: All transactions are final
2. **Currency**: All monetary values are in USD
3. **Profit**: Negative profit indicates loss
4. **Customer Identity**: Customer IDs are unique for a customer
5. **Product Hierarchy**: Category → Sub-Category → Product relationship is maintained

## Setup

### 1. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv analysis_env

# Activate virtual environment
# On Linux/Mac:
source analysis_env/bin/activate

# On Windows:
analysis_env\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Download Dataset

The dataset will be automatically downloaded when you first run the analysis:

```bash
python3 main.py
```

## Running the Analysis

```bash
# Run complete analysis
python3 main.py

```

## Running Tests

```bash
# Run all tests
pytest test_analysis.py -v

# Run specific test
pytest test_analysis.py::test_calculate_rfm -v

```

## Analysis Outputs

### 1. Profitability Analysis
- Multi-level aggregation (Region -> Category -> Sub-Category)
- Performance tier classification
- Top/bottom performers

### 2. RFM Customer Segmentation
- Recency, Frequency, Monetary scoring
- Customer segment classification (Champions, At Risk, etc)
- Top valuable customers

### 3. Product Portfolio Analysis
- BCG Matrix classification (Stars, Cash Cows, Dogs, Question Marks)
- Revenue and profit concentration

## Key Insights

The analysis provides actionable insights on:
- Most/least profitable product lines
- Customer lifetime value and retention risk
- Product portfolio optimization opportunities
- Revenue concentration and diversification

## Requirements

- Python 3.8+


### Why These Analyses?
- **Profitability**: Core business metric, hierarchical analysis
- **RFM**: Industry-standard customer segmentation
- **BCG Matrix**: Strategic framework for product decisions

