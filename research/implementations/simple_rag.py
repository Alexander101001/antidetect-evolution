"""🔍 SIMPLE RAG - from RAGFlow (87k stars)"""
import json
import re
from pathlib import Path
from datetime import datetime

class SimpleRAG:
    def __init__(self, memory_dir="memory"):
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(exist_ok=True)
        self.documents = []
        self._load_documents()
    
    def _load_documents(self):
        for mem_file in self.memory_dir.glob("*.json"):
            try:
                data = json.loads(mem_file.read_text())
                text = json.dumps(data) if isinstance(data, dict) else str(data)
                self.documents.append({"text": text, "source": mem_file.name, "data": data})
            except:
                pass
    
    def add_document(self, doc, source="manual"):
        entry = {"text": json.dumps(doc), "source": source, "data": doc}
        self.documents.append(entry)
        timestamp = int(datetime.now().timestamp() * 1000)
        (self.memory_dir / f"{timestamp}_{source}.json").write_text(json.dumps(doc, indent=2))
    
    def retrieve(self, query, top_k=3):
        query_words = set(re.findall(r"\w+", query.lower()))
        scores = []
        for doc in self.documents:
            doc_words = set(re.findall(r"\w+", doc["text"].lower()))
            overlap = len(query_words & doc_words)
            scores.append((overlap, doc))
        scores.sort(reverse=True, key=lambda x: x[0])
        return [doc for _, doc in scores[:top_k] if _ > 0]


if __name__ == "__main__":
    rag = SimpleRAG()
    rag.add_document({"action": "registered on Vercel", "result": "success"})
    rag.add_document({"action": "posted to Reddit", "result": "success"})
    results = rag.retrieve("successful registrations")
    print(f"🔍 RAG found {len(results)} relevant docs")
    for r in results:
        print(f"   - {r['source']}: {r['text'][:80]}")
