"""
Flask API for Credit Engine Frontend Integration
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import tempfile
import traceback
from pathlib import Path
import pandas as pd
from werkzeug.utils import secure_filename

# Import existing credit engine components
import sys
sys.path.append(str(Path(__file__).parent))
# Ensure credit_engine/src is on the import path so `from src.*` works
sys.path.append(str(Path(__file__).parent / "credit_engine"))

from credit_engine.app import process_application

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'csv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Credit Engine API is running'})

@app.route('/api/process-application', methods=['POST'])
def process_credit_application():
    """
    Process credit application with document uploads
    """
    try:
        # Get form data
        applicant_name = request.form.get('applicant_name', 'Unknown Applicant')
        officer_notes = request.form.get('officer_notes', '')

        # Handle file uploads
        pdf_file = None
        gst_file = None
        bank_file = None

        if 'pdf_file' in request.files:
            pdf_file_obj = request.files['pdf_file']
            if pdf_file_obj and allowed_file(pdf_file_obj.filename):
                filename = secure_filename(pdf_file_obj.filename)
                pdf_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                pdf_file_obj.save(pdf_file)

        if 'gst_file' in request.files:
            gst_file_obj = request.files['gst_file']
            if gst_file_obj and allowed_file(gst_file_obj.filename):
                filename = secure_filename(gst_file_obj.filename)
                gst_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                gst_file_obj.save(gst_file)

        if 'bank_file' in request.files:
            bank_file_obj = request.files['bank_file']
            if bank_file_obj and allowed_file(bank_file_obj.filename):
                filename = secure_filename(bank_file_obj.filename)
                bank_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                bank_file_obj.save(bank_file)

        # Process application using existing credit engine
        decision_md, five_cs_md, narrative, status_text, cam_path, fraud_result, bank_analysis = process_application(
            pdf_file, gst_file, bank_file, officer_notes, applicant_name
        )

        # Parse the markdown results into structured data
        result = parse_credit_decision(decision_md, five_cs_md, narrative, status_text, cam_path, fraud_result, bank_analysis)

        return jsonify({
            'success': True,
            'result': result,
            'processing_status': status_text.split('\n')
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'trace': traceback.format_exc(),
        }), 500

def parse_credit_decision(decision_md, five_cs_md, narrative, status_text, cam_path, fraud_result=None, bank_analysis=None):
    """
    Parse markdown results into structured JSON
    """
    # Parse decision markdown
    decision_lines = decision_md.split('\n')
    credit_score = 0
    decision = 'PENDING'
    loan_limit = 0
    risk_premium = 0.0

    for line in decision_lines:
        if 'Credit Score' in line:
            # Extract score from markdown table
            parts = line.split('|')
            if len(parts) >= 3:
                score_text = parts[2].strip()
                credit_score = int(score_text.split('/')[0])
        elif 'Decision' in line and 'APPROVE' in line:
            decision = 'APPROVE'
        elif 'Decision' in line and 'REJECT' in line:
            decision = 'REJECT'
        elif 'Loan Limit' in line:
            parts = line.split('|')
            if len(parts) >= 3:
                limit_text = parts[2].strip()
                # Remove ₹ and commas
                limit_str = limit_text.replace('₹', '').replace(',', '')
                loan_limit = int(limit_str)
        elif 'Risk Premium' in line:
            parts = line.split('|')
            if len(parts) >= 3:
                premium_text = parts[2].strip()
                risk_premium = float(premium_text.replace('%', ''))

    # Parse Five Cs
    five_cs = {
        'character': {'score': 0, 'rationale': ''},
        'capacity': {'score': 0, 'rationale': ''},
        'capital': {'score': 0, 'rationale': ''},
        'collateral': {'score': 0, 'rationale': ''},
        'conditions': {'score': 0, 'rationale': ''}
    }

    # Parse markdown table: | **Character** | 8.0 ████░░░░░░ | rationale |
    five_cs_lines = five_cs_md.split('\n')
    for line in five_cs_lines:
        if '**' in line and '|' in line:
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 4:
                # Extract parameter name
                param_text = parts[1].lower().replace('**', '')
                # Extract score (first number in the score cell)
                score_text = parts[2]
                # Get first word which is the score
                score_val = score_text.split()[0] if score_text else '0'
                # Extract rationale
                rationale = parts[3] if len(parts) > 3 else ''
                
                try:
                    score = float(score_val)
                    if param_text in five_cs:
                        five_cs[param_text] = {'score': int(score), 'rationale': rationale}
                except (ValueError, IndexError):
                    pass

    # Prepare fraud and bank analysis
    fraud_analysis_result = None
    bank_analysis_result = None
    
    if fraud_result:
        fraud_analysis_result = {
            'fraud_score': fraud_result.get('fraud_score', 0),
            'total_flags': fraud_result.get('total_flags', 0),
            'high_severity_count': fraud_result.get('high_severity_count', 0)
        }
    
    if bank_analysis:
        bank_analysis_result = {
            'avg_balance': bank_analysis.get('avg_balance', 0),
            'total_inflow': bank_analysis.get('total_inflow', 0),
            'total_outflow': bank_analysis.get('total_outflow', 0)
        }

    return {
        'decision': decision,
        'credit_score': credit_score,
        'loan_limit': loan_limit,
        'risk_premium_pct': risk_premium,
        'five_cs': {
            c: {'score': min(10, max(0, int(v['score'] / 10))), 'rationale': v['rationale']}
            for c, v in five_cs.items()
        },
        'narrative': narrative,
        'cam_path': cam_path,
        'fraud_analysis': fraud_analysis_result,
        'bank_analysis': bank_analysis_result,
        'processing_status': status_text.split('\n')
    }

@app.route('/api/download-cam/<path:filename>', methods=['GET'])
def download_cam(filename):
    """
    Download CAM PDF
    """
    try:
        # Ensure the file path is within the output directory
        output_dir = Path(__file__).parent / 'credit_engine' / 'output'
        file_path = output_dir / filename
        
        # Security check: ensure the path is within output_dir
        if not str(file_path).startswith(str(output_dir)):
            return jsonify({'error': 'Invalid file path'}), 400
        
        if not file_path.exists():
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/manual-score', methods=['POST'])
def manual_credit_score():
    """
    Manual credit scoring endpoint for direct financial data input
    """
    try:
        data = request.get_json()

        # Extract financial data
        financials = {
            'revenue': data.get('revenue', 0),
            'net_profit': data.get('net_profit', 0),
            'debt_to_equity': data.get('debt_to_equity', 0),
        }

        fraud_result = {
            'fraud_score': data.get('fraud_score', 0),
            'total_flags': 0,
            'high_severity_count': 0,
            'medium_severity_count': 0,
        }

        bank_analysis = {
            'avg_balance': data.get('avg_balance', 0),
        }

        # Use existing scorer
        from src.scorer import CreditScorer
        import yaml

        ROOT = Path(__file__).resolve().parent
        CONFIG_PATH = ROOT / "config.yaml"

        with open(CONFIG_PATH, "r") as f:
            CONFIG = yaml.safe_load(f)

        scorer = CreditScorer(CONFIG)
        result = scorer.score(
            financials=financials,
            fraud_result=fraud_result,
            research_context="Manual credit assessment",
            bank_analysis=bank_analysis,
            officer_notes=data.get('officer_notes', ''),
        )

        return jsonify({
            'success': True,
            'result': result
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'trace': traceback.format_exc(),
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)