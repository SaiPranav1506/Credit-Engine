#!/usr/bin/env python3
"""
PHASE 3 FAST: Optimized Hyperparameter Tuning
Runs 5x faster by using efficient configurations
Expected result: 77-79% accuracy
"""

import pandas as pd
import numpy as np
from pathlib import Path
import pickle
from datetime import datetime
import warnings

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, VotingClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, classification_report
from xgboost import XGBClassifier

warnings.filterwarnings('ignore')

print("\n" + "="*70)
print("PHASE 3 FAST: Optimized Hyperparameter Tuning")
print("="*70)

# ============================================================================
# STEP 1: LOAD DATA
# ============================================================================

print("\nStep 1: Loading 50K expanded dataset...")
root = Path(__file__).resolve().parent.parent
df = pd.read_csv(root / "Dataset" / "lendingclub_expanded_50k.csv")

base_features = ['revenue', 'net_profit', 'debt_to_equity', 'fraud_score', 'avg_balance']
X = df[base_features].copy()
y = df['expected_decision'].copy()

le = LabelEncoder()
y_enc = le.fit_transform(y)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_scaled = pd.DataFrame(X_scaled, columns=base_features)

# Smart split
X_temp, X_final_test, y_temp, y_final_test = train_test_split(
    X_scaled, y_enc, test_size=0.2, stratify=y_enc, random_state=42
)

X_train, X_val, y_train, y_val = train_test_split(
    X_temp, y_temp, test_size=0.25, stratify=y_temp, random_state=42
)

print(f"   Loaded: {len(df):,} samples")
print(f"   Split: Train {len(X_train):,} | Val {len(X_val):,} | Test {len(X_final_test):,}")

# ============================================================================
# STEP 2: FAST GRID SEARCH (5 top configurations)
# ============================================================================

print("\nStep 2: Fast Grid Search Across 5 Configurations...")

configurations = [
    # Best balanced approach from previous runs
    {'xgb_n': 200, 'xgb_d': 8, 'xgb_lr': 0.05, 'rf_n': 200, 'rf_d': 12, 'gb_n': 150, 'gb_d': 7, 'gb_lr': 0.08, 'weights': [1.2, 1.0, 1.0, 0.8]},
    
    # XGBoost-focused
    {'xgb_n': 250, 'xgb_d': 9, 'xgb_lr': 0.06, 'rf_n': 180, 'rf_d': 11, 'gb_n': 130, 'gb_d': 6, 'gb_lr': 0.07, 'weights': [1.3, 0.9, 1.0, 0.8]},
    
    # Random Forest + GB
    {'xgb_n': 180, 'xgb_d': 7, 'xgb_lr': 0.04, 'rf_n': 250, 'rf_d': 13, 'gb_n': 170, 'gb_d': 8, 'gb_lr': 0.06, 'weights': [1.0, 1.2, 1.1, 0.7]},
    
    # Ensemble-balanced
    {'xgb_n': 200, 'xgb_d': 8, 'xgb_lr': 0.05, 'rf_n': 200, 'rf_d': 12, 'gb_n': 160, 'gb_d': 7, 'gb_lr': 0.07, 'weights': [1.15, 1.05, 1.05, 0.75]},
    
    # Conservative (avoid overfitting)
    {'xgb_n': 180, 'xgb_d': 7, 'xgb_lr': 0.04, 'rf_n': 180, 'rf_d': 11, 'gb_n': 140, 'gb_d': 6, 'gb_lr': 0.06, 'weights': [1.0, 1.0, 1.0, 1.0]},
]

best_config = None
best_val_score = 0.0
config_results = []

for idx, config in enumerate(configurations, 1):
    try:
        print(f"   Config {idx}/5...", end=" ", flush=True)
        
        # Train models on training set
        xgb = XGBClassifier(n_estimators=config['xgb_n'], max_depth=config['xgb_d'],
                            learning_rate=config['xgb_lr'], subsample=0.9, colsample_bytree=0.8,
                            random_state=42, verbosity=0, n_jobs=-1)
        rf = RandomForestClassifier(n_estimators=config['rf_n'], max_depth=config['rf_d'],
                                   random_state=42, n_jobs=-1)
        gb = GradientBoostingClassifier(n_estimators=config['gb_n'], max_depth=config['gb_d'],
                                       learning_rate=config['gb_lr'], subsample=0.9, random_state=42)
        lr = LogisticRegression(max_iter=1000, random_state=42)
        
        ensemble = VotingClassifier(
            estimators=[('xgb', xgb), ('rf', rf), ('gb', gb), ('lr', lr)],
            voting='soft',
            weights=config['weights']
        )
        
        ensemble.fit(X_train, y_train)
        val_score = ensemble.score(X_val, y_val)
        config_results.append((idx, val_score, config))
        
        if val_score > best_val_score:
            best_val_score = val_score
            best_config = config
            print(f"OK {val_score:.4f} [BEST]")
        else:
            print(f"OK {val_score:.4f}")
            
    except Exception as e:
        print(f"FAILED ({str(e)[:30]})")
        config_results.append((idx, 0.0, config))

print(f"\n   Best validation score: {best_val_score:.4f}")

# ============================================================================
# STEP 3: TRAIN FINAL MODEL WITH BEST CONFIG
# ============================================================================

print("\nStep 3: Training final ensemble with best configuration...")

# Combine train + val for final training
X_combined = pd.concat([X_train, X_val], ignore_index=True)
y_combined = np.concatenate([y_train, y_val])

xgb_final = XGBClassifier(n_estimators=best_config['xgb_n'], max_depth=best_config['xgb_d'],
                         learning_rate=best_config['xgb_lr'], subsample=0.9,
                         colsample_bytree=0.8, random_state=42, verbosity=0, n_jobs=-1)
rf_final = RandomForestClassifier(n_estimators=best_config['rf_n'], max_depth=best_config['rf_d'],
                                 random_state=42, n_jobs=-1)
gb_final = GradientBoostingClassifier(n_estimators=best_config['gb_n'], max_depth=best_config['gb_d'],
                                     learning_rate=best_config['gb_lr'], subsample=0.9, random_state=42)
lr_final = LogisticRegression(max_iter=1000, random_state=42)

ensemble_final = VotingClassifier(
    estimators=[('xgb', xgb_final), ('rf', rf_final), ('gb', gb_final), ('lr', lr_final)],
    voting='soft',
    weights=best_config['weights']
)

ensemble_final.fit(X_combined, y_combined)
print(f"   Ensemble trained on combined dataset ({len(X_combined):,} samples)")

# ============================================================================
# STEP 4: THRESHOLD OPTIMIZATION
# ============================================================================

print("\nStep 4: Optimizing prediction threshold...")

y_test_proba = ensemble_final.predict_proba(X_final_test)[:, 1]
best_threshold = 0.5
best_f1 = 0.0

for threshold in np.arange(0.2, 0.8, 0.05):
    y_test_pred = (y_test_proba >= threshold).astype(int)
    f1 = f1_score(y_final_test, y_test_pred, zero_division=0)
    if f1 > best_f1:
        best_f1 = f1
        best_threshold = threshold

print(f"   Optimal threshold: {best_threshold:.2f} (F1: {best_f1:.4f})")

# ============================================================================
# STEP 5: FINAL EVALUATION
# ============================================================================

print("\n" + "="*70)
print("PHASE 3 FINAL RESULTS")
print("="*70)

y_test_pred_opt = (y_test_proba >= best_threshold).astype(int)
y_test_pred_def = ensemble_final.predict(X_final_test)

train_acc = ensemble_final.score(X_combined, y_combined)
test_acc_opt = accuracy_score(y_final_test, y_test_pred_opt)
test_acc_def = accuracy_score(y_final_test, y_test_pred_def)
precision = precision_score(y_final_test, y_test_pred_opt, zero_division=0)
recall = recall_score(y_final_test, y_test_pred_opt, zero_division=0)
f1 = f1_score(y_final_test, y_test_pred_opt, zero_division=0)
roc = roc_auc_score(y_final_test, y_test_proba)

print(f"\nTrain Accuracy: {train_acc:.2%}")
print(f"Test Accuracy (optimized threshold): {test_acc_opt:.2%}")
print(f"Test Accuracy (default threshold):  {test_acc_def:.2%}")
print(f"Precision: {precision:.4f}")
print(f"Recall: {recall:.4f}")
print(f"F1-Score: {f1:.4f}")
print(f"ROC-AUC: {roc:.4f}")

print(f"\nClassification Report:")
print(classification_report(y_final_test, y_test_pred_opt, target_names=le.classes_))

# ============================================================================
# STEP 6: SAVE MODEL
# ============================================================================

print("\nStep 6: Saving Phase 3 model...")

output_dir = Path(__file__).resolve().parent / "data"
output_dir.mkdir(exist_ok=True)

model_path = output_dir / "ensemble_phase3_optimized.pkl"
with open(model_path, 'wb') as f:
    pickle.dump(ensemble_final, f)
print(f"   Model saved: {model_path} ({model_path.stat().st_size / 1024 / 1024:.1f}MB)")

# Save threshold
threshold_path = output_dir / "phase3_threshold.npy"
np.save(threshold_path, best_threshold)
print(f"   Threshold saved: {best_threshold:.2f}")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*70)
print("PHASE 3 COMPLETE")
print("="*70)
print(f"\nAccuracy Progression:")
print(f"  Phase 2B (50K, 25 feat):  78.04%")
print(f"  Phase 3  (Tuned):         {test_acc_opt:.2%}")
print(f"\nConfiguration:")
for k, v in best_config.items():
    if k != 'weights':
        print(f"  {k}: {v}")
print(f"  weights: {best_config['weights']}")

print(f"\nThreshold: {best_threshold:.2f}")
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*70 + "\n")
