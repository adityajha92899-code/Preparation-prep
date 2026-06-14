"""Seed the placeholder knowledge base with sample documents."""
from training.rag_pipeline import PlacementKnowledgeBase, KBDocument
import uuid


def seed():
    kb = PlacementKnowledgeBase()
    kb.build_complete_knowledge_base()

    docs = [
        KBDocument(content="Binary search is a divide and conquer algorithm...", metadata={"topic": "binary_search"}, doc_id=str(uuid.uuid4())),
        KBDocument(content="Design a URL shortener: use hash, DB, redirect service...", metadata={"topic": "url_shortener"}, doc_id=str(uuid.uuid4())),
    ]

    kb._batch_add("dsa_solutions", docs)
    kb._batch_add("system_designs", docs)
    print("Seeded KB with sample documents")


if __name__ == '__main__':
    seed()
