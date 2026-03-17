# Credit Decision Engine - C4 Diagrams (Mermaid)

Use these in any Mermaid-compatible tool (mermaid.live, GitHub, Notion, etc.)

---

## 1. System Context Diagram

```mermaid
C4Context
    title System Context - Credit Decision Engine

    Person(officer, "Credit Officer", "Uploads financial docs and reviews credit decisions")
    System(engine, "Credit Decision Engine", "AI-powered credit analysis system using transformer models on 4GB VRAM GPU. Automates APPROVE/REJECT decisions.")
    System_Ext(gpu, "NVIDIA GPU", "CUDA 12.1 - provides inference acceleration (~3.2GB VRAM)")
    System_Ext(hf, "HuggingFace Hub", "Pre-trained model weights: TinyLlama, DistilBERT, MiniLM")

    Rel(officer, engine, "Uploads PDF, GST CSV, Bank CSV, Notes", "Browser / Gradio")
    Rel(engine, officer, "Returns decision, Five Cs, CAM PDF", "HTTP")
    Rel(engine, gpu, "Model inference", "PyTorch CUDA")
    Rel(engine, hf, "Downloads models", "HTTPS")
```

---

## 2. Container Diagram

```mermaid
C4Container
    title Container Diagram - Credit Decision Engine

    Person(officer, "Credit Officer", "Reviews credit applications")

    System_Boundary(engine, "Credit Decision Engine") {
        Container(ui, "Gradio Web UI", "Python / Gradio 4.44", "Multi-tab interface: Decision, Five Cs, Narrative, Status")
        Container(parser, "PDF Parser", "DistilBERT + PyMuPDF", "Extracts 15 financial metrics, 5 ratios, risk indicators. ~400MB VRAM")
        Container(fraud, "Fraud Detector", "NetworkX + Pandas", "Graph-based: circular trading, z-score anomalies, concentration risk")
        Container(rag, "Research RAG", "FAISS + MiniLM-L6-v2", "384-dim embeddings, top-k document retrieval. ~200MB VRAM")
        Container(scorer, "Credit Scorer", "TinyLlama-1.1B 4-bit", "Five Cs rule engine + LLM narrative. ~1.2GB VRAM")
        Container(cam, "CAM Generator", "ReportLab", "Professional Credit Appraisal Memorandum PDF")
        ContainerDb(db, "Decision DB", "SQLite3", "Stores all credit decisions")
        ContainerDb(faiss, "Vector Index", "FAISS", "Document embeddings store")
    }

    Rel(officer, ui, "Upload docs", "Browser")
    Rel(ui, parser, "Step 1: Parse PDF")
    Rel(ui, fraud, "Step 2: Detect fraud")
    Rel(ui, rag, "Step 4: Retrieve context")
    Rel(ui, scorer, "Step 5: Score application")
    Rel(ui, cam, "Step 7: Generate report")
    Rel(ui, db, "Step 6: Save decision")
    Rel(rag, faiss, "Query embeddings")
    Rel(ui, officer, "Decision + CAM PDF", "Browser")
```

---

## 3. Full Pipeline Flow Diagram

```mermaid
flowchart TB
    subgraph INPUT["📥 INPUTS"]
        PDF["Financial PDF<br/>(Annual Reports)"]
        GST["GST Transactions CSV<br/>(seller_gstin, buyer_gstin, amount)"]
        BANK["Bank Statements CSV<br/>(date, debit, credit, balance)"]
        NOTES["Officer Notes<br/>(Free text observations)"]
    end

    subgraph STEP1["Step 1: PDF PARSING — DistilBERT + PyMuPDF"]
        direction TB
        S1A["Extract raw text<br/>from PDF bytes"]
        S1B["Regex extraction<br/>15 financial metrics"]
        S1C["Derive 5 ratios<br/>D/A, D/E, CR, ICR, NM"]
        S1D["Risk detection<br/>14 risk + 10 positive keywords"]
        S1E["Section classification<br/>DistilBERT zero-shot NLP"]
        S1A --> S1B --> S1C
        S1A --> S1D
        S1A --> S1E
    end

    subgraph STEP2["Step 2: FRAUD DETECTION — NetworkX Graph"]
        direction TB
        S2A["Build DiGraph<br/>GSTIN nodes → transaction edges"]
        S2B["Circular Trading<br/>Detect cycles (3-6 entities)"]
        S2C["Amount Anomalies<br/>Z-score > 2σ detection"]
        S2D["Concentration Risk<br/>> 70% single counterparty"]
        S2E["Fraud Score<br/>HIGH×25 + MEDIUM×10"]
        S2A --> S2B & S2C & S2D
        S2B & S2C & S2D --> S2E
    end

    subgraph STEP3["Step 3: BANK ANALYSIS — Pandas"]
        direction TB
        S3A["Calculate avg_balance<br/>total_inflow, total_outflow"]
        S3B["Compute EMI-to-income<br/>ratio"]
        S3A --> S3B
    end

    subgraph STEP4["Step 4: RAG CONTEXT — FAISS + MiniLM"]
        direction TB
        S4A["Query FAISS index<br/>384-dim cosine similarity"]
        S4B["Retrieve top-5<br/>relevant document chunks"]
        S4C["Format context<br/>for LLM prompt"]
        S4A --> S4B --> S4C
    end

    subgraph STEP5["Step 5: CREDIT SCORING — TinyLlama 4-bit"]
        direction TB
        S5A["Five Cs Rule Engine"]
        S5B["Character 20%<br/>100 - fraud×1.5"]
        S5C["Capacity 25%<br/>Net margin + ICR"]
        S5D["Capital 20%<br/>D/E ratio + Net worth"]
        S5E["Collateral 15%<br/>Current ratio + Assets"]
        S5F["Conditions 20%<br/>Bank balance + EMI"]
        S5G["Weighted Score = Σ(Ci × Wi)"]
        S5H{"Score >= 60?"}
        S5I["✅ APPROVE"]
        S5J["⚠️ REVIEW<br/>(40-60)"]
        S5K["❌ REJECT<br/>(<= 40)"]
        S5L["Loan Limit =<br/>Revenue × 0.4 × Score/100"]
        S5M["Risk Premium =<br/>2% + (100-Score) × 0.05"]
        S5N["AI Narrative<br/>TinyLlama inference"]
        S5A --> S5B & S5C & S5D & S5E & S5F
        S5B & S5C & S5D & S5E & S5F --> S5G --> S5H
        S5H -->|"Yes"| S5I
        S5H -->|"40-60"| S5J
        S5H -->|"No"| S5K
        S5G --> S5L & S5M & S5N
    end

    subgraph STEP6["Step 6: SAVE DECISION"]
        DB[("SQLite DB<br/>data/demo.sqlite")]
    end

    subgraph STEP7["Step 7: CAM PDF — ReportLab"]
        direction TB
        S7A["Header + Executive Summary"]
        S7B["Five Cs Analysis Table"]
        S7C["Financial Highlights"]
        S7D["Fraud & Risk Analysis"]
        S7E["AI Recommendation"]
        S7A --> S7B --> S7C --> S7D --> S7E
    end

    subgraph OUTPUT["📤 OUTPUTS"]
        O1["Decision Tab<br/>APPROVE/REJECT + Score + Loan Limit"]
        O2["Five Cs Tab<br/>Visual score bars per dimension"]
        O3["Narrative Tab<br/>AI-generated credit analysis"]
        O4["Status Tab<br/>Pipeline execution log"]
        O5["CAM PDF Download<br/>Professional credit memo"]
    end

    PDF --> STEP1
    GST --> STEP2
    BANK --> STEP3
    NOTES --> STEP5

    STEP1 --> STEP5
    STEP2 --> STEP5
    STEP3 --> STEP5
    STEP4 --> STEP5

    STEP5 --> STEP6
    STEP5 --> STEP7

    STEP6 --> OUTPUT
    STEP7 --> OUTPUT

    style INPUT fill:#e1f5fe,stroke:#0288d1,stroke-width:2px
    style STEP1 fill:#fff3e0,stroke:#ff9800,stroke-width:2px
    style STEP2 fill:#fce4ec,stroke:#e91e63,stroke-width:2px
    style STEP3 fill:#e8f5e9,stroke:#4caf50,stroke-width:2px
    style STEP4 fill:#f3e5f5,stroke:#9c27b0,stroke-width:2px
    style STEP5 fill:#fff9c4,stroke:#fbc02d,stroke-width:2px
    style STEP6 fill:#e0f2f1,stroke:#009688,stroke-width:2px
    style STEP7 fill:#e8eaf6,stroke:#3f51b5,stroke-width:2px
    style OUTPUT fill:#e1f5fe,stroke:#0288d1,stroke-width:2px
```

---

## 4. Component Diagram - Scorer (Five Cs Breakdown)

```mermaid
flowchart LR
    subgraph Inputs
        FIN["Financials<br/>Revenue, Profit,<br/>EBITDA, Assets..."]
        FRD["Fraud Result<br/>Score 0-100,<br/>Flags, Cycles"]
        BNK["Bank Metrics<br/>Avg Balance,<br/>EMI Ratio"]
        RAG["RAG Context<br/>Top-5 doc chunks"]
        NTS["Officer Notes<br/>Free text"]
    end

    subgraph FiveCs["Five Cs Rule Engine"]
        C1["CHARACTER<br/>Weight: 20%<br/>━━━━━━━━━<br/>Base: 100 - fraud×1.5<br/>+5 per positive keyword"]
        C2["CAPACITY<br/>Weight: 25%<br/>━━━━━━━━━<br/>Net Margin > 10%: +20<br/>ICR > 3×: +15"]
        C3["CAPITAL<br/>Weight: 20%<br/>━━━━━━━━━<br/>D/E < 1: +25<br/>Net Worth > 0: +10"]
        C4["COLLATERAL<br/>Weight: 15%<br/>━━━━━━━━━<br/>CR > 2: +20<br/>Assets > ₹10cr: +15"]
        C5["CONDITIONS<br/>Weight: 20%<br/>━━━━━━━━━<br/>Balance > ₹20L: +15<br/>EMI > 50%: -20"]
    end

    subgraph Decision
        SCORE["Credit Score<br/>= Σ(Ci × Wi)"]
        DEC{"Decision"}
        APP["✅ APPROVE<br/>(≥ 60)"]
        REV["⚠️ REVIEW<br/>(40-60)"]
        REJ["❌ REJECT<br/>(≤ 40)"]
        LOAN["Loan Limit<br/>Rev × 0.4 × Score/100"]
        RISK["Risk Premium<br/>2% + (100-Score)×0.05"]
        NARR["TinyLlama<br/>AI Narrative"]
    end

    FRD & NTS --> C1
    FIN --> C2 & C3 & C4
    BNK --> C5
    C1 & C2 & C3 & C4 & C5 --> SCORE
    SCORE --> DEC
    DEC --> APP & REV & REJ
    SCORE --> LOAN & RISK
    RAG & FIN & FRD --> NARR
```

---

## 5. Sequence Diagram

```mermaid
sequenceDiagram
    actor Officer as Credit Officer
    participant UI as Gradio UI<br/>(app.py)
    participant Parser as PDF Parser<br/>(DistilBERT)
    participant Fraud as Fraud Detector<br/>(NetworkX)
    participant Bank as Bank Analyzer<br/>(Pandas)
    participant RAG as Research RAG<br/>(FAISS)
    participant Scorer as Credit Scorer<br/>(TinyLlama)
    participant DB as SQLite DB
    participant CAM as CAM Generator<br/>(ReportLab)

    Officer->>UI: Upload PDF + GST CSV + Bank CSV + Notes

    rect rgb(255, 243, 224)
        Note over UI,Parser: Step 1: Document Parsing
        UI->>Parser: parse(pdf_bytes)
        Parser->>Parser: extract_text_from_bytes()
        Parser->>Parser: extract_financials() → 15 metrics + 5 ratios
        Parser->>Parser: detect_risks() → 14 risk keywords
        Parser->>Parser: classify_sections() → DistilBERT zero-shot
        Parser-->>UI: {financials, risks, sections}
    end

    rect rgb(252, 228, 236)
        Note over UI,Fraud: Step 2: Fraud Detection
        UI->>Fraud: analyze(gst_dataframe)
        Fraud->>Fraud: build_graph() → GSTIN DiGraph
        Fraud->>Fraud: detect_circular_trading()
        Fraud->>Fraud: detect_amount_anomalies()
        Fraud->>Fraud: detect_concentration_risk()
        Fraud-->>UI: {fraud_score, flags, cycles}
    end

    rect rgb(232, 245, 233)
        Note over UI,Bank: Step 3: Bank Analysis
        UI->>Bank: analyze_bank_csv(bank_df)
        Bank-->>UI: {avg_balance, inflow, outflow, emi_ratio}
    end

    rect rgb(243, 229, 245)
        Note over UI,RAG: Step 4: RAG Context
        UI->>RAG: build_context("credit risk for {applicant}")
        RAG->>RAG: FAISS L2 search → top-5 chunks
        RAG-->>UI: formatted_context_string
    end

    rect rgb(255, 249, 196)
        Note over UI,Scorer: Step 5: Credit Scoring
        UI->>Scorer: score(financials, fraud, bank, rag, notes)
        Scorer->>Scorer: _compute_five_cs() → weighted scores
        Scorer->>Scorer: Decision: APPROVE/REVIEW/REJECT
        Scorer->>Scorer: Calculate loan_limit & risk_premium
        Scorer->>Scorer: _generate_narrative() → TinyLlama inference
        Scorer-->>UI: {score, decision, loan_limit, five_cs, narrative}
    end

    rect rgb(224, 242, 241)
        Note over UI,DB: Step 6: Save Decision
        UI->>DB: INSERT decision record
    end

    rect rgb(232, 234, 246)
        Note over UI,CAM: Step 7: Generate CAM PDF
        UI->>CAM: generate(results, financials, fraud, name)
        CAM->>CAM: Build header + Five Cs table + financials
        CAM-->>UI: cam_pdf_bytes + file_path
    end

    UI-->>Officer: Decision + Five Cs + Narrative + Status + CAM PDF
```

---

## 6. Technology Stack Diagram

```mermaid
block-beta
    columns 3

    block:ui["🖥️ PRESENTATION LAYER"]:3
        Gradio["Gradio 4.44<br/>Web UI<br/>Port 7860"]
    end

    block:processing["⚙️ PROCESSING LAYER"]:3
        Parser["PDF Parser<br/>DistilBERT<br/>+ PyMuPDF"]
        Fraud["Fraud Detector<br/>NetworkX<br/>+ Pandas"]
        Scorer["Credit Scorer<br/>TinyLlama-1.1B<br/>4-bit NF4"]
    end

    block:data["💾 DATA LAYER"]:3
        FAISS["FAISS Index<br/>384-dim<br/>MiniLM-L6-v2"]
        SQLite["SQLite DB<br/>Decision Log"]
        ReportLab["ReportLab<br/>CAM PDF<br/>Generator"]
    end

    block:infra["🏗️ INFRASTRUCTURE"]:3
        PyTorch["PyTorch 2.4<br/>CUDA 12.1"]
        HF["HuggingFace<br/>Transformers 4.44"]
        BnB["BitsAndBytes<br/>4-bit Quantization"]
    end

    style ui fill:#e3f2fd,stroke:#1565c0
    style processing fill:#fff3e0,stroke:#ef6c00
    style data fill:#e8f5e9,stroke:#2e7d32
    style infra fill:#fce4ec,stroke:#c62828
```
