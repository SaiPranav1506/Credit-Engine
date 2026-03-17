"""FAISS-based RAG (Retrieval-Augmented Generation) for local credit research documents."""

import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer


class ResearchRAG:
    """Embeds local documents into FAISS and retrieves relevant context for credit analysis."""

    def __init__(self, config: dict):
        self.config = config
        faiss_cfg = config.get("faiss", {})
        emb_cfg = config.get("models", {}).get("embeddings", {})

        self.embedding_dim = faiss_cfg.get("embedding_dim", 384)
        self.chunk_size = faiss_cfg.get("chunk_size", 256)
        self.chunk_overlap = faiss_cfg.get("chunk_overlap", 50)

        model_name = emb_cfg.get("name", "sentence-transformers/all-MiniLM-L6-v2")
        self.encoder = SentenceTransformer(model_name)

        # FAISS flat L2 index
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.documents: list[str] = []
        self.metadata: list[dict] = []

    # ------------------------------------------------------------------
    def add_document(self, text: str, source: str = "unknown"):
        """Chunk text and add to FAISS index."""
        chunks = self._chunk_text(text)
        if not chunks:
            return

        embeddings = self.encoder.encode(chunks, show_progress_bar=False)
        embeddings = np.array(embeddings, dtype="float32")
        self.index.add(embeddings)

        for chunk in chunks:
            self.documents.append(chunk)
            self.metadata.append({"source": source})

    def add_texts(self, texts: list[str], source: str = "batch"):
        """Add multiple pre-split text chunks."""
        if not texts:
            return
        embeddings = self.encoder.encode(texts, show_progress_bar=False)
        embeddings = np.array(embeddings, dtype="float32")
        self.index.add(embeddings)

        for t in texts:
            self.documents.append(t)
            self.metadata.append({"source": source})

    # ------------------------------------------------------------------
    def query(self, question: str, top_k: int = 5) -> list[dict]:
        """Retrieve the top_k most relevant chunks for a question."""
        if self.index.ntotal == 0:
            return []

        q_emb = self.encoder.encode([question], show_progress_bar=False)
        q_emb = np.array(q_emb, dtype="float32")

        distances, indices = self.index.search(q_emb, min(top_k, self.index.ntotal))

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < 0 or idx >= len(self.documents):
                continue
            results.append({
                "text": self.documents[idx],
                "source": self.metadata[idx]["source"],
                "distance": float(dist),
            })

        return results

    # ------------------------------------------------------------------
    def build_context(self, question: str, top_k: int = 5) -> str:
        """Return a formatted context string for the scorer LLM."""
        results = self.query(question, top_k)
        if not results:
            return "No relevant research documents found."

        context_parts = []
        for i, r in enumerate(results, 1):
            context_parts.append(
                f"[Source {i}: {r['source']}]\n{r['text']}"
            )

        return "\n\n".join(context_parts)

    # ------------------------------------------------------------------
    def ingest_directory(self, directory: str):
        """Ingest all .txt and .pdf files from a directory."""
        if not os.path.isdir(directory):
            return

        for fname in os.listdir(directory):
            fpath = os.path.join(directory, fname)
            if fname.lower().endswith(".txt"):
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    self.add_document(f.read(), source=fname)
            elif fname.lower().endswith(".pdf"):
                try:
                    import fitz
                    doc = fitz.open(fpath)
                    text = "".join(page.get_text() for page in doc)
                    doc.close()
                    self.add_document(text, source=fname)
                except Exception:
                    pass

    # ------------------------------------------------------------------
    def get_stats(self) -> dict:
        return {
            "total_chunks": self.index.ntotal,
            "embedding_dim": self.embedding_dim,
            "chunk_size": self.chunk_size,
        }

    def save(self, index_path: str, docs_path: str):
        """Persist FAISS index plus document/metadata store."""
        index_dir = os.path.dirname(index_path)
        docs_dir = os.path.dirname(docs_path)
        if index_dir:
            os.makedirs(index_dir, exist_ok=True)
        if docs_dir:
            os.makedirs(docs_dir, exist_ok=True)

        faiss.write_index(self.index, index_path)
        with open(docs_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "documents": self.documents,
                    "metadata": self.metadata,
                },
                f,
                ensure_ascii=True,
            )

    def load(self, index_path: str, docs_path: str) -> bool:
        """Load FAISS index plus document/metadata store if both exist."""
        if not (os.path.isfile(index_path) and os.path.isfile(docs_path)):
            return False

        self.index = faiss.read_index(index_path)
        with open(docs_path, "r", encoding="utf-8") as f:
            payload = json.load(f)

        self.documents = payload.get("documents", [])
        self.metadata = payload.get("metadata", [])
        return True

    # ------------------------------------------------------------------
    def _chunk_text(self, text: str) -> list[str]:
        """Split text into overlapping word-level chunks."""
        words = text.split()
        chunks = []
        step = max(1, self.chunk_size - self.chunk_overlap)
        for i in range(0, len(words), step):
            chunk = " ".join(words[i : i + self.chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        return chunks
