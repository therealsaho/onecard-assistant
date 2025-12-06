"""
Script to build the RAG index.
Usage: python scripts/build_rag_index.py --kb data/knowledge_base.txt --out data/rag_index
"""
import argparse
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator.embedding_rag import EmbeddingRAG

def main():
    parser = argparse.ArgumentParser(description="Build RAG Index")
    parser.add_argument("--kb", default="data/knowledge_base.txt", help="Path to knowledge base file")
    parser.add_argument("--out", default="data/rag_index", help="Output directory for index")
    parser.add_argument("--rebuild", action="store_true", help="Force rebuild")
    
    args = parser.parse_args()
    
    print(f"Initializing RAG with KB: {args.kb} and Index Dir: {args.out}")
    
    rag = EmbeddingRAG(kb_path=args.kb, index_dir=args.out)
    rag.build_index(rebuild=args.rebuild)
    
    print("Done.")

if __name__ == "__main__":
    main()
