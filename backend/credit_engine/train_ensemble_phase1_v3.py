#!/usr/bin/env python3
"""
PHASE 1 v3: Better approach - Feature engineering + Class weights + No oversynthesis
The key insight: Don't force balance with SMOTE, use class_weight in models instead
"""

import pandas as pd
import numpy as np
from pathlib import Path
import pickle
from datetime import datetime

from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, VotingClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, 
    roc_auc_score, classification_report
)
from xgboost import XGBClassifier
import lightgbm as lgb
import warnings

warnings.filterwarnings('ignore')


def engineer_features(df):
    """Create 8 powerful financial features"""
    print("\n✨ Phase 1 Step 1: Feature Engineering...")
    
    df_eng = df.copy()
    
    # 1. Profitability Score
    profit_ratio = df_eng['net_profit'] / (df_eng['revenue'] + 1)
    df_eng['profit_score'] = np.where(profit_ratio > 0, profit_ratio * 100, -abs(profit_ratio) * 100).clip(-50, 100)
    
    # 2. Liquidity Strength
    df_eng['liquidity_strength'] = (df_eng['avg_balance'] / (df_eng['revenue'] + 1) * 100).clip(0, 100)
    
    # 3. Leverage Health  (lower debt is better)
    df_eng['leverage_health'] = (100 / (1 + df_eng['debt_to_equity'])).clip(0, 100)
    
    # 4. Risk Score (inverse of fraud score)
    df_eng['risk_level'] = (100 - df_eng['fraud_score']).clip(0, 100)
    
    # 5. Combined Financial Strength
    df_eng['financial_strength'] = (
        df_eng['profit_score'].clip(0, 100) * 0.3 +
        df_eng['liquidity_strength'] * 0.3 +
        df_eng['leverage_health'] * 0.2 +
        df_eng['risk_level'] * 0.2
    ).clip(0, 100)
    
    # 6. Debt Burden Adjusted
    df_eng['debt_burden_adj'] = (df_eng['debt_to_equity'] / (df_eng['revenue'] + 1) * 100).clip(0, 100)
    
    # 7. Revenue Stability Indicator (using variance proxy)
    df_eng['stability_score'] = np.where(
        df_eng['profit_score'] > 0,
        df_eng['financial_strength'] * 0.8 + 20,
        df_eng['financial_strength'] * 0.5
    ).clip(0, 100)
    
    # 8. Overall Credit Health Score
    df_eng['credit_health'] = (
        df_eng['financial_strength'] * 0.5 +
        df_eng['risk_level'] * 0.3 +
        (100 - df_eng['debt_burden_adj']) * 0.2
    ).clip(0, 100)
    
    # Clean
    for col in df_eng.columns:
        df_eng[col] = df_eng[col].replace([np.inf, -np.inf], 0).fillna(0)
    
    print(f"   ✓ Created 8 new risk/health features")
    return df_eng


def main():
    print("\n" + "="*70)
    print("PHASE 1 v3: Smart Boost via Features + Class Weights")
    print("="*70)
    
    # Load and prepare
    print("\n📂 Loading data...")
    root = Path(__file__).resolve().parent.parent
    df = pd.read_csv(root / "Dataset" / "lendingclub_full.csv")
    df = df.dropna(subset=['expected_decision'])
    print(f"   ✓ {len(df):,} samples loaded")
    
    # Engineer features
    df = engineer_features(df)
    
    # Prepare
    print("\n📋 Preparing data...")
    feature_cols = [
        'revenue', 'net_profit', 'debt_to_equity', 'fraud_score', 'avg_balance',
        'profit_score', 'liquidity_strength', 'leverage_health', 'risk_level',
        'financial_strength', 'debt_burden_adj', 'stability_score', 'credit_health'
    ]
    
    X = df[feature_cols].copy()
    y = df['expected_decision'].copy()
    
    le = LabelEncoder()
    y_enc = le.fit_transform(y)
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_scaled = pd.DataFrame(X_scaled, columns=feature_cols)
    
    # Split
    print(f"   ✓ {len(feature_cols)} features created")
    print(f"   ✓ {len(X_scaled):,} samples")
    
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y_enc, test_size=0.2, stratify=y_enc, random_state=42
    )
    print(f"   ✓ Train: {len(X_train):,} | Test: {len(X_test):,}")
    
    # Train ensemble WITH CLASS WEIGHTS (not SMOTE)
    print("\n🤖 Phase 1 Step 2: Training Ensemble with Class Weights...")
    
    models = {
        'xgboost': XGBClassifier(
            n_estimators=200,
            max_depth=8,
            learning_rate=0.08,
            subsample=0.9,
            colsample_bytree=0.85,
            min_child_weight=1,
            scale_pos_weight=sum(y_train == 0) / (sum(y_train == 1) + 1),
            random_state=42,
            verbosity=0
        ),
        'lightgbm': lgb.LGBMClassifier(
            n_estimators=200,
            max_depth=9,
            learning_rate=0.08,
            num_leaves=60,
            is_unbalance=True,
            min_child_samples=15,
            random_state=42,
            verbosity=-1
        ),
        'random_forest': RandomForestClassifier(
            n_estimators=200,
            max_depth=12,
            min_samples_split=4,
            class_weight='balanced',
            random_state=42,
            n_jobs=-1
        ),
        'gradient_boosting': GradientBoostingClassifier(
            n_estimators=150,
            max_depth=7,
            learning_rate=0.1,
            subsample=0.9,
            random_state=42
        ),
        'logistic_regression': LogisticRegression(
            max_iter=1000,
            class_weight='balanced',
            random_state=42
        )
    }
    
    print("   Training models...")
    scores = {}
    for name, model in models.items():
        print(f"      {name}...", end=" ", flush=True)
        model.fit(X_train, y_train)
        score = model.score(X_test, y_test)
        scores[name] = score
        print(f"✓ ({score:.2%})")
    
    # Ensemble
    print("   Creating soft voting ensemble...")
    ensemble = VotingClassifier(
        estimators=list(models.items()),
        voting='soft',
        weights=[1.2, 1.2, 1.0, 1.0, 0.9]
    )
    ensemble.fit(X_train, y_train)
    print("   ✓ Ensemble ready")
    
    # Evaluate
    print("\n" + "="*70)
    print("📊 RESULTS")
    print("="*70)
    
    y_pred = ensemble.predict(X_test)
    y_proba = ensemble.predict_proba(X_test)[:, 1]
    
    train_acc = ensemble.score(X_train, y_train)
    test_acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    roi = roc_auc_score(y_test, y_proba) if len(np.unique(y_test)) > 1 else 0
    
    cv = cross_val_score(ensemble, X_train, y_train, cv=5, scoring='accuracy')
    
    print(f"\n📈 BASELINE")
    print(f"   Test Accuracy: 70.60%")
    print(f"   ROC-AUC:       52.76%")
    
    print(f"\n✨ PHASE 1 RESULT")
    print(f"   Train Accuracy: {train_acc:.2%}")
    print(f"   Test Accuracy:  {test_acc:.2%}")
    print(f"   Precision:      {prec:.2%}")
    print(f"   Recall:         {rec:.2%}")
    print(f"   F1-Score:       {f1:.2%}")
    print(f"   ROC-AUC:        {roi:.4f}")
    
    print(f"\n   CV Mean:        {cv.mean():.2%}")
    print(f"   CV Std:         ±{cv.std():.2%}")
    
    imp = (test_acc - 0.706) * 100
    print(f"\n🚀 {'+' if imp > 0 else ''}{imp:+.2f}pp improvement")
    
    print(f"\n📋 Detailed:")
    print(classification_report(y_test, y_pred, target_names=le.classes_))
    
    print(f"\n🏆 Individual Model Scores:")
    for name, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
        print(f"   {name:20s}: {score:.2%}")
    
    # Save
    print("\n💾 Saving...")
    path = root / "credit_engine" / "data" / "ensemble_lc_phase1_v3.pkl"
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'wb') as f:
        pickle.dump({
            'ensemble': ensemble,
            'scaler': scaler,
            'features': feature_cols,
            'encoder': le, 
            'timestamp': datetime.now().isoformat(),
            'phase': 1,
            'metrics': {
                'test_accuracy': test_acc,
                'train_accuracy': train_acc,
                'precision': prec,
                'recall': rec,
                'f1': f1,
                'roc_auc': roi,
                'cv_mean': cv.mean(),
                'cv_std': cv.std()
            },
            'base_scores': scores
        }, f)
    
    print(f"   ✓ Saved to {path}")
    print(f"   ✓ Size: {path.stat().st_size / 1e6:.1f}MB")
    
    print("\n" + "="*70)
    print("✅ PHASE 1 COMPLETE!")
    print("="*70)
    print("\n📈 Summary:")
    print(f"   ✓ 8 new financial health features engineered")
    print(f"   ✓ No synthetic data (SMOTE) - using class_weight instead")
    print(f"   ✓ 5-model ensemble trained with proper weighting")
    print(f"   ✓ Test accuracy: {test_acc:.2%} ({imp:+.2f}pp vs baseline)")
    
    if test_acc > 0.706:
        print("\n🎉 SUCCESS! Phase 1 improved accuracy!")
    else:
        print("\n⚠️ Accuracy decreased - may need different feature engineering")
    
    print("\n📅 Next Steps: Ready for Phase 2 if needed")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
