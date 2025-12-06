"""
RAG Engine module for simple knowledge base retrieval.
"""
from typing import List, Dict
import os

class RAGEngine:
    """
    Simple RAG engine that performs substring matching on the knowledge base.
    """
    
    def __init__(self, kb_path: str = "knowledge_base.txt"):
        self.kb_path = kb_path
        self._load_kb()
        
    def _load_kb(self):
        try:
            if os.path.exists(self.kb_path):
                with open(self.kb_path, "r", encoding="utf-8") as f:
                    self.lines = [line.strip() for line in f.readlines() if line.strip()]
            else:
                self.lines = []
        except Exception:
            self.lines = []

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Search the knowledge base for lines containing the query terms.
        
        Args:
            query: The search query.
            top_k: Max number of results to return.
            
        Returns:
            List of dictionaries with 'text', 'source', and 'line_no'.
        """
        query_terms = query.lower().split()
        results = []
        
        for i, line in enumerate(self.lines):
            line_lower = line.lower()
            # Simple scoring: count how many query terms are in the line
            score = sum(1 for term in query_terms if term in line_lower)
            
            if score > 0:
                results.append({
                    "text": line,
                    "source": "knowledge_base.txt",
                    "line_no": i + 1,
                    "score": score
                })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return results[:top_k]
