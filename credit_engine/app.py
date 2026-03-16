"""Gradio UI — end-to-end Credit Decision Engine interface."""

import os
import tempfile
import sqlite3
from pathlib import Path

import yaml
import pandas as pd
import gradio as gr

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config.yaml"

with open(CONFIG_PATH, "r") as f:
    CONFIG = yaml.safe_load(f)

# ---------------------------------------------------------------------------
# Lazy-loaded singletons (keep VRAM under 3.2 GB)
# ---------------------------------------------------------------------------
_parser = None
_fraud = None
_rag = None
_scorer = None
_cam = None


def get_parser():
    global _parser
    if _parser is None:
        from src.parser import PDFParser
        _parser = PDFParser(CONFIG)
    return _parser


def get_fraud():
    global _fraud
    if _fraud is None:
        from src.fraud import FraudDetector
        _fraud = FraudDetector(CONFIG)
    return _fraud


def get_rag():
    global _rag
    if _rag is None:
        from src.research import ResearchRAG
        _rag = ResearchRAG(CONFIG)

        paths_cfg = CONFIG.get("paths", {})
        index_path = str(ROOT / paths_cfg.get("rag_index_path", "data/rag_index.faiss"))
        docs_path = str(ROOT / paths_cfg.get("rag_docs_path", "data/rag_docs.json"))

        loaded = _rag.load(index_path=index_path, docs_path=docs_path)
        if not loaded:
            # Fallback: ingest local docs and persist for later runs.
            local_data_dir = str(ROOT / paths_cfg.get("data_dir", "data"))
            local_dataset_dir = str(ROOT / paths_cfg.get("dataset_dir", "dataset"))
            external_dataset_dir = str(ROOT.parent / paths_cfg.get("external_dataset_dir", "Dataset"))

            for data_path in [local_data_dir, local_dataset_dir, external_dataset_dir]:
                _rag.ingest_directory(data_path)

            _rag.save(index_path=index_path, docs_path=docs_path)
    return _rag


def get_scorer():
    global _scorer
    if _scorer is None:
        from src.scorer import CreditScorer
        _scorer = CreditScorer(CONFIG)
    return _scorer


def get_cam():
    global _cam
    if _cam is None:
        from src.cam import CAMGenerator
        _cam = CAMGenerator(CONFIG)
    return _cam


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------
def _init_db():
    db_path = ROOT / CONFIG["database"]["path"]
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            applicant TEXT,
            credit_score REAL,
            decision TEXT,
            loan_limit REAL,
            risk_premium REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn


def _save_decision(applicant, result):
    conn = _init_db()
    conn.execute(
        "INSERT INTO decisions (applicant, credit_score, decision, loan_limit, risk_premium) VALUES (?, ?, ?, ?, ?)",
        (applicant, result["credit_score"], result["decision"],
         result["loan_limit"], result["risk_premium_pct"]),
    )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Bank statement analysis
# ---------------------------------------------------------------------------
def analyze_bank_csv(file_path: str | None) -> dict:
    if not file_path:
        return {}
    df = pd.read_csv(file_path)
    analysis = {}

    if "balance" in df.columns:
        analysis["avg_balance"] = df["balance"].astype(float).mean()
        analysis["min_balance"] = df["balance"].astype(float).min()
        analysis["max_balance"] = df["balance"].astype(float).max()

    if "credit" in df.columns and "debit" in df.columns:
        total_credit = df["credit"].astype(float).sum()
        total_debit = df["debit"].astype(float).sum()
        analysis["total_inflow"] = total_credit
        analysis["total_outflow"] = total_debit
        analysis["net_flow"] = total_credit - total_debit

    if "category" in df.columns:
        emi_total = df.loc[df["category"] == "EMI", "debit"].astype(float).sum()
        income_total = df.loc[df["category"] == "RECEIPT", "credit"].astype(float).sum()
        analysis["emi_to_income_ratio"] = emi_total / income_total if income_total > 0 else 0

    return analysis


# ---------------------------------------------------------------------------
# Main processing pipeline
# ---------------------------------------------------------------------------
def process_application(
    pdf_file, gst_file, bank_file, officer_notes, applicant_name
):
    """Run the full credit decision pipeline and return results."""
    status_parts = []

    # 1. Parse PDF
    if pdf_file is not None:
        parser = get_parser()
        parsed = parser.parse(pdf_file)
        financials = parsed["financials"]
        risks = parsed["risks"]
        status_parts.append(f"✓ PDF parsed — {risks['total_sentences']} sentences, {risks['risk_count']} risk flags")
    else:
        financials = {}
        risks = {"risk_sentences": [], "positive_sentences": [], "risk_density": 0,
                 "total_sentences": 0, "risk_count": 0, "positive_count": 0}
        status_parts.append("⚠ No PDF uploaded — using empty financials")

    # 2. Fraud detection on GST
    if gst_file is not None:
        gst_df = pd.read_csv(gst_file)
        fraud_detector = get_fraud()
        fraud_result = fraud_detector.analyze(gst_df)
        status_parts.append(
            f"✓ GST fraud analysis — score {fraud_result['fraud_score']}/100, {fraud_result['total_flags']} flags"
        )
    else:
        fraud_result = {
            "fraud_score": 0, "circular_trading": [], "amount_anomalies": [],
            "concentration_risks": [], "total_flags": 0,
            "high_severity_count": 0, "medium_severity_count": 0,
            "graph_stats": {"nodes": 0, "edges": 0, "density": 0},
        }
        status_parts.append("⚠ No GST CSV — fraud score set to 0")

    # 3. Bank analysis
    bank_analysis = analyze_bank_csv(bank_file)
    if bank_analysis:
        status_parts.append(f"✓ Bank analysis — avg balance ₹{bank_analysis.get('avg_balance', 0):,.0f}")
    else:
        status_parts.append("⚠ No bank statement")

    # 4. RAG context
    rag = get_rag()
    research_context = rag.build_context(
        f"credit analysis for {applicant_name} revenue {financials.get('revenue', 0)}"
    )
    status_parts.append(f"✓ RAG context — {rag.get_stats()['total_chunks']} chunks indexed")

    # 5. Credit scoring
    scorer = get_scorer()
    result = scorer.score(
        financials=financials,
        fraud_result=fraud_result,
        research_context=research_context,
        bank_analysis=bank_analysis,
        officer_notes=officer_notes or "",
    )
    status_parts.append(f"✓ Scored — {result['credit_score']}/100 → {result['decision']}")

    # 6. Save to DB
    _save_decision(applicant_name or "Unknown", result)

    # 7. Generate CAM PDF
    cam = get_cam()
    cam_path = str(ROOT / "output" / f"CAM_{applicant_name or 'report'}.pdf")
    cam.generate(result, financials, fraud_result,
                 applicant_name=applicant_name or "Applicant",
                 output_path=cam_path)
    status_parts.append("✓ CAM PDF generated")

    # -- Format outputs --
    decision_md = _format_decision(result)
    five_cs_md = _format_five_cs(result["five_cs"])
    status_text = "\n".join(status_parts)

    return decision_md, five_cs_md, result["narrative"], status_text, cam_path, fraud_result, bank_analysis


# ---------------------------------------------------------------------------
# Formatters
# ---------------------------------------------------------------------------
def _format_decision(result: dict) -> str:
    color = "green" if result["decision"] == "APPROVE" else "red"
    return (
        f"## Credit Decision\n\n"
        f"| Metric | Value |\n"
        f"|--------|-------|\n"
        f"| **Credit Score** | {result['credit_score']}/100 |\n"
        f"| **Decision** | **{result['decision']}** |\n"
        f"| **Loan Limit** | ₹{result['loan_limit']:,.0f} |\n"
        f"| **Risk Premium** | {result['risk_premium_pct']:.2f}% |\n"
    )


def _format_five_cs(five_cs: dict) -> str:
    md = "## Five Cs Breakdown\n\n| Parameter | Score | Rationale |\n|-----------|-------|----------|\n"
    for c_name in ["character", "capacity", "capital", "collateral", "conditions"]:
        data = five_cs.get(c_name, {"score": 0, "rationale": "N/A"})
        bar = "█" * int(data["score"] / 10) + "░" * (10 - int(data["score"] / 10))
        md += f"| **{c_name.title()}** | {data['score']:.1f} {bar} | {data['rationale']} |\n"
    return md


# ---------------------------------------------------------------------------
# Gradio Interface
# ---------------------------------------------------------------------------
def build_ui():
    theme = gr.themes.Soft()

    with gr.Blocks(theme=theme, title="Credit Decision Engine") as demo:
        gr.Markdown(
            "# 🏦 Credit Decision Engine\n"
            "**Transformer-powered credit analysis** — Upload documents, get APPROVE/REJECT + CAM PDF\n"
            "---"
        )

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 📄 Upload Documents")
                applicant_name = gr.Textbox(label="Applicant Name", placeholder="e.g. Acme Corp Pvt Ltd")
                pdf_input = gr.File(label="Financial Statement PDF", file_types=[".pdf"])
                gst_input = gr.File(label="GST Transactions CSV", file_types=[".csv"])
                bank_input = gr.File(label="Bank Statement CSV", file_types=[".csv"])
                officer_notes = gr.Textbox(
                    label="Credit Officer Notes",
                    placeholder="Observations, site visit notes, management quality...",
                    lines=4,
                )
                submit_btn = gr.Button("🔍 Analyze & Score", variant="primary", size="lg")

            with gr.Column(scale=2):
                gr.Markdown("### 📊 Results")
                with gr.Tabs():
                    with gr.Tab("Decision"):
                        decision_output = gr.Markdown()
                    with gr.Tab("Five Cs"):
                        five_cs_output = gr.Markdown()
                    with gr.Tab("Narrative"):
                        narrative_output = gr.Textbox(label="AI Narrative", lines=15, interactive=False)
                    with gr.Tab("Status"):
                        status_output = gr.Textbox(label="Pipeline Status", lines=10, interactive=False)

                cam_download = gr.File(label="📥 Download CAM PDF")

        submit_btn.click(
            fn=process_application,
            inputs=[pdf_input, gst_input, bank_input, officer_notes, applicant_name],
            outputs=[decision_output, five_cs_output, narrative_output, status_output, cam_download],
        )

        gr.Markdown(
            "---\n*Credit Decision Engine v1.0 • TinyLlama-4bit + DistilBERT + FAISS • 4GB VRAM*"
        )

    return demo


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    os.makedirs(ROOT / "output", exist_ok=True)
    demo = build_ui()
    demo.launch(
        server_port=CONFIG["gradio"]["server_port"],
        share=CONFIG["gradio"]["share"],
    )
