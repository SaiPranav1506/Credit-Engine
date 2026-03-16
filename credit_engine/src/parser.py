"""DistilBERT-based PDF parser for extracting financials and risk indicators."""

import re
import fitz  # PyMuPDF
import torch
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline


class PDFParser:
    """Parses financial PDFs and extracts structured data using DistilBERT NER/classification."""

    # Financial line-item patterns
    FINANCIAL_PATTERNS = {
        "revenue": r"(?:revenue|total\s*income|turnover|gross\s*sales|sales\s*revenue|net\s*sales)[\s:]*[\₹$]?\s*([\d,]+\.?\d*)",
        "net_profit": r"(?:net\s*profit|pat|profit\s*after\s*tax|net\s*income)[\s:]*[\₹$]?\s*([\d,]+\.?\d*)",
        "ebitda": r"(?:ebitda|operating\s*profit|earnings\s*before\s*interest\s*tax\s*depreciation\s*amortization)[\s:]*[\₹$]?\s*([\d,]+\.?\d*)",
        "total_assets": r"(?:total\s*assets|assets)[\s:]*[\₹$]?\s*([\d,]+\.?\d*)",
        "total_liabilities": r"(?:total\s*liabilities|liabilities)[\s:]*[\₹$]?\s*([\d,]+\.?\d*)",
        "current_assets": r"(?:current\s*assets)[\s:]*[\₹$]?\s*([\d,]+\.?\d*)",
        "current_liabilities": r"(?:current\s*liabilities)[\s:]*[\₹$]?\s*([\d,]+\.?\d*)",
        "net_worth": r"(?:net\s*worth|shareholders?\s*equity|equity|owners?\s*equity)[\s:]*[\₹$]?\s*([\d,]+\.?\d*)",
        "debt": r"(?:long\s*term\s*debt|total\s*borrowings?|term\s*loans?|total\s*debt)[\s:]*[\₹$]?\s*([\d,]+\.?\d*)",
        "interest_expense": r"(?:interest\s*expense|finance\s*cost|interest\s*paid)[\s:]*[\₹$]?\s*([\d,]+\.?\d*)",
        "depreciation": r"(?:depreciation|amortization|depreciation\s*and\s*amortization)[\s:]*[\₹$]?\s*([\d,]+\.?\d*)",
        "tax_expense": r"(?:tax\s*expense|income\s*tax|provision\s*for\s*tax|tax\s*liability)[\s:]*[\₹$]?\s*([\d,]+\.?\d*)",
        "cash_flow_operations": r"(?:cash\s*from\s*operations|operating\s*cash\s*flow|net\s*cash\s*from\s*operating\s*activities)[\s:]*[\₹$]?\s*([\d,]+\.?\d*)",
    }

    RISK_KEYWORDS = [
        "default", "overdue", "npa", "non-performing", "restructured",
        "wilful defaulter", "fraud", "litigation", "disputed", "loss",
        "negative net worth", "eroded", "declining", "stressed",
        "write-off", "provision", "contingent liability"
    ]

    POSITIVE_KEYWORDS = [
        "profit", "growth", "increase", "positive", "healthy",
        "strong", "improved", "stable", "consistent", "quality"
    ]

    def __init__(self, config: dict):
        self.config = config
        parser_cfg = config.get("models", {}).get("parser", {})
        model_name = parser_cfg.get("name", "distilbert-base-uncased")
        max_len = parser_cfg.get("max_length", 512)
        self.enable_section_classification = parser_cfg.get("enable_section_classification", False)

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = None
        self.model = None
        self.max_length = max_len

        self.classifier = None
        if self.enable_section_classification:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(
                model_name, num_labels=2
            ).to(self.device)
            # Zero-shot classifier for section labelling
            self.classifier = pipeline(
                "zero-shot-classification",
                model=model_name,
                device=0 if self.device == "cuda" else -1,
            )

    # ------------------------------------------------------------------
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract raw text from a PDF file."""
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text

    def extract_text_from_bytes(self, pdf_bytes: bytes) -> str:
        """Extract raw text from PDF bytes (Gradio upload)."""
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text

    # ------------------------------------------------------------------
    def extract_financials(self, text: str) -> dict:
        """Regex + NLP extraction of financial line items."""
        financials = {}
        text_lower = text.lower()

        for key, pattern in self.FINANCIAL_PATTERNS.items():
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            if matches:
                try:
                    value = float(matches[0].replace(",", ""))
                    financials[key] = value
                except ValueError:
                    financials[key] = 0.0
            else:
                financials[key] = 0.0

        # Derived ratios
        if financials.get("total_assets", 0) > 0:
            financials["debt_to_asset"] = financials.get("total_liabilities", 0) / financials["total_assets"]

        if financials.get("net_worth", 0) > 0:
            financials["debt_to_equity"] = financials.get("debt", 0) / financials["net_worth"]

        if financials.get("current_liabilities", 0) > 0:
            financials["current_ratio"] = financials.get("current_assets", 0) / financials["current_liabilities"]

        if financials.get("interest_expense", 0) > 0 and financials.get("ebitda", 0) > 0:
            financials["interest_coverage"] = financials["ebitda"] / financials["interest_expense"]

        if financials.get("revenue", 0) > 0:
            financials["net_margin"] = financials.get("net_profit", 0) / financials["revenue"]

        return financials

    # ------------------------------------------------------------------
    def detect_risks(self, text: str) -> dict:
        """Identify risk sentences and positive signals in the text."""
        sentences = re.split(r"[.\n]", text)
        risk_sentences = []
        positive_sentences = []

        for sent in sentences:
            sent_lower = sent.lower().strip()
            if not sent_lower:
                continue
            for kw in self.RISK_KEYWORDS:
                if kw in sent_lower:
                    risk_sentences.append(sent.strip())
                    break
            for kw in self.POSITIVE_KEYWORDS:
                if kw in sent_lower:
                    positive_sentences.append(sent.strip())
                    break

        risk_score = len(risk_sentences) / max(len(sentences), 1)
        return {
            "risk_sentences": risk_sentences[:10],
            "positive_sentences": positive_sentences[:10],
            "risk_density": round(risk_score, 4),
            "total_sentences": len(sentences),
            "risk_count": len(risk_sentences),
            "positive_count": len(positive_sentences),
        }

    # ------------------------------------------------------------------
    def classify_sections(self, text: str) -> dict:
        """Use DistilBERT zero-shot to label text chunks."""
        if not self.enable_section_classification or self.classifier is None:
            return {}

        candidate_labels = [
            "income statement", "balance sheet", "cash flow",
            "auditor notes", "management discussion", "risk factors"
        ]
        chunks = self._chunk_text(text, max_chars=800)
        section_map = {}

        for chunk in chunks[:15]:  # limit to save VRAM
            result = self.classifier(chunk, candidate_labels)
            top_label = result["labels"][0]
            section_map.setdefault(top_label, []).append(chunk)

        return section_map

    # ------------------------------------------------------------------
    def parse(self, pdf_input) -> dict:
        """Full pipeline: PDF → text → financials + risks + sections."""
        if isinstance(pdf_input, bytes):
            text = self.extract_text_from_bytes(pdf_input)
        elif isinstance(pdf_input, str) and pdf_input.endswith(".pdf"):
            text = self.extract_text_from_pdf(pdf_input)
        else:
            text = str(pdf_input)

        financials = self.extract_financials(text)
        risks = self.detect_risks(text)
        sections = self.classify_sections(text)

        return {
            "raw_text": text,
            "financials": financials,
            "risks": risks,
            "sections": sections,
        }

    # ------------------------------------------------------------------
    @staticmethod
    def _chunk_text(text: str, max_chars: int = 800) -> list:
        words = text.split()
        chunks, current = [], []
        length = 0
        for w in words:
            if length + len(w) + 1 > max_chars:
                chunks.append(" ".join(current))
                current, length = [], 0
            current.append(w)
            length += len(w) + 1
        if current:
            chunks.append(" ".join(current))
        return chunks
