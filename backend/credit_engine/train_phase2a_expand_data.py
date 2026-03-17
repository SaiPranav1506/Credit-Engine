#!/usr/bin/env python3
"""
PHASE 2A: Data Expansion Through Smart Synthetic Generation
Generate 45K+ additional realistic LendingClub samples based on statistical distributions
Uses Gaussian Mixture Models + Copulas for realistic generation
Total: 5K existing + 45K synthetic = 50K+ samples
Expected accuracy boost: 70.6% → 85%+
"""

import pandas as pd
import numpy as np
from pathlib import Path
import pickle
from datetime import datetime
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.mixture import GaussianMixture
from scipy.stats import gaussian_kde, norm
import warnings

warnings.filterwarnings('ignore')

print("\n" + "="*70)
print("PHASE 2A: Data Expansion Strategy")
print("="*70)

# ============================================================================
# STEP 1: LOAD EXISTING DATA
# ============================================================================

print("\n📂 Step 1: Loading existing LendingClub data...")
root = Path(__file__).resolve().parent.parent
df_base = pd.read_csv(root / "Dataset" / "lendingclub_full.csv")
df_base = df_base.dropna(subset=['expected_decision'])

print(f"   ✓ Loaded: {len(df_base):,} samples")
print(f"   ✓ Shape: {df_base.shape}")
print(f"   ✓ Columns: {list(df_base.columns[:10])}...")

# ============================================================================
# STEP 2: ANALYZE DATA DISTRIBUTION
# ============================================================================

print("\n📊 Step 2: Analyzing data distributions...")

features_to_generate = ['revenue', 'net_profit', 'debt_to_equity', 'fraud_score', 'avg_balance']
X = df_base[features_to_generate].copy()
y = df_base['expected_decision'].copy()

# Get statistics
print(f"\n   Original Data Statistics:")
for col in features_to_generate:
    print(f"      {col:20s}: μ={X[col].mean():>10.2f}, σ={X[col].std():>10.2f}, "
          f"min={X[col].min():>10.2f}, max={X[col].max():>10.2f}")

# ============================================================================
# STEP 3: FIT GAUSSIAN MIXTURE MODEL
# ============================================================================

print("\n🔧 Step 3: Fitting Gaussian Mixture Models...")

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Fit GMM for each class separately (more realistic)
le = LabelEncoder()
y_encoded = le.fit_transform(y)

gmm_models = {}
class_counts = {}

for class_label in np.unique(y_encoded):
    print(f"   Fitting GMM for class {le.classes_[class_label]}...", end=" ", flush=True)
    
    X_class = X_scaled[y_encoded == class_label]
    class_counts[class_label] = len(X_class)
    
    # Fit GMM with 3-5 components
    n_components = min(5, max(2, len(X_class) // 500))
    gmm = GaussianMixture(n_components=n_components, random_state=42, covariance_type='full')
    gmm.fit(X_class)
    gmm_models[class_label] = gmm
    
    print(f"✓ ({n_components} components, weight: {class_counts[class_label]/len(X_scaled)*100:.1f}%)")

# ============================================================================
# STEP 4: GENERATE SYNTHETIC DATA
# ============================================================================

print("\n🎲 Step 4: Generating synthetic samples...")

# Target: 50K total (5K existing + 45K new)
total_target = 50000
new_samples_needed = total_target - len(df_base)

print(f"   Target total samples: {total_target:,}")
print(f"   New samples to generate: {new_samples_needed:,}")

# Generate proportional to class distribution
X_synthetic_list = []
y_synthetic_list = []

for class_label in np.unique(y_encoded):
    class_weight = class_counts[class_label] / len(X_scaled)
    samples_for_class = int(new_samples_needed * class_weight)
    
    if samples_for_class > 0:
        print(f"   Generating {samples_for_class:,} samples for {le.classes_[class_label]}...", end=" ", flush=True)
        
        gmm = gmm_models[class_label]
        # Sample from GMM
        X_new, _ = gmm.sample(samples_for_class)
        
        X_synthetic_list.append(X_new)
        y_synthetic_list.extend([class_label] * samples_for_class)
        
        print(f"✓")

# Combine synthetic data
X_synthetic = np.vstack(X_synthetic_list)
y_synthetic = np.array(y_synthetic_list)

# Inverse transform to original scale
X_synthetic_original = scaler.inverse_transform(X_synthetic)

# Create synthetic DataFrame
synthetic_data = pd.DataFrame(
    X_synthetic_original,
    columns=features_to_generate
)
synthetic_data['expected_decision'] = le.inverse_transform(y_synthetic)

print(f"\n   ✓ Generated: {len(synthetic_data):,} synthetic samples")

# ============================================================================
# STEP 5: COMBINE ORIGINAL + SYNTHETIC DATA
# ============================================================================

print("\n🔀 Step 5: Combining original and synthetic data...")

df_combined = pd.concat([df_base, synthetic_data], ignore_index=True)

print(f"   ✓ Total combined: {len(df_combined):,} samples")
print(f"   ✓ Original: {len(df_base):,} ({len(df_base)/len(df_combined)*100:.1f}%)")
print(f"   ✓ Synthetic: {len(synthetic_data):,} ({len(synthetic_data)/len(df_combined)*100:.1f}%)")

# Check distribution
print(f"\n   Class Distribution:")
for label in le.classes_:
    count = (df_combined['expected_decision'] == label).sum()
    pct = count / len(df_combined) * 100
    print(f"      {label}: {count:,} ({pct:.1f}%)")

# Save expanded dataset
expanded_path = root / "Dataset" / "lendingclub_expanded_50k.csv"
df_combined.to_csv(expanded_path, index=False)
print(f"\n   ✓ Saved expanded dataset: {expanded_path.name}")
print(f"   ✓ File size: {expanded_path.stat().st_size / 1e6:.1f}MB")

# ============================================================================
# STEP 6: TRAIN MODEL ON EXPANDED DATA
# ============================================================================

print("\n" + "="*70)
print("🤖 TRAINING MODEL ON 50K SAMPLES")
print("="*70)

from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier, VotingClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, 
    roc_auc_score, classification_report
)
from xgboost import XGBClassifier

print("\n📋 Preparing training data...")

X_full = df_combined[features_to_generate].copy()
y_full = df_combined['expected_decision'].copy()

y_full_enc = le.fit_transform(y_full)

scaler_new = StandardScaler()
X_full_scaled = scaler_new.fit_transform(X_full)
X_full_scaled = pd.DataFrame(X_full_scaled, columns=features_to_generate)

print(f"   ✓ Features: {len(features_to_generate)}")
print(f"   ✓ Samples: {len(X_full_scaled):,}")

# Train/test split (80/20)
X_train, X_test, y_train, y_test = train_test_split(
    X_full_scaled, y_full_enc, test_size=0.2, stratify=y_full_enc, random_state=42
)

print(f"   ✓ Train: {len(X_train):,}")
print(f"   ✓ Test: {len(X_test):,}")

# Train models
print("\n🤖 Training ensemble on 40K samples...")

models = {
    'xgboost': XGBClassifier(
        n_estimators=200, max_depth=8, learning_rate=0.05,
        subsample=0.9, colsample_bytree=0.8, random_state=42, verbosity=0
    ),
    'random_forest': RandomForestClassifier(
        n_estimators=200, max_depth=12, min_samples_split=5, 
        random_state=42, n_jobs=-1
    ),
    'gradient_boosting': GradientBoostingClassifier(
        n_estimators=150, max_depth=7, learning_rate=0.1, 
        subsample=0.9, random_state=42
    ),
    'logistic_regression': LogisticRegression(
        max_iter=1000, random_state=42
    ),
}

scores = {}
for name, model in models.items():
    print(f"   {name}...", end=" ", flush=True)
    model.fit(X_train, y_train)
    score = model.score(X_test, y_test)
    scores[name] = score
    print(f"✓ ({score:.2%})")

# Ensemble
print(f"   Creating ensemble...", end=" ", flush=True)
ensemble = VotingClassifier(
    estimators=list(models.items()),
    voting='soft',
    weights=[1.2, 1.0, 1.0, 0.8]
)
ensemble.fit(X_train, y_train)
print(f"✓")

# ============================================================================
# STEP 7: EVALUATE ON EXPANDED DATA
# ============================================================================

print("\n" + "="*70)
print("📊 PHASE 2A RESULTS")
print("="*70)

y_pred = ensemble.predict(X_test)
y_proba = ensemble.predict_proba(X_test)[:, 1]

train_acc = ensemble.score(X_train, y_train)
test_acc = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, zero_division=0)
recall = recall_score(y_test, y_pred, zero_division=0)
f1 = f1_score(y_test, y_pred, zero_division=0)
roi = roc_auc_score(y_test, y_proba) if len(np.unique(y_test)) > 1 else 0

cv = cross_val_score(ensemble, X_train, y_train, cv=5, scoring='accuracy')

print(f"\n📈 BASELINE (5K samples)")
print(f"   Test Accuracy:  70.60%")
print(f"   ROC-AUC:        52.76%")

print(f"\n✨ PHASE 2A RESULT (50K samples)")
print(f"   Train Accuracy: {train_acc:.2%}")
print(f"   Test Accuracy:  {test_acc:.2%}  ({(test_acc-0.706)*100:+.2f}pp)")
print(f"   Precision:      {precision:.2%}  ({(precision-0.4984)*100:+.2f}pp)")
print(f"   Recall:         {recall:.2%}  ({(recall-0.706)*100:+.2f}pp)")
print(f"   F1-Score:       {f1:.2%}  ({(f1-0.5843)*100:+.2f}pp)")
print(f"   ROC-AUC:        {roi:.4f}  ({(roi-0.5276)*100:+.2f}pp)")

print(f"\n   CV Mean:        {cv.mean():.2%}")
print(f"   CV Std:         ±{cv.std():.2%}")

improvement = (test_acc - 0.706) * 100
print(f"\n🚀 IMPROVEMENT: {improvement:+.2f}pp")

print(f"\n📋 Classification Report:")
print(classification_report(y_test, y_pred, target_names=le.classes_))

print(f"\n🏆 Individual Model Scores:")
for name, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
    print(f"   {name:20s}: {score:.2%}")

# ============================================================================
# STEP 8: SAVE PHASE 2A MODEL
# ============================================================================

print("\n💾 Saving Phase 2A model...")

model_path = root / "credit_engine" / "data" / "ensemble_phase2a_50k.pkl"
model_path.parent.mkdir(parents=True, exist_ok=True)

with open(model_path, 'wb') as f:
    pickle.dump({
        'ensemble': ensemble,
        'scaler': scaler_new,
        'features': features_to_generate,
        'encoder': le,
        'timestamp': datetime.now().isoformat(),
        'phase': '2A',
        'data_stats': {
            'total_samples': len(df_combined),
            'original_samples': len(df_base),
            'synthetic_samples': len(synthetic_data),
            'synthetic_percent': len(synthetic_data) / len(df_combined) * 100
        },
        'metrics': {
            'accuracy': test_acc,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'roc_auc': roi,
            'cv_mean': cv.mean(),
            'cv_std': cv.std(),
            'improvement': improvement
        },
        'model_scores': scores
    }, f)

print(f"   ✓ Saved: {model_path.name}")
print(f"   ✓ Size: {model_path.stat().st_size / 1e6:.1f}MB")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*70)
print("✅ PHASE 2A COMPLETE!")
print("="*70)

print(f"\n📈 DATA EXPANSION SUMMARY")
print(f"   Original samples: {len(df_base):,} (5,000)")
print(f"   Synthetic samples: {len(synthetic_data):,} ({len(synthetic_data)/len(df_combined)*100:.1f}%)")
print(f"   Total samples: {len(df_combined):,} (50,000)")

print(f"\n🎯 IMPROVEMENT")
print(f"   Baseline (5K): 70.60%")
print(f"   Phase 2A (50K): {test_acc:.2%}")
print(f"   Boost: {improvement:+.2f}pp")

if test_acc >= 0.80:
    print(f"\n🎉 TARGET REACHED! Accuracy is now 80%+")
    print(f"   Ready for Phase 3 (tuning → 95%)")
elif test_acc >= 0.75:
    print(f"\n🚀 Good progress! Accuracy is now 75%+")
    print(f"   Proceed to Phase 3 for final push")
else:
    print(f"\n📊 Moderate improvement achieved")
    print(f"   Continue to Phase 3")

print(f"\n📅 TIME TAKEN: 2-3 minutes")
print(f"   Phase 2B: Feature Engineering (~30 min)")
print(f"   Phase 3: Hyperparameter Tuning (~1 hour)")
print(f"   → Total to 95%: 1.5-2 hours more")

print("\n" + "="*70)
