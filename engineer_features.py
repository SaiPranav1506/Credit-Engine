"""
Apply feature engineering to the synthetic dataset.
Converts raw 5-feature dataset to engineered 14-feature dataset.
"""

import pandas as pd
import numpy as np
from pathlib import Path


def engineer_features(df):
    """
    Apply feature engineering transformations.
    Mimics what's in labeled_scorer_data_engineered.csv
    """
    engineered = df.copy()
    
    # 1. Profit margin
    engineered['profit_margin'] = engineered['net_profit'] / engineered['revenue'].replace(0, 1)
    
    # 2. Debt ratio (alternative to D2E)
    engineered['debt_ratio'] = engineered['debt_to_equity'] / (engineered['debt_to_equity'] + 1)
    
    # 3. Balance to revenue ratio
    engineered['balance_to_revenue'] = engineered['avg_balance'] / engineered['revenue'].replace(0, 1)
    
    # 4. Profit to balance ratio
    engineered['profit_to_balance'] = engineered['net_profit'] / engineered['avg_balance'].replace(0, 1)
    
    # 5. Fraud risk level (categorize fraud_score)
    engineered['fraud_risk_level'] = pd.cut(
        engineered['fraud_score'],
        bins=[0, 33, 66, 100],
        labels=[0, 1, 2],
        include_lowest=True
    ).astype(int)
    
    # 6. Fraud-revenue interaction
    engineered['fraud_revenue_interaction'] = (engineered['fraud_score'] / 100) * engineered['revenue'] / 1_000_000
    
    # 7. Profit-debt interaction
    engineered['profit_debt_interaction'] = engineered['net_profit'] * engineered['debt_to_equity']
    
    # 8. Log revenue
    engineered['log_revenue'] = np.log1p(engineered['revenue'])
    
    # 9. Log average balance
    engineered['log_avg_balance'] = np.log1p(engineered['avg_balance'])
    
    # Handle infinite values (only for numeric columns)
    engineered = engineered.replace([np.inf, -np.inf], np.nan)
    numeric_cols = engineered.select_dtypes(include=[np.number]).columns
    engineered[numeric_cols] = engineered[numeric_cols].fillna(engineered[numeric_cols].mean())
    
    return engineered


def main():
    # Load synthetic data
    df = pd.read_csv('credit_engine/data/labeled_scorer_data.csv')
    print(f"Loaded dataset with {len(df)} records and {len(df.columns)} columns")
    print(f"Shape: {df.shape}")
    
    # Apply feature engineering
    df_engineered = engineer_features(df)
    
    # Verify
    print(f"\nEngineered dataset shape: {df_engineered.shape}")
    print(f"Columns: {list(df_engineered.columns)}")
    
    # Save
    output_path = Path('credit_engine/data/labeled_scorer_data_engineered.csv')
    df_engineered.to_csv(output_path, index=False)
    print(f"\n✅ Saved engineered dataset to {output_path}")
    
    # Show sample
    print(f"\nFirst 3 rows:")
    print(df_engineered.head(3))
    
    print(f"\nDataset statistics:")
    print(df_engineered.describe())


if __name__ == "__main__":
    main()
