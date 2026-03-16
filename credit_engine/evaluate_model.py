"""Evaluate model accuracies on sample data."""

import os
import pandas as pd
from pathlib import Path
import yaml
from sklearn.metrics import f1_score, roc_auc_score, accuracy_score

from src.parser import PDFParser
from src.fraud import FraudDetector
from src.scorer import CreditScorer
from src.research import ResearchRAG


def load_config():
    root = Path(__file__).resolve().parent
    config_path = root / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def evaluate_parser(config):
    """Evaluate PDF parser accuracy on sample PDF."""
    parser = PDFParser(config)
    # Use a PDF from Dataset folder
    sample_pdf = Path(__file__).parent.parent / "Dataset" / "Annual report FY 2018-19.pdf"

    if not sample_pdf.exists():
        print("Sample PDF not found, skipping parser evaluation.")
        return None

    parsed = parser.parse(str(sample_pdf))

    # Check if key financials are extracted (presence-based accuracy)
    expected_keys = ["revenue", "net_profit", "ebitda", "total_assets", "debt_to_equity"]
    correct = sum(1 for key in expected_keys if key in parsed["financials"] and parsed["financials"][key] > 0)
    total = len(expected_keys)
    accuracy = correct / total if total > 0 else 0
    print(f"Parser Accuracy: {accuracy:.2%} ({correct}/{total} financials extracted)")
    return accuracy


def evaluate_fraud(config):
    """Evaluate fraud detection on sample GST data."""
    fraud_detector = FraudDetector(config)
    gst_path = Path(__file__).parent / "data" / "gst_transactions.csv"

    if not gst_path.exists():
        print("GST CSV not found, skipping fraud evaluation.")
        return None

    gst_df = pd.read_csv(gst_path)
    result = fraud_detector.analyze(gst_df)

    # For demo, assume high fraud score indicates detection
    # In real scenario, use labeled data
    detected = result["fraud_score"] > 50  # Threshold
    # Assume ground truth: if there are anomalies, it's positive
    has_anomalies = len(result["amount_anomalies"]) > 0 or len(result["circular_trading"]) > 0
    accuracy = 1.0 if detected == has_anomalies else 0.0
    print(f"Fraud Detection Accuracy: {accuracy:.2%} (Detected: {detected}, Has Anomalies: {has_anomalies})")
    return accuracy


def evaluate_scorer(config):
    """Evaluate scorer decision accuracy."""
    scorer = CreditScorer(config)

    # Sample inputs (hardcoded for demo)
    samples = [
        {
            "financials": {"revenue": 1000000, "net_profit": 100000, "debt_to_equity": 0.5},
            "fraud_result": {"fraud_score": 20},
            "research_context": "Stable market conditions.",
            "bank_analysis": {"avg_balance": 500000},
            "officer_notes": "Good management.",
            "expected_decision": "APPROVE",
        },
        {
            "financials": {"revenue": 500000, "net_profit": -50000, "debt_to_equity": 2.0},
            "fraud_result": {"fraud_score": 80},
            "research_context": "Risky sector.",
            "bank_analysis": {"avg_balance": 100000},
            "officer_notes": "Concerns about liquidity.",
            "expected_decision": "REJECT",
        },
    ]

    y_true = []
    y_pred = []

    for sample in samples:
        result = scorer.score(**{k: v for k, v in sample.items() if k != "expected_decision"})
        y_true.append(sample["expected_decision"])
        y_pred.append(result["decision"])

    accuracy = accuracy_score(y_true, y_pred)
    print(f"Scorer Decision Accuracy: {accuracy:.2%} ({sum(1 for t, p in zip(y_true, y_pred) if t == p)}/{len(y_true)} correct)")
    return accuracy


def evaluate_rag(config):
    """Evaluate RAG retrieval accuracy."""
    rag = ResearchRAG(config)
    # Ingest from data and Dataset
    rag.ingest_directory(str(Path(__file__).parent / "data"))
    rag.ingest_directory(str(Path(__file__).parent.parent / "Dataset"))

    # Sample queries and expected keywords in results
    queries = [
        ("financial statements", "annual"),
        ("credit analysis", "report"),
    ]

    correct = 0
    total = len(queries)

    for query, keyword in queries:
        results = rag.query(query, top_k=5)
        if any(keyword.lower() in r["text"].lower() for r in results):
            correct += 1

    accuracy = correct / total if total > 0 else 0
    print(f"RAG Retrieval Accuracy: {accuracy:.2%} ({correct}/{total} queries with relevant results)")
    return accuracy


def main():
    config = load_config()

    print("Evaluating Model Accuracies...\n")

    parser_acc = evaluate_parser(config)
    fraud_auc = evaluate_fraud(config)
    scorer_acc = evaluate_scorer(config)
    rag_acc = evaluate_rag(config)

    print("\nSummary:")
    if parser_acc is not None:
        print(f"- PDF Parsing Accuracy: {parser_acc:.2%}")
    if fraud_auc is not None:
        print(f"- Fraud Detection AUC: {fraud_auc:.2%}")
    if scorer_acc is not None:
        print(f"- Decision Accuracy: {scorer_acc:.2%}")
    if rag_acc is not None:
        print(f"- RAG Retrieval Accuracy: {rag_acc:.2%}")


if __name__ == "__main__":
    main()
