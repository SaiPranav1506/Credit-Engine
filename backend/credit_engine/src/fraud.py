"""NetworkX-based circular trading and fraud detection on GST transaction graphs."""

import itertools
import pandas as pd
import networkx as nx
import numpy as np


class FraudDetector:
    """Builds a directed transaction graph and detects circular trading + anomalies."""

    def __init__(self, config: dict):
        self.config = config
        fraud_cfg = config.get("fraud", {})
        self.circular_threshold = fraud_cfg.get("circular_trade_threshold", 0.7)
        self.min_cycle = fraud_cfg.get("min_cycle_length", 3)
        self.max_cycle = fraud_cfg.get("max_cycle_length", 6)
        self.suspicious_std = fraud_cfg.get("suspicious_amount_std", 2.0)
        self.graph = nx.DiGraph()

    # ------------------------------------------------------------------
    def build_graph(self, gst_df: pd.DataFrame) -> nx.DiGraph:
        """Build directed graph from GST transactions DataFrame."""
        self.graph = nx.DiGraph()

        for _, row in gst_df.iterrows():
            seller = str(row.get("seller_gstin", "")).strip()
            buyer = str(row.get("buyer_gstin", "")).strip()
            amount = float(row.get("taxable_value", 0))

            if not seller or not buyer or seller == buyer:
                continue

            if self.graph.has_edge(seller, buyer):
                self.graph[seller][buyer]["weight"] += amount
                self.graph[seller][buyer]["count"] += 1
                self.graph[seller][buyer]["invoices"].append(
                    str(row.get("invoice_number", ""))
                )
            else:
                self.graph.add_edge(
                    seller, buyer,
                    weight=amount,
                    count=1,
                    invoices=[str(row.get("invoice_number", ""))],
                )

        return self.graph

    # ------------------------------------------------------------------
    def detect_circular_trading(self) -> list:
        """Find cycles in the transaction graph (circular trading)."""
        cycles_found = []
        try:
            all_cycles = list(nx.simple_cycles(self.graph))
        except Exception:
            all_cycles = []

        for cycle in all_cycles:
            length = len(cycle)
            if self.min_cycle <= length <= self.max_cycle:
                cycle_amount = self._get_cycle_amount(cycle)
                cycles_found.append({
                    "entities": cycle,
                    "length": length,
                    "total_amount": cycle_amount,
                    "type": "circular_trading",
                    "severity": "HIGH" if length >= 4 else "MEDIUM",
                })

        return cycles_found

    # ------------------------------------------------------------------
    def detect_amount_anomalies(self, gst_df: pd.DataFrame) -> list:
        """Detect statistically anomalous transaction amounts."""
        anomalies = []
        if gst_df.empty or "taxable_value" not in gst_df.columns:
            return anomalies

        amounts = gst_df["taxable_value"].astype(float)
        mean_amt = amounts.mean()
        std_amt = amounts.std()

        if std_amt == 0:
            return anomalies

        for idx, row in gst_df.iterrows():
            val = float(row["taxable_value"])
            z_score = (val - mean_amt) / std_amt
            if abs(z_score) > self.suspicious_std:
                anomalies.append({
                    "invoice": str(row.get("invoice_number", "")),
                    "seller": str(row.get("seller_gstin", "")),
                    "buyer": str(row.get("buyer_gstin", "")),
                    "amount": val,
                    "z_score": round(z_score, 2),
                    "type": "amount_anomaly",
                    "severity": "HIGH" if abs(z_score) > 3 else "MEDIUM",
                })

        return anomalies

    # ------------------------------------------------------------------
    def detect_concentration_risk(self) -> list:
        """Detect entities with high transaction concentration (single counterparty)."""
        risks = []
        for node in self.graph.nodes():
            out_edges = list(self.graph.out_edges(node, data=True))
            in_edges = list(self.graph.in_edges(node, data=True))

            total_out = sum(d["weight"] for _, _, d in out_edges) if out_edges else 0
            total_in = sum(d["weight"] for _, _, d in in_edges) if in_edges else 0

            # Check outgoing concentration
            for _, target, data in out_edges:
                if total_out > 0 and data["weight"] / total_out > self.circular_threshold:
                    risks.append({
                        "entity": node,
                        "counterparty": target,
                        "concentration": round(data["weight"] / total_out, 2),
                        "direction": "outgoing",
                        "type": "concentration_risk",
                        "severity": "MEDIUM",
                    })

            # Check incoming concentration
            for source, _, data in in_edges:
                if total_in > 0 and data["weight"] / total_in > self.circular_threshold:
                    risks.append({
                        "entity": node,
                        "counterparty": source,
                        "concentration": round(data["weight"] / total_in, 2),
                        "direction": "incoming",
                        "type": "concentration_risk",
                        "severity": "MEDIUM",
                    })

        return risks

    # ------------------------------------------------------------------
    def analyze(self, gst_df: pd.DataFrame) -> dict:
        """Full fraud analysis pipeline."""
        self.build_graph(gst_df)

        circular = self.detect_circular_trading()
        anomalies = self.detect_amount_anomalies(gst_df)
        concentration = self.detect_concentration_risk()

        all_flags = circular + anomalies + concentration
        high_count = sum(1 for f in all_flags if f.get("severity") == "HIGH")
        med_count = sum(1 for f in all_flags if f.get("severity") == "MEDIUM")

        # Fraud score: 0 (clean) to 100 (highly suspicious)
        fraud_score = min(100, high_count * 25 + med_count * 10)

        return {
            "fraud_score": fraud_score,
            "circular_trading": circular,
            "amount_anomalies": anomalies,
            "concentration_risks": concentration,
            "total_flags": len(all_flags),
            "high_severity_count": high_count,
            "medium_severity_count": med_count,
            "graph_stats": {
                "nodes": self.graph.number_of_nodes(),
                "edges": self.graph.number_of_edges(),
                "density": round(nx.density(self.graph), 4) if self.graph.number_of_nodes() > 0 else 0,
            },
        }

    # ------------------------------------------------------------------
    def _get_cycle_amount(self, cycle: list) -> float:
        """Sum of edge weights along a cycle."""
        total = 0
        for i in range(len(cycle)):
            u = cycle[i]
            v = cycle[(i + 1) % len(cycle)]
            if self.graph.has_edge(u, v):
                total += self.graph[u][v]["weight"]
        return total
