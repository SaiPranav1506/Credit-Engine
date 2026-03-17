#!/usr/bin/env python3
"""
LendingClub Dataset Setup - Alternative Download Method
Downloads via direct HTTP or subprocess CLI
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import warnings
import subprocess
import sys
import os

warnings.filterwarnings('ignore')

def main():
    print("""
╔════════════════════════════════════════════════════════════════════════╗
║    LENDINGCLUB DATASET SETUP & INTEGRATION (Alternative Method)       ║
║    Downloads, transforms, and prepares data for model training        ║
╚════════════════════════════════════════════════════════════════════════╝
    """)
    
    print("\n📥 Step 1: Downloading LendingClub dataset...")
    print("   Using Kaggle CLI...")
    
    temp_dir = Path("./temp_lendingclub")
    temp_dir.mkdir(exist_ok=True)
    
    # Read credentials
    kaggle_config = Path.home() / ".kaggle" / "kaggle.json"
    if not kaggle_config.exists():
        print("❌ Kaggle credentials not found at:", kaggle_config)
        return False
    
    try:
        # Try using kaggle CLI via subprocess
        cmd = [
            sys.executable, "-m", "kaggle",
            "datasets", "download",
            "-d", "wordsforthewise/lending-club",
            "-p", str(temp_dir),
            "--unzip"
        ]
        
        print(f"   Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode != 0:
            print(f"❌ Download failed: {result.stderr}")
            return False
        
        print("   ✅ Download complete!")
        
    except Exception as e:
        print(f"❌ Download error: {e}")
        return False
    
    # Step 2: Load and transform data
    print("\n🔄 Step 2: Loading and transforming data...")
    
    csv_files = list(temp_dir.glob("*.csv"))
    if not csv_files:
        print("❌ No CSV files found in download")
        return False
    
    main_file = max(csv_files, key=lambda x: x.stat().st_size)
    print(f"   Loading: {main_file.name}")
    
    try:
        df_raw = pd.read_csv(main_file, low_memory=False)
        print(f"   Shape: {df_raw.shape}")
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return False
    
    # Transform to your schema
    print("   Transforming to your schema...")
    transformed = pd.DataFrame()
    
    transformed['revenue'] = df_raw['annual_inc'].fillna(0) if 'annual_inc' in df_raw.columns else 0
    transformed['net_profit'] = (df_raw['loan_amnt'].fillna(0) * 0.1) if 'loan_amnt' in df_raw.columns else 0
    
    if 'dti' in df_raw.columns:
        transformed['debt_to_equity'] = (df_raw['dti'].fillna(0) / 100).clip(0, 10)
    else:
        transformed['debt_to_equity'] = 0
    
    transformed['fraud_score'] = 0
    if 'delinq_2yrs' in df_raw.columns:
        transformed['fraud_score'] = (df_raw['delinq_2yrs'].fillna(0) * 15).clip(0, 100)
    
    transformed['avg_balance'] = (df_raw['loan_amnt'].fillna(0) / 12) if 'loan_amnt' in df_raw.columns else 0
    
    # Map loan status to decision
    if 'loan_status' in df_raw.columns:
        status_mapping = {
            'Fully Paid': 'APPROVE', 'Current': 'APPROVE', 'Issued': 'APPROVE',
            'In Grace Period': 'APPROVE',
            'Default': 'REJECT', 'Charged Off': 'REJECT',
            'Late (16-30 days)': 'REJECT', 'Late (31-120 days)': 'REJECT'
        }
        transformed['expected_decision'] = df_raw['loan_status'].map(status_mapping).fillna('REJECT')
    else:
        transformed['expected_decision'] = 'REJECT'
    
    # Clean empty rows
    numeric_cols = ['revenue', 'net_profit', 'debt_to_equity', 'avg_balance']
    initial_len = len(transformed)
    transformed = transformed[~(transformed[numeric_cols] == 0).all(axis=1)]
    
    print(f"   ✅ Transformed: {len(transformed):,} records (removed {initial_len - len(transformed)} empty rows)")
    
    # Step 3: Save datasets
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
    
    # Step 4: Create monitoring report
    print("\n📊 Step 4: Creating monitoring report...")
    
    approve_count = (transformed['expected_decision'] == 'APPROVE').sum()
    reject_count = (transformed['expected_decision'] == 'REJECT').sum()
    
    report = f"""
═══════════════════════════════════════════════════════════════════════
                    LENDINGCLUB INTEGRATION REPORT
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
═══════════════════════════════════════════════════════════════════════
    """
    
    print(report)
    
    # Save report
    report_path = dataset_dir / "lendingclub_integration_report.txt"
    with open(report_path, 'w') as f:
        f.write(report)
    
    # Step 5: Cleanup
    print("\n🧹 Step 5: Cleaning up temporary files...")
    import shutil
    try:
        shutil.rmtree(temp_dir)
        print("   ✅ Cleanup complete")
    except:
        print("   ⚠️  Could not remove temp directory (manual cleanup may be needed)")
    
    print("\n✅ LendingClub Dataset Integration Complete!")
    print(f"\n📁 Datasets saved to: {dataset_dir}")
    print("\nNext Steps:")
    print("1. Run: python credit_engine/train_ensemble_lc.py")
    print("2. Update model path in credit_engine/src/scorer.py")
    print("3. Restart API server for new model")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
