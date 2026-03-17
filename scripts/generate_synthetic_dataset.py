#!/usr/bin/env python3
"""
Synthetic LendingClub Dataset Generator
Creates realistic LendingClub-like data when direct download fails
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

def generate_synthetic_lendingclub(n_samples=5000, random_state=42):
    """Generate synthetic LendingClub-like dataset"""
    np.random.seed(random_state)
    
    print(f"   Generating {n_samples:,} synthetic LendingClub records...")
    
    # Generate realistic distributions
    annual_inc = np.random.lognormal(10.5, 0.8, n_samples)  # Income distribution
    loan_amnt = np.random.lognormal(9.5, 1.2, n_samples)    # Loan amount
    dti = np.random.beta(2, 10, n_samples) * 50             # Debt-to-income ratio
    delinq_2yrs = np.random.poisson(0.3, n_samples)         # Delinquencies
    
    # Loan status with realistic distribution (70% good, 30% bad)
    loan_status = np.random.choice(
        ['Fully Paid', 'Current', 'Default', 'Charged Off'],
        p=[0.45, 0.25, 0.20, 0.10],
        size=n_samples
    )
    
    # Create dataframe
    df = pd.DataFrame({
        'annual_inc': annual_inc.clip(0, None),
        'loan_amnt': loan_amnt.clip(0, None),
        'dti': dti.clip(0, 100),
        'delinq_2yrs': delinq_2yrs.astype(int),
        'loan_status': loan_status,
        'emp_length': np.random.uniform(0, 60, n_samples),
        'home_ownership': np.random.choice(['RENT', 'OWN', 'MORTGAGE', 'OTHER'], n_samples),
        'grade': np.random.choice(['A', 'B', 'C', 'D', 'E', 'F', 'G'], n_samples, p=[0.15, 0.25, 0.25, 0.20, 0.10, 0.03, 0.02]),
    })
    
    return df

def transform_to_schema(df_raw):
    """Transform to credit scoring schema"""
    transformed = pd.DataFrame()
    
    transformed['revenue'] = df_raw['annual_inc'].fillna(0)
    transformed['net_profit'] = (df_raw['loan_amnt'].fillna(0) * 0.1)
    transformed['debt_to_equity'] = (df_raw['dti'].fillna(0) / 100).clip(0, 10)
    transformed['fraud_score'] = (df_raw['delinq_2yrs'].fillna(0) * 15).clip(0, 100)
    transformed['avg_balance'] = (df_raw['loan_amnt'].fillna(0) / 12)
    
    # Map loan status
    status_mapping = {
        'Fully Paid': 'APPROVE', 
        'Current': 'APPROVE',
        'Default': 'REJECT',
        'Charged Off': 'REJECT'
    }
    transformed['expected_decision'] = df_raw['loan_status'].map(status_mapping).fillna('REJECT')
    
    return transformed

def main():
    print("""
╔════════════════════════════════════════════════════════════════════════╗
║    SYNTHETIC LENDINGCLUB DATASET GENERATOR                            ║
║    Creates realistic credit data when direct download unavailable     ║
╚════════════════════════════════════════════════════════════════════════╝
    """)
    
    print("\n📊 Step 1: Generating synthetic LendingClub dataset...")
    
    # Generate full dataset
    df_raw = generate_synthetic_lendingclub(n_samples=5000, random_state=42)
    print(f"   ✅ Generated synthetic data: {df_raw.shape}")
    
    # Transform
    print("\n🔄 Step 2: Transforming to credit schema...")
    transformed = transform_to_schema(df_raw)
    
    # Quality checks
    numeric_cols = ['revenue', 'net_profit', 'debt_to_equity', 'avg_balance']
    initial_len = len(transformed)
    transformed = transformed[~(transformed[numeric_cols] == 0).all(axis=1)]
    
    print(f"   ✅ Transformed: {len(transformed):,} records (removed {initial_len - len(transformed)} empty rows)")
    
    # Save datasets
    print("\n💾 Step 3: Saving datasets...")
    
    dataset_dir = Path(__file__).parent.parent / "Dataset"
    dataset_dir.mkdir(parents=True, exist_ok=True)
    
    # Full dataset
    full_path = dataset_dir / "lendingclub_full.csv"
    transformed.to_csv(full_path, index=False)
    print(f"   ✓ lendingclub_full.csv ({len(transformed):,} samples)")
    
    # 1000 samples
    sample_1k = transformed.sample(n=min(1000, len(transformed)), random_state=42)
    sample_1k_path = dataset_dir / "lendingclub_1000_samples.csv"
    sample_1k.to_csv(sample_1k_path, index=False)
    print(f"   ✓ lendingclub_1000_samples.csv (1,000 samples)")
    
    # 2000 samples
    sample_2k = transformed.sample(n=min(2000, len(transformed)), random_state=42)
    sample_2k_path = dataset_dir / "lendingclub_2000_samples.csv"
    sample_2k.to_csv(sample_2k_path, index=False)
    print(f"   ✓ lendingclub_2000_samples.csv (2,000 samples)")
    
    # Report
    print("\n📊 Step 4: Dataset Summary...")
    
    approve_count = (transformed['expected_decision'] == 'APPROVE').sum()
    reject_count = (transformed['expected_decision'] == 'REJECT').sum()
    
    report = f"""
═══════════════════════════════════════════════════════════════════════
                  LENDINGCLUB SYNTHETIC DATASET REPORT
═══════════════════════════════════════════════════════════════════════

📊 DATASET STATISTICS
─────────────────────────────────────────────────────────────────────
Total Samples:              {len(transformed):,}
Approved Records:           {approve_count:,} ({approve_count/len(transformed)*100:.1f}%)
Rejected Records:           {reject_count:,} ({reject_count/len(transformed)*100:.1f}%)

Generated Datasets:
  • lendingclub_full.csv              {len(transformed):,} samples
  • lendingclub_1000_samples.csv      1,000 samples
  • lendingclub_2000_samples.csv      2,000 samples

📈 FEATURE STATISTICS
─────────────────────────────────────────────────────────────────────
Revenue (annual_inc):
  Mean:    ${transformed['revenue'].mean():,.0f}
  Median:  ${transformed['revenue'].median():,.0f}
  Std:     ${transformed['revenue'].std():,.0f}

Debt-to-Equity Ratio:
  Mean:    {transformed['debt_to_equity'].mean():.2f}
  Median:  {transformed['debt_to_equity'].median():.2f}
  Max:     {transformed['debt_to_equity'].max():.2f}

Fraud Score:
  Mean:    {transformed['fraud_score'].mean():.1f}
  Median:  {transformed['fraud_score'].median():.1f}
  Max:     {transformed['fraud_score'].max():.1f}

═══════════════════════════════════════════════════════════════════════
Generated Report: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Location: Dataset/
Data Type: Synthetic (realistic distributions for model training)
═══════════════════════════════════════════════════════════════════════
    """
    
    print(report)
    
    report_path = dataset_dir / "lendingclub_integration_report.txt"
    with open(report_path, 'w') as f:
        f.write(report)
    
    print("\n✅ Synthetic Dataset Generation Complete!")
    print(f"\n📁 Datasets saved to: {dataset_dir}")
    print("\nNext Steps:")
    print("1. Run: python credit_engine/train_ensemble_lc.py")
    print("2. Update model path in credit_engine/src/scorer.py")
    print("3. Restart API server for new model")
    
    return True

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
