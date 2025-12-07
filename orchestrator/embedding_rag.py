"""
Enhanced Embedding-based RAG Engine.
Supports chunking, persistence, mock/real embeddings, and hybrid fallback.
"""
import os
import json
import hashlib
import random
import math
from typing import List, Dict, Optional, Any
from config.embedding_settings import (
    EMBEDDING_PROVIDER,
    RUN_REAL_EMBEDDINGS,
    RAG_INDEX_DIR,
    RAG_MIN_SCORE,
    INDEX_VERSION
)
from llm.gemini_client import GeminiLLMClient

class EmbeddingRAG:
    """
    RAG engine using embeddings for semantic retrieval.
    """
    
    def __init__(self, kb_path: str = os.path.join("data", "knowledge_base.txt"), index_dir: str = RAG_INDEX_DIR):
        self.kb_path = kb_path
        self.index_dir = index_dir
        self.passages = []
        self.embeddings = [] # In-memory storage for mock/simple index
        
        self.llm_client = None
        if RUN_REAL_EMBEDDINGS:
            self.llm_client = GeminiLLMClient()
        
        # Ensure index dir exists
        os.makedirs(self.index_dir, exist_ok=True)
        
        # Load index if exists, otherwise load KB (lazy load or explicit build required)
        self._load_index()

    def _load_index(self):
        """Loads metadata and embeddings from disk."""
        metadata_path = os.path.join(self.index_dir, "metadata.json")
        
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("version") == INDEX_VERSION:
                        self.passages = data.get("passages", [])
                        # In a real scenario with Chroma/Faiss, we'd load the vector store here.
                        # For now, we'll re-compute mock embeddings on the fly or load them if we persisted them.
                        # To keep it simple for the prototype, we'll just rely on the passages metadata
                        # and re-compute mock embeddings in memory for search if needed, 
                        # or assume they are fast enough to generate.
                        pass
            except Exception as e:
                print(f"Failed to load RAG index: {e}")
        
        # If no index loaded, we might need to build it. 
        # But we won't auto-build on init to avoid startup delays.
        # The agent should handle empty index gracefully or we run the build script.

    def build_index(self, rebuild: bool = False):
        """
        Builds the index from the knowledge base.
        """
        if not rebuild and self.passages:
            return

        print(f"Building RAG index from {self.kb_path}...")
        
        # 1. Read KB
        if not os.path.exists(self.kb_path):
            print(f"KB file not found: {self.kb_path}")
            return
            
        with open(self.kb_path, "r", encoding="utf-8") as f:
            text = f.read()
            
        # 2. Chunk Text
        chunks = self._chunk_text(text)
        
        # 3. Create Passages
        self.passages = []
        for i, chunk in enumerate(chunks):
            passage = {
                "chunk_id": i,
                "text": chunk["text"],
                "source": "knowledge_base.txt",
                "line_no": chunk["line_start"], # Approximate
                "preview": chunk["text"][:120]
            }
            self.passages.append(passage)
            
            # In real mode, we would compute and persist embeddings here.
            
        # 4. Persist Metadata
        metadata = {
            "version": INDEX_VERSION,
            "passages": self.passages
        }
        with open(os.path.join(self.index_dir, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
            
        print(f"Index built with {len(self.passages)} passages.")

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Searches the index for relevant passages.
        """
        if not self.passages:
            # Try to build on the fly if empty (fallback)
            self.build_index()
            if not self.passages:
                return []

        query_embedding = self._get_embedding(query)
        
        scored_results = []
        
        for passage in self.passages:
            # Compute score
            doc_embedding = self._get_embedding(passage["text"])
            score = self._cosine_similarity(query_embedding, doc_embedding)
            
            if score >= RAG_MIN_SCORE:
                result = passage.copy()
                result["score"] = score
                scored_results.append(result)
        
        # Sort by score desc
        scored_results.sort(key=lambda x: x["score"], reverse=True)
        
        # Hybrid Fallback Check
        # If no results found or top score is low, try lexical fallback
        if not scored_results:
            return self._lexical_fallback(query, top_k)
            
        return scored_results[:top_k]

    def _chunk_text(self, text: str, chunk_size: int = 300, overlap: int = 50) -> List[Dict]:
        """
        Splits text into chunks. 
        Simple line-based chunking for now, can be upgraded to token-based.
        """
        lines = text.split('\n')
        chunks = []
        current_chunk = []
        current_length = 0
        chunk_start_line = 1
        current_line_idx = 0
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Estimate tokens (approx 4 chars per token)
            line_len = len(line) // 4
            
            if current_length + line_len > chunk_size and current_chunk:
                # Emit chunk
                chunks.append({
                    "text": "\n".join(current_chunk),
                    "line_start": chunk_start_line
                })
                
                # Handle overlap (keep last few lines)
                # Simple overlap: keep last line
                overlap_chunk = [current_chunk[-1]] if current_chunk else []
                current_chunk = overlap_chunk
                current_length = len(overlap_chunk[0]) // 4 if overlap_chunk else 0
                chunk_start_line = i + 1 # Approximate
            
            current_chunk.append(line)
            current_length += line_len
            
        if current_chunk:
            chunks.append({
                "text": "\n".join(current_chunk),
                "line_start": chunk_start_line
            })
            
        return chunks

    def _get_embedding(self, text: str) -> List[float]:
        """
        Generates an embedding for the text.
        Supports 'Mock Semantic' mode by mapping keywords to specific dimensions.
        """
        if RUN_REAL_EMBEDDINGS and self.llm_client:
            return self.llm_client.embed(text)
            
        # Mock Semantic Embedding
        # We use a 64-dim vector. We reserve the first few dims for specific concepts.
        # This allows "international" to match "forex" if they share a concept dim.
        
        vector = [0.0] * 64
        text_lower = text.lower()
        
        # Concept 0: Forex / International
        if any(w in text_lower for w in ["forex", "markup", "international", "abroad", "foreign"]):
            vector[0] = 1.0
            
        # Concept 1: Rewards / Points
        if any(w in text_lower for w in ["reward", "points", "cashback", "earn", "category", "categories"]):
            vector[1] = 1.0
            
        # Concept 2: Interest / Period
        if any(w in text_lower for w in ["interest", "period", "days", "billing", "due"]):
            vector[2] = 1.0
            
        # Concept 3: Block / Lost
        if any(w in text_lower for w in ["block", "lost", "stolen", "freeze"]):
            vector[3] = 1.0
            
        # Fill the rest with deterministic random noise to distinguish non-matching texts
        # Seed with hash of text
        seed = int(hashlib.sha256(text.encode('utf-8')).hexdigest(), 16) % (10**8)
        random.seed(seed)
        
        for i in range(4, 64):
            vector[i] = random.uniform(-0.1, 0.1) # Low noise
            
        # Normalize
        norm = math.sqrt(sum(x*x for x in vector))
        if norm > 0:
            vector = [x/norm for x in vector]
            
        return vector

    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        """Computes cosine similarity between two vectors."""
        dot_product = sum(a * b for a, b in zip(v1, v2))
        norm_a = math.sqrt(sum(a * a for a in v1))
        norm_b = math.sqrt(sum(b * b for b in v2))
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
            
        return dot_product / (norm_a * norm_b)

    def _lexical_fallback(self, query: str, top_k: int) -> List[Dict]:
        """
        Simple substring/keyword match fallback.
        """
        query_terms = query.lower().split()
        results = []
        
        for passage in self.passages:
            text_lower = passage["text"].lower()
            score = sum(1 for term in query_terms if term in text_lower)
            
            if score > 0:
                result = passage.copy()
                result["score"] = 0.1 + (score * 0.05) # Lower score range for lexical
                result["fallback"] = "lexical"
                results.append(result)
                
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
