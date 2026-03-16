"""Feature engineering for credit scoring model."""

import pandas as pd
import numpy as np
from pathlib import Path


def engineer_features(df):
    """Create new features from existing ones."""
    df = df.copy()

    # Profit margin
    df['profit_margin'] = df['net_profit'] / df['revenue']

    # Debt ratio (inverse of debt-to-equity)
    df['debt_ratio'] = df['debt_to_equity']

    # Balance to revenue ratio
    df['balance_to_revenue'] = df['avg_balance'] / df['revenue']

    # Profit to balance ratio
    df['profit_to_balance'] = df['net_profit'] / df['avg_balance']

    # Fraud risk categories
    df['fraud_risk_level'] = pd.cut(df['fraud_score'],
                                    bins=[0, 30, 60, 100],
                                    labels=['low', 'medium', 'high'])

    # Convert categorical to numeric
    df['fraud_risk_level'] = df['fraud_risk_level'].map({'low': 0, 'medium': 1, 'high': 2})

    # Interaction features
    df['revenue_fraud_interaction'] = df['revenue'] * df['fraud_score'] / 1000000
    df['profit_debt_interaction'] = df['net_profit'] * df['debt_to_equity']

    # Log transformations for skewed features
    df['log_revenue'] = np.log1p(df['revenue'])
    df['log_avg_balance'] = np.log1p(df['avg_balance'])

    return df


def create_engineered_dataset():
    """Create and save engineered features dataset."""
    data_path = Path(__file__).parent / "data" / "labeled_scorer_data.csv"
    output_path = Path(__file__).parent / "data" / "labeled_scorer_data_engineered.csv"

    df = pd.read_csv(data_path)
    df_engineered = engineer_features(df)

    df_engineered.to_csv(output_path, index=False)
    print(f"Engineered dataset saved to {output_path}")
    print(f"Original features: {len(df.columns) - 1}")  # -1 for target
    print(f"Engineered features: {len(df_engineered.columns) - 1}")

    return df_engineered


if __name__ == "__main__":
    create_engineered_dataset()