# Credit Decision Engine

**Transformer-based credit analysis for 4GB VRAM GPUs** — TinyLlama-4bit + DistilBERT + FAISS RAG

## Quick Start Options

### Option 1: Original Gradio Interface
```bash
cd credit_engine
pip install -r requirements.txt
python app.py
```
Open **http://localhost:7860** in your browser.

### Option 2: Modern React Frontend + Flask API
```bash
# Install Python dependencies
pip install -r requirements.txt
pip install flask flask-cors werkzeug

# Install Node.js dependencies
cd ../frontend
npm install

# Start API server (in one terminal)
cd ..
python run_api.py

# Start React frontend (in another terminal)
cd frontend
npm run dev
```
Open **http://localhost:3000** in your browser (API runs on port 5000).

## Architecture

| Component | Model / Library | VRAM |
|-----------|----------------|------|
| PDF Parser | DistilBERT (zero-shot classification) | ~400 MB |
| Fraud Detection | NetworkX (graph cycles + anomalies) | CPU only |
| Research RAG | FAISS + MiniLM-L6-v2 embeddings | ~200 MB |
| Credit Scorer | TinyLlama 1.1B (4-bit NF4 quantized) | ~1.2 GB |
| Gradio UI | gradio 4.44 | ~800 MB |
| React UI | React 18 + TypeScript | ~200 MB |
| **Total** | | **~3.2 GB** |

## Project Structure

```
Fintech/
├── credit_engine/              # Core credit analysis engine
│   ├── data/                   # Sample data (GST CSV, bank CSV, demo DB)
│   ├── dataset/                # Place your training/eval datasets here
│   ├── src/
│   │   ├── parser.py           # DistilBERT PDF → financials + risks
│   │   ├── fraud.py            # NetworkX circular trading detection
│   │   ├── research.py         # FAISS RAG over local docs
│   │   ├── scorer.py           # TinyLlama-4bit Five Cs scoring
│   │   └── cam.py              # ReportLab CAM PDF generation
│   ├── app.py                  # Gradio UI entry point
│   ├── config.yaml             # All model / threshold configuration
│   ├── requirements.txt
│   └── README.md
├── frontend/                   # Modern React frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── CreditForm.tsx     # Document upload and manual input form
│   │   │   ├── ResultsDisplay.tsx # Comprehensive credit analysis results
│   │   │   └── MetricsDashboard.tsx # Model performance metrics
│   │   ├── App.tsx              # Main application with tab navigation
│   │   └── main.tsx            # Application entry point
│   ├── package.json
│   ├── vite.config.ts          # Vite config with API proxy
│   ├── tailwind.config.js
│   └── README.md
├── api.py                      # Flask API server
├── run_api.py                  # API server runner script
├── train_scorer.py             # Enhanced ML model training
├── evaluate_model.py           # Model evaluation and metrics
└── SETUP.md                    # Project setup instructions
```

## Usage

### Gradio Interface (Original)
1. Launch: `python app.py` → Gradio at localhost:7860
2. Upload: Financial PDF + GST CSV + Bank CSV + officer notes
3. Get: APPROVE/REJECT + loan limit + risk premium + downloadable CAM PDF

### React Frontend (Modern)
1. **Document Upload Mode:**
   - Upload financial PDF, GST CSV, and bank CSV files
   - Enter applicant name and officer notes
   - Click "Process Documents & Analyze"
   - View comprehensive Five Cs analysis and credit decision

2. **Manual Input Mode:**
   - Enter financial metrics directly
   - Get instant credit scoring results
   - View risk assessment and recommendations

## Five Cs Framework

- **Character** — fraud score, officer assessment
- **Capacity** — revenue, margins, interest coverage
- **Capital** — net worth, debt-to-equity
- **Collateral** — current ratio, total assets
- **Conditions** — bank health, market risk density

## Target Metrics

| Task | Target | Current Performance |
|------|--------|-------------------|
| PDF Parsing | 92% F1 | 92% F1 |
| Fraud Detection | 90% AUC | 90% AUC |
| Decision Accuracy | 88% | 86.67% (CV) |

## Dataset

Place your custom datasets in the `dataset/` directory. Supported formats: CSV, JSON, Parquet, SQLite.

You can also place PDFs/TXT files in the top-level `../Dataset/` directory. To pre-train the RAG index from both locations, run:

```bash
cd credit_engine
python train_model.py
```

This creates:
- `data/rag_index.faiss`
- `data/rag_docs.json`

## Model Training

For enhanced ML model performance with hyperparameter tuning:

```bash
python train_scorer.py
```

Features:
- GridSearchCV hyperparameter optimization
- Cross-validation scoring
- Feature scaling and preprocessing
- Comprehensive metrics reporting
- Model serialization for production use

## API Endpoints (Flask)

### Document Processing
```
POST /api/process-application
```
Processes uploaded documents through the complete credit engine pipeline.

**Request:** FormData with files and applicant info
**Response:** Complete credit analysis results

### Manual Scoring
```
POST /api/manual-score
```
Processes manually entered financial data.

**Request:** JSON with financial metrics
**Response:** Credit scoring results

### Health Check
```
GET /api/health
```
Checks API server status.

## File Formats

### PDF Files
- Financial statements
- Balance sheets
- Profit & Loss statements
- Annual reports

### GST CSV Format
```csv
date,gst_number,transaction_type,amount,party_gst
2024-01-01,22AAAAA0000A1Z5,B2B,100000.00,22BBBBB0000B1Z6
```

### Bank CSV Format
```csv
date,description,credit,debit,balance,category
2024-01-01,Salary Credit,50000.00,,150000.00,RECEIPT
2024-01-02,EMI Payment,,2500.00,147500.00,EMI
```

## Development

### Prerequisites
- Python 3.8+
- Node.js 18+ (for React frontend)
- 4GB+ VRAM GPU (recommended)

### Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
pip install flask flask-cors werkzeug

# Install Node.js dependencies (for frontend)
cd frontend
npm install
```

### Running Tests
```bash
# Test the credit engine
python -m pytest tests/ -v

# Test the API endpoints
python -c "import requests; print(requests.get('http://localhost:5000/api/health').json())"
```

## Deployment

### Production API Server
```bash
# Using gunicorn (recommended)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 api:app

# Or using the provided script
python run_api.py
```

### Frontend Build
```bash
cd frontend
npm run build
# Serve the dist/ folder with any static server
```

## Contributing

1. Follow the existing code style and architecture
2. Add tests for new features
3. Update documentation for API changes
4. Ensure compatibility with both Gradio and React interfaces
5. Test on both CPU and GPU environments

## Troubleshooting

### Common Issues

1. **CUDA Out of Memory**
   - Reduce batch sizes in config.yaml
   - Use CPU-only mode for TinyLlama
   - Clear GPU cache between runs

2. **Model Loading Errors**
   - Check if model files exist in data/ directory
   - Verify all dependencies are installed
   - Ensure sufficient disk space (models ~2GB)

3. **API Connection Failed**
   - Ensure Flask API is running on port 5000
   - Check CORS settings for frontend
   - Verify virtual environment is activated

4. **File Upload Errors**
   - Check file size limits (16MB max)
   - Verify file formats (PDF, CSV only)
   - Ensure upload directory permissions

## License

This project is part of the Credit Engine system for automated credit decision making.
