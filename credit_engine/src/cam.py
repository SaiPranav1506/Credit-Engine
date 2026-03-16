"""ReportLab-based Credit Appraisal Memorandum (CAM) PDF generator — Five Cs layout."""

import os
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY


class CAMGenerator:
    """Generates a professional Credit Appraisal Memorandum PDF from scoring results."""

    def __init__(self, config: dict):
        self.config = config
        self.styles = getSampleStyleSheet()
        self._add_custom_styles()

    # ------------------------------------------------------------------
    def _add_custom_styles(self):
        self.styles.add(ParagraphStyle(
            name="CAMTitle",
            parent=self.styles["Title"],
            fontSize=18,
            spaceAfter=10,
            textColor=colors.HexColor("#1a237e"),
            alignment=TA_CENTER,
        ))
        self.styles.add(ParagraphStyle(
            name="SectionHead",
            parent=self.styles["Heading2"],
            fontSize=13,
            spaceAfter=6,
            spaceBefore=12,
            textColor=colors.HexColor("#283593"),
            borderWidth=0,
            borderPadding=0,
        ))
        self.styles.add(ParagraphStyle(
            name="CAMBody",
            parent=self.styles["BodyText"],
            fontSize=10,
            leading=14,
            alignment=TA_JUSTIFY,
        ))
        self.styles.add(ParagraphStyle(
            name="CAMSmall",
            parent=self.styles["BodyText"],
            fontSize=8,
            leading=10,
            textColor=colors.grey,
        ))

    # ------------------------------------------------------------------
    def generate(self, score_result: dict, financials: dict, fraud_result: dict,
                 applicant_name: str = "Applicant", output_path: str | None = None) -> bytes:
        """Generate CAM PDF and return bytes (also saves to disk if output_path given)."""
        buf = io.BytesIO()
        doc = SimpleDocTemplate(
            buf, pagesize=A4,
            leftMargin=2 * cm, rightMargin=2 * cm,
            topMargin=2 * cm, bottomMargin=2 * cm,
        )

        elements = []
        elements += self._header(applicant_name, score_result)
        elements += self._executive_summary(score_result, financials)
        elements += self._five_cs_section(score_result)
        elements += self._financial_highlights(financials)
        elements += self._fraud_section(fraud_result)
        elements += self._recommendation(score_result)
        elements += self._footer()

        doc.build(elements)
        pdf_bytes = buf.getvalue()

        if output_path:
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(pdf_bytes)

        return pdf_bytes

    # ------------------------------------------------------------------
    def _header(self, applicant_name, score_result) -> list:
        elements = []
        elements.append(Paragraph("CREDIT APPRAISAL MEMORANDUM", self.styles["CAMTitle"]))
        elements.append(Spacer(1, 4 * mm))

        header_data = [
            ["Applicant:", applicant_name,
             "Date:", datetime.now().strftime("%d-%b-%Y")],
            ["Credit Score:", f"{score_result['credit_score']}/100",
             "Decision:", score_result["decision"]],
            ["Loan Limit:", f"₹{score_result['loan_limit']:,.0f}",
             "Risk Premium:", f"{score_result['risk_premium_pct']:.2f}%"],
        ]

        t = Table(header_data, colWidths=[80, 150, 80, 150])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8eaf6")),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 6 * mm))
        return elements

    # ------------------------------------------------------------------
    def _executive_summary(self, score_result, financials) -> list:
        elements = []
        elements.append(Paragraph("1. Executive Summary", self.styles["SectionHead"]))

        decision_color = "#2e7d32" if score_result["decision"] == "APPROVE" else "#c62828"
        summary_text = (
            f"The applicant has received a credit score of <b>{score_result['credit_score']}/100</b> "
            f"resulting in a <font color='{decision_color}'><b>{score_result['decision']}</b></font> recommendation. "
            f"Revenue stands at ₹{financials.get('revenue', 0):,.0f} with a net margin of "
            f"{financials.get('net_margin', 0):.1%}. "
            f"The recommended loan limit is ₹{score_result['loan_limit']:,.0f} at a risk premium "
            f"of {score_result['risk_premium_pct']:.2f}%."
        )
        elements.append(Paragraph(summary_text, self.styles["CAMBody"]))
        elements.append(Spacer(1, 4 * mm))
        return elements

    # ------------------------------------------------------------------
    def _five_cs_section(self, score_result) -> list:
        elements = []
        elements.append(Paragraph("2. Five Cs Analysis", self.styles["SectionHead"]))

        five_cs = score_result.get("five_cs", {})
        table_data = [["Parameter", "Score", "Weight", "Weighted", "Rationale"]]
        weights = self.config.get("five_cs", {})

        for c_name in ["character", "capacity", "capital", "collateral", "conditions"]:
            data = five_cs.get(c_name, {"score": 0, "rationale": "N/A"})
            w = weights.get(f"{c_name}_weight", 0.20)
            weighted = data["score"] * w
            table_data.append([
                c_name.title(),
                f"{data['score']:.1f}",
                f"{w:.0%}",
                f"{weighted:.1f}",
                Paragraph(data["rationale"], self.styles["CAMSmall"]),
            ])

        t = Table(table_data, colWidths=[70, 50, 50, 55, 235])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#283593")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 4 * mm))
        return elements

    # ------------------------------------------------------------------
    def _financial_highlights(self, financials) -> list:
        elements = []
        elements.append(Paragraph("3. Financial Highlights", self.styles["SectionHead"]))

        rows = [["Metric", "Value"]]
        display = {
            "Revenue": ("revenue", "₹{:,.0f}"),
            "Net Profit": ("net_profit", "₹{:,.0f}"),
            "EBITDA": ("ebitda", "₹{:,.0f}"),
            "Total Assets": ("total_assets", "₹{:,.0f}"),
            "Net Worth": ("net_worth", "₹{:,.0f}"),
            "Current Ratio": ("current_ratio", "{:.2f}"),
            "Debt-to-Equity": ("debt_to_equity", "{:.2f}"),
            "Interest Coverage": ("interest_coverage", "{:.1f}x"),
            "Net Margin": ("net_margin", "{:.1%}"),
        }
        for label, (key, fmt) in display.items():
            val = financials.get(key, 0)
            rows.append([label, fmt.format(val)])

        t = Table(rows, colWidths=[180, 280])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#283593")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 4 * mm))
        return elements

    # ------------------------------------------------------------------
    def _fraud_section(self, fraud_result) -> list:
        elements = []
        elements.append(Paragraph("4. Fraud & Risk Analysis", self.styles["SectionHead"]))

        fs = fraud_result.get("fraud_score", 0)
        flags = fraud_result.get("total_flags", 0)
        high = fraud_result.get("high_severity_count", 0)
        circular = fraud_result.get("circular_trading", [])

        color = "#2e7d32" if fs < 30 else "#f57f17" if fs < 60 else "#c62828"
        text = (
            f"Fraud score: <font color='{color}'><b>{fs}/100</b></font>. "
            f"Total flags: {flags} (High: {high}). "
        )
        if circular:
            text += f"Circular trading cycles detected: {len(circular)}."
        else:
            text += "No circular trading detected."

        elements.append(Paragraph(text, self.styles["CAMBody"]))
        elements.append(Spacer(1, 4 * mm))
        return elements

    # ------------------------------------------------------------------
    def _recommendation(self, score_result) -> list:
        elements = []
        elements.append(Paragraph("5. Recommendation", self.styles["SectionHead"]))

        narrative = score_result.get("narrative", "No narrative generated.")
        # Wrap long narrative into paragraphs
        for para in narrative.split("\n"):
            para = para.strip()
            if para:
                elements.append(Paragraph(para, self.styles["CAMBody"]))
                elements.append(Spacer(1, 2 * mm))

        return elements

    # ------------------------------------------------------------------
    def _footer(self) -> list:
        elements = []
        elements.append(Spacer(1, 10 * mm))
        elements.append(Paragraph(
            f"Generated by Credit Decision Engine v1.0 | {datetime.now().strftime('%d-%b-%Y %H:%M')} | "
            "This is an AI-assisted analysis — final decisions require human review.",
            self.styles["CAMSmall"],
        ))
        return elements
