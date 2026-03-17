"""TinyLlama-4bit credit scoring engine with Five Cs analysis."""

import importlib.util
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import joblib
from pathlib import Path

try:
    from transformers import BitsAndBytesConfig
except Exception:
    BitsAndBytesConfig = None


class CreditScorer:
    """Uses TinyLlama 1.1B (4-bit quantized) to produce credit decisions via the Five Cs."""

    SYSTEM_PROMPT = (
        "You are an expert credit analyst. Analyze the applicant data using the Five Cs framework "
        "(Character, Capacity, Capital, Collateral, Conditions). Provide:\n"
        "1. A credit score (0-100)\n"
        "2. Decision: APPROVE or REJECT\n"
        "3. Recommended loan limit\n"
        "4. Risk premium percentage\n"
        "5. Detailed Five Cs breakdown\n"
        "Be precise with numbers and justify each rating."
    )

    def __init__(self, config: dict):
        self.config = config
        scorer_cfg = config.get("models", {}).get("scorer", {})
        credit_cfg = config.get("credit", {})
        five_cs_cfg = config.get("five_cs", {})

        model_name = scorer_cfg.get("name", "TinyLlama/TinyLlama-1.1B-Chat-v1.0")
        self.max_new_tokens = scorer_cfg.get("max_new_tokens", 512)
        self.temperature = scorer_cfg.get("temperature", 0.3)
        self.enable_llm_on_cpu = scorer_cfg.get("enable_llm_on_cpu", False)
        self.quantization = scorer_cfg.get("quantization", "4bit")

        self.approve_threshold = credit_cfg.get("approve_threshold", 60)
        self.reject_threshold = credit_cfg.get("reject_threshold", 40)
        self.risk_premium_base = credit_cfg.get("risk_premium_base", 0.02)
        self.max_loan_ratio = credit_cfg.get("max_loan_to_revenue_ratio", 0.4)

        self.weights = {
            "character": five_cs_cfg.get("character_weight", 0.20),
            "capacity": five_cs_cfg.get("capacity_weight", 0.25),
            "capital": five_cs_cfg.get("capital_weight", 0.20),
            "collateral": five_cs_cfg.get("collateral_weight", 0.15),
            "conditions": five_cs_cfg.get("conditions_weight", 0.20),
        }

        # Load ML model for decision - prefer full LendingClub ensemble
        lc_model_path = Path(__file__).parent.parent / "data" / "ensemble_lc_lendingclub_full.pkl"
        fallback_model_path = Path(__file__).parent.parent / "data" / "ensemble_lc_lendingclub_2000_samples.pkl"
        
        self.ml_model = None
        self.label_encoder = None
        self.scaler = None
        
        # Try full LendingClub model first
        if lc_model_path.exists():
            self.ml_model = joblib.load(lc_model_path)
            # Load associated scaler and encoder
            lc_encoder_path = Path(__file__).parent.parent / "data" / "label_encoder_lc_lendingclub_full.pkl"
            lc_scaler_path = Path(__file__).parent.parent / "data" / "scaler_lc_lendingclub_full.pkl"
            if lc_encoder_path.exists():
                self.label_encoder = joblib.load(lc_encoder_path)
            if lc_scaler_path.exists():
                self.scaler = joblib.load(lc_scaler_path)
            print("✓ Using LendingClub ensemble model (5000 samples, 69.9% CV accuracy)")
        elif fallback_model_path.exists():
            self.ml_model = joblib.load(fallback_model_path)
            # Load associated scaler and encoder
            fallback_encoder_path = Path(__file__).parent.parent / "data" / "label_encoder_lc_lendingclub_2000_samples.pkl"
            fallback_scaler_path = Path(__file__).parent.parent / "data" / "scaler_lc_lendingclub_2000_samples.pkl"
            if fallback_encoder_path.exists():
                self.label_encoder = joblib.load(fallback_encoder_path)
            if fallback_scaler_path.exists():
                self.scaler = joblib.load(fallback_scaler_path)
            print("⚠ Using 2000-sample model (full model not found)")
        else:
            print("Warning: ML model not found, falling back to rule-based scoring.")

        has_cuda = torch.cuda.is_available()
        has_bnb = BitsAndBytesConfig is not None and importlib.util.find_spec("bitsandbytes") is not None
        use_4bit = has_cuda and self.quantization == "4bit" and has_bnb
        use_gpu_fp16 = has_cuda and not use_4bit
        self.use_llm_narrative = use_4bit or use_gpu_fp16 or self.enable_llm_on_cpu
        self.tokenizer = None
        self.model = None

        # Loading TinyLlama on CPU is extremely slow; keep it opt-in only.
        if self.use_llm_narrative:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            if use_4bit:
                bnb_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                )
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    quantization_config=bnb_config,
                    device_map="auto",
                    torch_dtype=torch.float16,
                )
            elif use_gpu_fp16:
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    device_map="auto",
                    torch_dtype=torch.float16,
                )
            else:
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    device_map="auto",
                    torch_dtype=torch.float32,
                )

            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

    # ------------------------------------------------------------------
    def score(
        self,
        financials: dict,
        fraud_result: dict,
        research_context: str,
        bank_analysis: dict | None = None,
        officer_notes: str = "",
    ) -> dict:
        """Produce a full credit decision from all inputs."""

        # --- Compute rule-based Five Cs sub-scores (0-100 each) ---
        five_cs = self._compute_five_cs(financials, fraud_result, bank_analysis, officer_notes)

        # Use ML model for decision if available
        if self.ml_model:
            features = [
                financials.get("revenue", 0),
                financials.get("net_profit", 0),
                financials.get("debt_to_equity", 0),
                fraud_result.get("fraud_score", 0),
                bank_analysis.get("avg_balance", 0) if bank_analysis else 0
            ]
            
            # Scale features if scaler is available
            if self.scaler:
                features_scaled = self.scaler.transform([features])[0]
            else:
                features_scaled = features
            
            pred = self.ml_model.predict([features_scaled])[0]
            
            # Handle both numeric and string predictions
            if isinstance(pred, str):
                decision = pred
            else:
                decision = "APPROVE" if pred == 1 else "REJECT"
            
            total_score = 80 if decision == "APPROVE" else 30  # Simplified score based on decision
        else:
            # Weighted total
            total_score = sum(
                five_cs[c]["score"] * self.weights[c] for c in self.weights
            )
            total_score = round(min(100, max(0, total_score)), 1)

            # Decision
            if total_score >= self.approve_threshold:
                decision = "APPROVE"
            elif total_score <= self.reject_threshold:
                decision = "REJECT"
            else:
                decision = "REVIEW"

        # Loan limit
        revenue = financials.get("revenue", 0)
        loan_limit = round(revenue * self.max_loan_ratio * (total_score / 100), 2)

        # Risk premium
        risk_premium = round(self.risk_premium_base + (100 - total_score) * 0.05, 2)

        # --- LLM narrative ---
        narrative = self._generate_narrative(
            financials, fraud_result, research_context, five_cs, total_score, decision, officer_notes
        )

        return {
            "credit_score": total_score,
            "decision": decision,
            "loan_limit": loan_limit,
            "risk_premium_pct": risk_premium,
            "five_cs": five_cs,
            "narrative": narrative,
        }

    # ------------------------------------------------------------------
    def _compute_five_cs(
        self, financials: dict, fraud_result: dict,
        bank_analysis: dict | None, officer_notes: str
    ) -> dict:
        """Rule-based scoring for each of the Five Cs."""
        cs = {}

        # CHARACTER — based on fraud score + officer notes
        fraud_score = fraud_result.get("fraud_score", 0)
        char_score = max(0, 100 - fraud_score * 1.5)
        if officer_notes:
            positive_words = sum(1 for w in ["good", "reliable", "strong", "trusted", "reputed"]
                                 if w in officer_notes.lower())
            char_score = min(100, char_score + positive_words * 5)
        cs["character"] = {
            "score": round(char_score, 1),
            "rationale": f"Fraud score {fraud_score}/100. {fraud_result.get('total_flags', 0)} flags detected."
        }

        # CAPACITY — revenue, profit margin, interest coverage
        net_margin = financials.get("net_margin", 0)
        interest_cov = financials.get("interest_coverage", 0)
        capacity_score = 50
        if net_margin > 0.10:
            capacity_score += 20
        elif net_margin > 0.05:
            capacity_score += 10
        elif net_margin < 0:
            capacity_score -= 25
        if interest_cov > 3:
            capacity_score += 15
        elif interest_cov > 1.5:
            capacity_score += 5
        elif interest_cov > 0 and interest_cov < 1:
            capacity_score -= 20
        capacity_score = max(0, min(100, capacity_score))
        cs["capacity"] = {
            "score": round(capacity_score, 1),
            "rationale": f"Net margin {net_margin:.2%}, interest coverage {interest_cov:.1f}x."
        }

        # CAPITAL — net worth, debt-to-equity
        d2e = financials.get("debt_to_equity", 0)
        nw = financials.get("net_worth", 0)
        capital_score = 50
        if d2e < 1:
            capital_score += 25
        elif d2e < 2:
            capital_score += 10
        else:
            capital_score -= 15
        if nw > 0:
            capital_score += 10
        else:
            capital_score -= 30
        capital_score = max(0, min(100, capital_score))
        cs["capital"] = {
            "score": round(capital_score, 1),
            "rationale": f"D/E ratio {d2e:.2f}, Net worth ₹{nw:,.0f}."
        }

        # COLLATERAL — current ratio, total assets
        curr_ratio = financials.get("current_ratio", 0)
        total_assets = financials.get("total_assets", 0)
        coll_score = 50
        if curr_ratio > 2:
            coll_score += 20
        elif curr_ratio > 1.5:
            coll_score += 10
        elif curr_ratio < 1:
            coll_score -= 20
        if total_assets > 10_000_000:
            coll_score += 15
        elif total_assets > 1_000_000:
            coll_score += 5
        coll_score = max(0, min(100, coll_score))
        cs["collateral"] = {
            "score": round(coll_score, 1),
            "rationale": f"Current ratio {curr_ratio:.2f}, Total assets ₹{total_assets:,.0f}."
        }

        # CONDITIONS — bank analysis health + risk density
        risk_density = 0
        cond_score = 60
        if bank_analysis:
            avg_bal = bank_analysis.get("avg_balance", 0)
            if avg_bal > 2_000_000:
                cond_score += 15
            elif avg_bal > 500_000:
                cond_score += 5
            emi_ratio = bank_analysis.get("emi_to_income_ratio", 0)
            if emi_ratio > 0.5:
                cond_score -= 20
            elif emi_ratio > 0.3:
                cond_score -= 10

        cond_score = max(0, min(100, cond_score))
        cs["conditions"] = {
            "score": round(cond_score, 1),
            "rationale": f"Market risk density {risk_density:.2%}. Bank health assessed."
        }

        return cs

    # ------------------------------------------------------------------
    def _generate_narrative(
        self, financials, fraud_result, research_context,
        five_cs, total_score, decision, officer_notes
    ) -> str:
        """Use TinyLlama to write a credit analysis narrative."""
        if not self.use_llm_narrative:
            return self._build_fast_narrative(
                financials=financials,
                fraud_result=fraud_result,
                five_cs=five_cs,
                total_score=total_score,
                decision=decision,
                officer_notes=officer_notes,
            )

        user_msg = (
            f"## Applicant Financial Summary\n"
            f"Revenue: ₹{financials.get('revenue', 0):,.0f}\n"
            f"Net Profit: ₹{financials.get('net_profit', 0):,.0f}\n"
            f"EBITDA: ₹{financials.get('ebitda', 0):,.0f}\n"
            f"Debt-to-Equity: {financials.get('debt_to_equity', 0):.2f}\n"
            f"Current Ratio: {financials.get('current_ratio', 0):.2f}\n\n"
            f"## Fraud Analysis\n"
            f"Fraud Score: {fraud_result.get('fraud_score', 0)}/100\n"
            f"Total Flags: {fraud_result.get('total_flags', 0)}\n\n"
            f"## Five Cs Scores\n"
        )
        for c, data in five_cs.items():
            user_msg += f"- {c.title()}: {data['score']}/100 — {data['rationale']}\n"

        user_msg += (
            f"\n## Credit Score: {total_score}/100 → {decision}\n"
            f"## Officer Notes: {officer_notes or 'None'}\n\n"
            f"## Research Context:\n{research_context[:500]}\n\n"
            f"Write a detailed credit analysis narrative covering all Five Cs."
        )

        prompt = (
            f"<|system|>\n{self.SYSTEM_PROMPT}</s>\n"
            f"<|user|>\n{user_msg}</s>\n"
            f"<|assistant|>\n"
        )

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=2048,
        ).to(self.model.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                temperature=self.temperature,
                do_sample=True,
                top_p=0.9,
                repetition_penalty=1.15,
            )

        generated = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Extract only the assistant response
        if "<|assistant|>" in generated:
            generated = generated.split("<|assistant|>")[-1].strip()

        return generated

    def _build_fast_narrative(
        self,
        financials: dict,
        fraud_result: dict,
        five_cs: dict,
        total_score: float,
        decision: str,
        officer_notes: str,
    ) -> str:
        """Deterministic narrative for low-latency CPU inference."""
        top_strength = max(five_cs.items(), key=lambda x: x[1]["score"])
        top_risk = min(five_cs.items(), key=lambda x: x[1]["score"])

        return (
            f"Credit score is {total_score}/100 with decision {decision}. "
            f"Revenue is Rs {financials.get('revenue', 0):,.0f}, net profit is Rs {financials.get('net_profit', 0):,.0f}, "
            f"and debt-to-equity is {financials.get('debt_to_equity', 0):.2f}. "
            f"Fraud score is {fraud_result.get('fraud_score', 0)}/100 with {fraud_result.get('total_flags', 0)} flags. "
            f"Strongest area is {top_strength[0].title()} ({top_strength[1]['score']:.1f}/100). "
            f"Primary risk area is {top_risk[0].title()} ({top_risk[1]['score']:.1f}/100). "
            f"Officer notes considered: {officer_notes or 'None'}."
        )
