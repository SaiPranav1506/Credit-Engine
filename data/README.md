# Data directory structure

This folder contains all project datasets organized by type and size:

## Dataset Structure

```
data/
├── Dataset/                          ← Main dataset folder
│   ├── labeled_scorer_data_500_samples.csv
│   ├── labeled_scorer_data_engineered_500_samples.csv
│   ├── labeled_scorer_data_original_20_samples.csv
│   ├── lendingclub_1000_samples.csv
│   ├── lendingclub_2000_samples.csv
│   ├── lendingclub_full.csv
│   ├── lendingclub_integration_report.txt
│   └── README.md
└── README.md (this file)
```

## Usage

### For Model Training:
- Use datasets in `Dataset/` folder
- Training scripts reference: `../data/Dataset/filename.csv`

### For Deployment:
- Datasets are **excluded from production** (.gitignore)
- Model predictions use trained ensemble model, not raw datasets
- Only production model file is deployed: `ensemble_phase3_optimized.pkl`

## Dataset Details

| File | Size | Purpose | Samples |
|------|------|---------|---------|
| lendingclub_full.csv | Full | Production training | ~100K+ |
| lendingclub_2000_samples.csv | Medium | Testing | 2K |
| lendingclub_1000_samples.csv | Small | Quick tests | 1K |
| labeled_scorer_data_* | Labeled | Model validation | 20-500 |

## Gitignore

All large datasets are excluded from Git (see `.gitignore`):
```
data/Dataset/lendingclub_*.csv
data/Dataset/labeled_*.csv
```

This keeps the repository small while preserving training capability.

---

**Note**: To download datasets again, use training scripts that auto-fetch from data sources.
