# 4GB VRAM CREDIT DECISION ENGINE - COMPLETE VS CODE SETUP + EXECUTION
# Transformer-based (TinyLlama/DistilBERT) - 88% accuracy - FULLY LOCAL

## PROJECT WORKFLOW (3 WEEKS):
Week 1: Setup + PDF Parser + Fraud Detection
Week 2: Research RAG + Credit Scorer  
Week 3: Gradio UI + CAM PDF + Testing

## REQUIRED FOLDER STRUCTURE - CREATE NOW:
credit_engine/
├── data/
│   ├── demo.sqlite
│   ├── sample_financials.pdf
│   ├── gst_transactions.csv
│   └── bank_statements.csv
├── src/
│   ├── __init__.py
│   ├── parser.py          # DistilBERT PDF → financials/risks
│   ├── fraud.py           # NetworkX circular trading detection
│   ├── research.py        # FAISS RAG (local docs)
│   ├── scorer.py          # TinyLlama-4bit decisions
│   └── cam.py            # ReportLab Five Cs PDF
├── app.py                 # Gradio UI - COMPLETE END-TO-END
├── requirements.txt
├── config.yaml
└── README.md

## INSTALL COMMANDS (RUN IN VS CODE TERMINAL):
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install transformers==4.44.0 bitsandbytes==0.43.1 accelerate==0.33.0
pip install gradio==4.44.0 sentence-transformers==3.0.1 networkx==3.3
pip install faiss-cpu==1.8.0 reportlab==4.2.2 pyyaml==6.0.2 shap==0.48.0
pip install PyMuPDF==1.24.7 pandas==2.2.2 sqlite3

## CORE EXECUTION (ONE COMMAND):
python app.py

## MEMORY USAGE (4GB GPU SAFE):
TinyLlama-4bit: 1.2GB | DistilBERT: 400MB | FAISS: 200MB | Gradio: 800MB | TOTAL: 3.2GB

## VS CODE EXTENSIONS REQUIRED:
Python | Jupyter | GitHub Copilot | Gradio | Error Lens

## COMPLETE requirements.txt - GENERATE:
"""
torch==2.4.0+cu121
transformers==4.44.0
bitsandbytes==0.43.1
accelerate==0.33.0
gradio==4.44.0
sentence-transformers==3.0.1
networkx==3.3
faiss-cpu==1.8.0
reportlab==4.2.2
PyMuPDF==1.24.7
pandas==2.2.2
pyyaml==6.0.2
shap==0.48.0
"""

## EXECUTION WORKFLOW:
1. python app.py → Gradio launches localhost:7860
2. Upload: PDF + GST CSV + Bank CSV + Officer notes
3. GET: APPROVE/REJECT + Loan Limit + Risk Premium + CAM PDF
4. Five Cs: Character/Capacity/Capital/Collateral/Conditions

## TARGET METRICS:
PDF Parsing: 92% F1 | Fraud Detection: 90% AUC | Decision Accuracy: 88%

## GPU MONITORING:
nvidia-smi -l 1  # Terminal tab 2

GENERATE ALL 8 FILES WITH COMPLETE IMPLEMENTATION FOR 4GB VRAM!
DEPLOYMENT READY GRADIO UI WITH SAMPLE DATA!
