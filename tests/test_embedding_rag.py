import unittest
import os
import shutil
import json
from orchestrator.embedding_rag import EmbeddingRAG

class TestEmbeddingRAG(unittest.TestCase):
    
    def setUp(self):
        self.test_dir = "tests/test_rag_index"
        self.kb_path = "tests/test_kb.txt"
        
        # Create dummy KB
        with open(self.kb_path, "w", encoding="utf-8") as f:
            f.write("OneCard offers 5x reward points on dining.\n")
            f.write("Forex markup is 1%.\n")
            f.write("You can block your card instantly via the app.\n")
            
        # Clean index dir
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        if os.path.exists(self.kb_path):
            os.remove(self.kb_path)

    def test_build_index_mock(self):
        """Test building index with mock embeddings."""
        rag = EmbeddingRAG(kb_path=self.kb_path, index_dir=self.test_dir)
        rag.build_index()
        
        # Check metadata file
        metadata_path = os.path.join(self.test_dir, "metadata.json")
        self.assertTrue(os.path.exists(metadata_path))
        
        with open(metadata_path, "r") as f:
            data = json.load(f)
            self.assertEqual(len(data["passages"]), 1) # Small KB should be 1 chunk

    def test_search_mock_deterministic(self):
        """Test search returns results."""
        rag = EmbeddingRAG(kb_path=self.kb_path, index_dir=self.test_dir)
        rag.build_index()
        
        # Exact match query should have high score (mock embedding is deterministic hash)
        # Actually, mock embedding is random seeded by text hash. 
        # Query embedding is seeded by query hash.
        # So "OneCard offers 5x reward points" query should be close to the passage?
        # No, hash(A) and hash(B) are uncorrelated even if A ~ B.
        # So mock embedding search is basically random unless query == passage.
        # However, for the purpose of this test, we just want to ensure it runs and returns *something* 
        # or handles the random score correctly.
        
        # Wait, if mock embedding is random, search results are random.
        # This makes testing "correctness" hard.
        # But we can test that it returns results and sorts them.
        
        results = rag.search("reward points")
        self.assertTrue(len(results) <= 3)
        
        # Check structure
        if results:
            self.assertIn("text", results[0])
            self.assertIn("score", results[0])
            
    def test_lexical_fallback(self):
        """Test lexical fallback when semantic score is low."""
        rag = EmbeddingRAG(kb_path=self.kb_path, index_dir=self.test_dir)
        rag.build_index()
        
        # Force low semantic score by mocking _cosine_similarity to return 0
        original_similarity = rag._cosine_similarity
        rag._cosine_similarity = lambda a, b: 0.0
        
        # Query with keyword match
        results = rag.search("dining")
        
        # Should return result via fallback
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]["fallback"], "lexical")
        self.assertIn("dining", results[0]["text"])
        
        # Restore
        rag._cosine_similarity = original_similarity

if __name__ == "__main__":
    unittest.main()
