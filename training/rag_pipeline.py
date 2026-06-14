import logging
from dataclasses import dataclass
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class KBDocument:
    content: str
    metadata: Dict[str, Any]
    doc_id: str


class PlacementKnowledgeBase:
    def __init__(self, persist_dir: str = "./chroma_db"):
        self.persist_dir = persist_dir
        self.collections = {}
        self._use_chroma = False
        try:
            import chromadb
            from chromadb.config import Settings as ChromaSettings

            self._chroma = chromadb.Client(chromadb.config.Settings(chroma_db_impl="duckdb+parquet", persist_directory=self.persist_dir))
            self._use_chroma = True
        except Exception:
            logger.info("Chroma not available or failed to init; using in-memory KB")
            self._chroma = None

    def _init_collections(self):
        # placeholder for chroma collections or in-memory ones
        names = [
            "interview_experiences",
            "dsa_solutions",
            "system_designs",
            "company_insights",
            "salary_data",
            "projects",
        ]
        if self._use_chroma and self._chroma:
            for n in names:
                try:
                    self._chroma.get_collection(n)
                except Exception:
                    self._chroma.create_collection(n)
        else:
            self.collections = {n: [] for n in names}

    def build_complete_knowledge_base(self):
        logger.info("Building KB (chroma-ready)")
        self._init_collections()

    def _batch_add(self, collection, documents: List[KBDocument]):
        if self._use_chroma and self._chroma:
            coll = self._chroma.get_collection(collection)
            texts = [d.content for d in documents]
            metadatas = [d.metadata for d in documents]
            ids = [d.doc_id for d in documents]
            coll.add(documents=texts, metadatas=metadatas, ids=ids)
            return

        if collection not in self.collections:
            return
        for d in documents:
            self.collections[collection].append(d)

    def search(self, query: str, collection_name: str = "all", n_results: int = 3, where_filter: Optional[Dict] = None):
        results = []
        # If chroma is available, use semantic search
        if self._use_chroma and self._chroma:
            if collection_name == "all":
                # aggregate from all collections
                for name in self._chroma.list_collections():
                    coll = self._chroma.get_collection(name.name)
                    res = coll.query(query_texts=[query], n_results=n_results)
                    for r in res['documents'][0][:n_results]:
                        results.append({"content": r, "metadata": {}, "distance": 0.0, "id": ""})
            else:
                coll = self._chroma.get_collection(collection_name)
                res = coll.query(query_texts=[query], n_results=n_results)
                for r in res['documents'][0][:n_results]:
                    results.append({"content": r, "metadata": {}, "distance": 0.0, "id": ""})
            return results

        # Fallback naive search: return first n documents from collection
        if collection_name == "all":
            for k, v in self.collections.items():
                for doc in v[:n_results]:
                    results.append({"content": doc.content, "metadata": doc.metadata, "distance": 0.0, "id": doc.doc_id})
        else:
            coll = self.collections.get(collection_name, [])
            for doc in coll[:n_results]:
                results.append({"content": doc.content, "metadata": doc.metadata, "distance": 0.0, "id": doc.doc_id})
        return results

    def augment_with_context(self, query: str, agent_type: str) -> str:
        res = self.search(query, collection_name="all", n_results=2)
        if not res:
            return query
        ctx = "\n".join([r["content"][:500] for r in res])
        return f"## Relevant KB:\n{ctx}\n\n## User Query\n{query}"
