# Credit Engine Frontend

A modern React + Vite frontend for the AI-powered credit scoring system with document upload capabilities.

## Features

- **Document Upload**: Upload PDF financial statements, GST CSV files, and bank statements
- **Manual Input**: Alternative manual data entry for quick assessments
- **Real-time Processing**: AI-powered credit scoring with comprehensive analysis
- **Five Cs Analysis**: Detailed character, capacity, capital, collateral, and conditions assessment
- **Fraud Detection**: Automated fraud analysis from GST data
- **Bank Analysis**: Transaction analysis and cash flow insights
- **Model Metrics Dashboard**: Visualize model performance and feature importance
- **Responsive Design**: Works on desktop and mobile devices
- **Modern UI**: Built with Tailwind CSS and Lucide icons

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **Recharts** - Data visualization
- **Lucide React** - Icons
- **Axios** - HTTP client

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.8+
- Virtual environment with required packages

### Installation

1. **Install frontend dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start the backend API:**
   ```bash
   # From project root
   python run_api.py
   ```

3. **Start the frontend development server:**
   ```bash
   cd frontend
   npm run dev
   ```

4. **Open your browser:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000

## Usage

### Document Upload Mode

1. **Select "Document Upload"** mode
2. **Enter applicant information:**
   - Applicant name
   - Officer notes (optional)

3. **Upload documents:**
   - **Financial PDF**: Company financial statements, balance sheets, P&L statements
   - **GST CSV**: Goods and Services Tax transaction data for fraud analysis
   - **Bank CSV**: Bank statements for cash flow and transaction analysis

4. **Click "Process Documents & Analyze"**
5. **View results** in the comprehensive analysis display

### Manual Input Mode

1. **Select "Manual Input"** mode
2. **Enter financial metrics:**
   - Annual revenue
   - Net profit
   - Debt-to-equity ratio
   - Fraud score
   - Average account balance

3. **Click "Analyze Credit Risk"**
4. **View results** in the analysis display

## API Endpoints

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

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── CreditForm.tsx       # Document upload and manual input form
│   │   ├── ResultsDisplay.tsx   # Comprehensive credit analysis results
│   │   └── MetricsDashboard.tsx # Model performance metrics
│   ├── App.tsx                  # Main application with tab navigation
│   └── main.tsx                # Application entry point
├── package.json
├── vite.config.ts              # Vite config with API proxy
├── tailwind.config.js
└── README.md

api.py                         # Flask API server
run_api.py                     # API server runner script
```

## Features Overview

### Document Processing Pipeline

1. **PDF Parsing**: Extracts financial data from PDF documents
2. **GST Fraud Analysis**: Detects suspicious patterns in tax transactions
3. **Bank Statement Analysis**: Analyzes cash flow and transaction patterns
4. **RAG Context**: Retrieves relevant financial knowledge
5. **Credit Scoring**: Applies ML model for final decision
6. **CAM Generation**: Creates Credit Assessment Memorandum PDF

### Results Display

- **Credit Decision**: Approve/Reject with confidence score
- **Five Cs Breakdown**: Detailed analysis of credit factors
- **Risk Assessment**: Fraud scores and risk levels
- **Financial Metrics**: Loan limits and risk premiums
- **Processing Status**: Step-by-step pipeline progress
- **Recommendations**: Actionable insights for credit officers

### Model Metrics Dashboard

- **Performance Charts**: Accuracy, precision, recall metrics
- **Feature Importance**: Which factors influence decisions most
- **Cross-validation Results**: Robustness testing
- **Confusion Matrix**: Prediction accuracy breakdown
- **Model Characteristics**: Hyperparameters and dataset info

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run lint` - Run ESLint
- `npm run preview` - Preview production build

### API Development

- `python run_api.py` - Start Flask API server
- API runs on port 5000 with CORS enabled
- File uploads stored in `uploads/` directory

### Code Style

- Uses ESLint for code linting
- TypeScript for type safety
- Prettier for code formatting (recommended)

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

## Contributing

1. Follow the existing code style
2. Add TypeScript types for new features
3. Test components on different screen sizes
4. Update API documentation for new endpoints
5. Add proper error handling for API calls

## Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Ensure Flask API is running on port 5000
   - Check CORS settings
   - Verify virtual environment is activated

2. **File Upload Errors**
   - Check file size limits (16MB max)
   - Verify file formats (PDF, CSV only)
   - Ensure upload directory exists

3. **Model Loading Errors**
   - Check if model files exist in `data/` directory
   - Verify all Python dependencies are installed
   - Check configuration in `config.yaml`

## License

This project is part of the Credit Engine system.