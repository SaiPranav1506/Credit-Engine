"""Train (build) the RAG index from local dataset folders."""

from pathlib import Path
import yaml

from src.research import ResearchRAG


def main() -> None:
    root = Path(__file__).resolve().parent
    config_path = root / "config.yaml"

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    paths_cfg = config.get("paths", {})
    data_dir = root / paths_cfg.get("data_dir", "data")
    local_dataset_dir = root / paths_cfg.get("dataset_dir", "dataset")
    external_dataset_dir = root.parent / paths_cfg.get("external_dataset_dir", "Dataset")

    index_path = root / paths_cfg.get("rag_index_path", "data/rag_index.faiss")
    docs_path = root / paths_cfg.get("rag_docs_path", "data/rag_docs.json")

    rag = ResearchRAG(config)

    for data_path in [data_dir, local_dataset_dir, external_dataset_dir]:
        rag.ingest_directory(str(data_path))

    rag.save(index_path=str(index_path), docs_path=str(docs_path))

    stats = rag.get_stats()
    print("RAG training completed.")
    print(f"Indexed chunks: {stats['total_chunks']}")
    print(f"FAISS index: {index_path}")
    print(f"Metadata: {docs_path}")


if __name__ == "__main__":
    main()
