"""
Quick reference for SEC 10-K extraction.
How to use the SEC data extraction pipeline.
"""

# ============================================================================
# STEP 1: Install required dependencies
# ============================================================================
# pip install requests pandas numpy

# ============================================================================
# STEP 2: Find Company CIK Numbers
# ============================================================================
# Go to: https://www.sec.gov/cgi-bin/browse-edgar
# Search for a company name and get its CIK number

# Examples of popular company CIKs:
SEC_CIK_EXAMPLES = {
    # Tech
    '0000789019': 'Microsoft',
    '0001018724': 'Amgen',
    '0000051143': 'Apple',
    '0001652044': 'Alphabet (Google)',
    
    # Finance
    '0000064670': 'Goldman Sachs',
    '0000072741': 'JPMorgan Chase',
    
    # Energy
    '0000034088': 'Chevron',
    '0000108772': 'Exxon Mobil',
    
    # Consumer
    '0000866787': 'Walmart',
    '0001147149': 'Tesla',
    
    # Healthcare
    '0000040545': 'Johnson & Johnson',
    '0001125228': 'Moderna',
}

# ============================================================================
# STEP 3: Run the extraction
# ============================================================================
# Option A: Use default sample companies
# $ python extract_sec_data.py

# Option B: Customize with your own companies
# Edit extract_sec_data.py and replace the 'companies' dict in create_sample_sec_dataset()

# ============================================================================
# STEP 4: Output
# ============================================================================
# Creates: credit_engine/data/labeled_scorer_data_sec.csv
# With columns: revenue, net_profit, debt_to_equity, fraud_score, 
#               avg_balance, expected_decision

# ============================================================================
# STEP 5: Train your model with new data
# ============================================================================
# Copy the output to your training data:
# $ python -c "
# import pandas as pd
# df_sec = pd.read_csv('credit_engine/data/labeled_scorer_data_sec.csv')
# df_orig = pd.read_csv('credit_engine/data/labeled_scorer_data.csv')
# df_combined = pd.concat([df_orig, df_sec], ignore_index=True)
# df_combined.to_csv('credit_engine/data/labeled_scorer_data.csv', index=False)
# print(f'Combined dataset: {len(df_combined)} records')
# "

# Then retrain:
# $ python credit_engine/train_scorer.py
# $ python credit_engine/train_ensemble.py

print(__doc__)
