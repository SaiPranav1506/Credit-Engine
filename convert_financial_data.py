"""
Alternative: Load financial data from CSV/structured sources.
Useful for LendingClub, Home Credit, and other Kaggle datasets.
"""

import pandas as pd
import numpy as np
from pathlib import Path


class FinancialDataConverter:
    """Convert various financial datasets to your training format."""
    
    @staticmethod
    def from_lending_club(csv_path):
        """
        Convert LendingClub CSV to your format.
        
        Download from: https://www.kaggle.com/datasets/wordsforthewise/lending-club
        
        LendingClub columns → your model format:
        - annual_inc → revenue
        - loan_amnt → used for fraud_score calculation
        - dti → debt_to_equity (debt-to-income ratio)
        - delinq_2yrs → fraud_score component
        - total_acc → avg_balance estimate
        - loan_status → expected_decision
        """
        try:
            df = pd.read_csv(csv_path, nrows=1000)  # Load first 1000 for demo
            
            # Create your feature set
            result = pd.DataFrame()
            
            # Revenue = annual income
            result['revenue'] = df['annual_inc'].fillna(df['annual_inc'].mean())
            
            # Net profit = estimated (30% of revenue)
            result['net_profit'] = result['revenue'] * 0.30
            
            # Debt-to-equity = debt-to-income ratio
            result['debt_to_equity'] = df['dti'].fillna(0.8)
            
            # Fraud score = based on delinquencies and late payments
            fraud_score = (
                df['delinq_2yrs'].fillna(0) * 15 +  # 15 points per delinquency
                df['inq_last_6mths'].fillna(0) * 5 +  # 5 points per inquiry
                (df['pub_rec'].fillna(0) > 0).astype(int) * 40  # 40 points if has public record
            ).clip(0, 100)
            result['fraud_score'] = fraud_score
            
            # Average balance estimate
            result['avg_balance'] = (df['total_acc'].fillna(5) * 50000).clip(10000, 1000000)
            
            # Label: APPROVE if fully paid, REJECT if charged off
            result['expected_decision'] = df['loan_status'].apply(
                lambda x: 'APPROVE' if x == 'Fully Paid' else 'REJECT'
            )
            
            # Clean up
            result = result.dropna()
            result = result[(result['revenue'] > 0) & (result['debt_to_equity'] >= 0)]
            
            print(f"✅ Converted {len(result)} LendingClub records")
            return result
        
        except Exception as e:
            print(f"❌ Error reading LendingClub data: {e}")
            return None
    
    @staticmethod
    def from_home_credit(application_csv, bureau_csv=None):
        """
        Convert Home Credit Default Risk dataset.
        
        Download from: https://www.kaggle.com/c/home-credit-default-risk
        """
        try:
            df_app = pd.read_csv(application_csv, nrows=1000)
            
            result = pd.DataFrame()
            
            # Revenue = annual income
            result['revenue'] = df_app['AMT_INCOME_TOTAL'].fillna(100000)
            
            # Net profit = estimated credit amount * 0.2 (conservative)
            result['net_profit'] = (df_app['AMT_CREDIT'].fillna(50000) * 0.2)
            
            # Debt-to-equity = credit-to-income ratio
            result['debt_to_equity'] = (
                df_app['AMT_CREDIT'].fillna(50000) / df_app['AMT_INCOME_TOTAL'].fillna(100000)
            ).clip(0, 5)
            
            # Fraud score based on target (0 = good, 1 = default)
            fraud_score = df_app['TARGET'].fillna(0) * 50 + \
                          (df_app['EXT_SOURCE_1'].fillna(0.5) < 0.3).astype(int) * 30
            result['fraud_score'] = fraud_score.clip(0, 100)
            
            # Average balance estimate
            result['avg_balance'] = (df_app['AMT_CREDIT'].fillna(50000) * 0.4)
            
            # Label
            result['expected_decision'] = df_app['TARGET'].apply(
                lambda x: 'REJECT' if x == 1 else 'APPROVE'
            )
            
            result = result.dropna()
            result = result[(result['revenue'] > 0)]
            
            print(f"✅ Converted {len(result)} Home Credit records")
            return result
        
        except Exception as e:
            print(f"❌ Error reading Home Credit data: {e}")
            return None
    
    @staticmethod
    def from_german_credit(csv_path):
        """
        Convert German Credit Dataset (classic credit scoring dataset).
        
        Download from: https://archive.ics.uci.edu/ml/datasets/Statlog+(German+Credit+Data)
        """
        try:
            # German Credit Data structure
            df = pd.read_csv(csv_path, sep=' ', header=None)
            
            result = pd.DataFrame()
            
            # Revenue = credit amount (column 4)
            result['revenue'] = df[4].fillna(5000)
            
            # Net profit = estimated monthly income (column 18) * 12 * 0.25
            result['net_profit'] = df[18].fillna(2000) * 12 * 0.25
            
            # Debt-to-equity = credit / annual income
            result['debt_to_equity'] = (
                df[4].fillna(5000) / (df[18].fillna(2000) * 12)
            ).clip(0, 5)
            
            # Fraud score based on account status
            fraud_score = (df[0].apply(lambda x: 50 if x == 'A11' else 20)).fillna(20)
            result['fraud_score'] = fraud_score
            
            # Average balance estimate
            result['avg_balance'] = df[4].fillna(5000) * 0.3
            
            # Label (last column is target: 1 = good, 2 = bad)
            result['expected_decision'] = df[df.columns[-1]].apply(
                lambda x: 'APPROVE' if x == 1 else 'REJECT'
            )
            
            result = result.dropna()
            
            print(f"✅ Converted {len(result)} German Credit records")
            return result
        
        except Exception as e:
            print(f"❌ Error reading German Credit data: {e}")
            return None


def generate_sample_data(num_records=100):
    """
    Generate synthetic financial data for testing.
    Useful if you don't have real data yet.
    """
    np.random.seed(42)
    
    # Generate synthetic but realistic data
    revenues = np.random.lognormal(mean=12, sigma=2, size=num_records)  # Log-normal distribution
    net_profits = revenues * np.random.uniform(0.05, 0.25, num_records)
    debt_to_equity = np.random.uniform(0.1, 3.0, num_records)
    fraud_scores = np.random.beta(2, 5, num_records) * 100  # Beta distribution
    avg_balances = revenues * np.random.uniform(0.2, 0.5, num_records)
    
    # Approve if: good profit margin, low debt, low fraud score
    decisions = []
    for i in range(num_records):
        profit_margin = net_profits[i] / revenues[i]
        d2e = debt_to_equity[i]
        fraud = fraud_scores[i]
        score = 0
        
        if profit_margin > 0.15: score += 30
        elif profit_margin > 0.05: score += 15
        
        if d2e < 1: score += 30
        elif d2e < 2: score += 15
        
        if fraud < 30: score += 25
        elif fraud < 60: score += 10
        
        decisions.append('APPROVE' if score >= 40 else 'REJECT')
    
    df = pd.DataFrame({
        'revenue': revenues,
        'net_profit': net_profits,
        'debt_to_equity': debt_to_equity,
        'fraud_score': fraud_scores,
        'avg_balance': avg_balances,
        'expected_decision': decisions
    })
    
    print(f"✅ Generated {num_records} synthetic records")
    return df


def main():
    print("Financial Data Converter")
    print("=" * 70)
    
    output_dir = Path('credit_engine/data')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    converter = FinancialDataConverter()
    
    # Option 1: Generate synthetic data (for testing)
    print("\n1️⃣ Generating synthetic data (for quick testing)...")
    df_synthetic = generate_sample_data(500)
    output_synthetic = output_dir / 'labeled_scorer_data_synthetic.csv'
    df_synthetic.to_csv(output_synthetic, index=False)
    print(f"   Saved to: {output_synthetic}\n")
    
    # Option 2: Load from LendingClub (if you have it downloaded)
    lending_club_path = Path('labeled_data.csv')  # Adjust path if needed
    if lending_club_path.exists():
        print("\n2️⃣ Converting LendingClub data...")
        df_lc = converter.from_lending_club(str(lending_club_path))
        if df_lc is not None:
            output_lc = output_dir / 'labeled_scorer_data_lending_club.csv'
            df_lc.to_csv(output_lc, index=False)
            print(f"   Saved to: {output_lc}\n")
    else:
        print("\n2️⃣ LendingClub data not found (download from Kaggle)")
        print("   Link: https://www.kaggle.com/datasets/wordsforthewise/lending-club\n")
    
    print("=" * 70)
    print("Next steps:")
    print("1. Choose a dataset to use (synthetic or download real data from Kaggle)")
    print("2. Copy the output CSV to: credit_engine/data/labeled_scorer_data.csv")
    print("3. Run: python credit_engine/train_scorer.py")
    print("4. Check accuracy improvements!")


if __name__ == "__main__":
    main()
