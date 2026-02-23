#!/usr/bin/env python3
"""
search.py – Query Azure AI Search + Claude API for Intelligent Answers

Combines Azure AI Search (retrieval) with Claude API (generation) in a
classic RAG pattern:

1. User asks a question
2. Azure AI Search finds Top-8 relevant documents
3. Claude analyzes the retrieved context and generates an answer
4. Sources and relevance scores are displayed

Usage:
    python3 scripts/search.py "your question here"
    python3 scripts/search.py "welche EU AI Act Artikel muss ich abdecken?"
    python3 scripts/search.py "what components does the architecture have?"

Token Cost: ~0.01-0.05$ per query (Claude API only, Azure Search is free tier)
"""

import os
import sys
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
import anthropic

load_dotenv()

# ── Config ────────────────────────────────────────────────
SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX", "ai-context-vault")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")
TOP_K = 8
MAX_TOKENS = 2000
MODEL = "claude-sonnet-4-20250514"


def search_azure(query: str) -> list:
    """Search Azure AI Search for relevant documents."""
    client = SearchClient(
        SEARCH_ENDPOINT, INDEX_NAME, AzureKeyCredential(SEARCH_KEY)
    )
    results = client.search(
        search_text=query,
        top=TOP_K,
        include_total_count=True,
    )

    docs = []
    for r in results:
        docs.append(
            {
                "path": r.get("path", "unknown"),
                "title": r.get("title", ""),
                "doc_type": r.get("doc_type", ""),
                "content": r.get("content", "")[:3000],
                "score": r.get("@search.score", 0),
            }
        )
    return docs


def ask_claude(query: str, docs: list) -> str:
    """Send query + retrieved context to Claude for analysis."""
    if not ANTHROPIC_KEY:
        return "❌ ANTHROPIC_API_KEY not set in .env"

    context_parts = []
    for i, doc in enumerate(docs):
        context_parts.append(
            f"[{i+1}] {doc['path']} (type: {doc['doc_type']}, score: {doc['score']:.2f})\n"
            f"{doc['content'][:2000]}"
        )
    context = "\n\n---\n\n".join(context_parts)

    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    message = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Du bist ein Research-Assistent. Beantworte die folgende Frage "
                    f"NUR basierend auf dem bereitgestellten Kontext. "
                    f"Nutze Quellenverweise wie [1], [2] etc.\n\n"
                    f"Frage: {query}\n\n"
                    f"Kontext:\n{context}"
                ),
            }
        ],
    )
    return message.content[0].text


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/search.py \"your question\"")
        sys.exit(1)

    query = " ".join(sys.argv[1:])

    if not SEARCH_ENDPOINT or not SEARCH_KEY:
        print("❌ Azure Search credentials missing in .env")
        sys.exit(1)

    print(f"\n🔍 Suche: '{query}'")
    print("=" * 60)

    # Step 1: Retrieve from Azure
    docs = search_azure(query)
    print(f"📄 {len(docs)} relevante Dokumente gefunden:")
    for doc in docs:
        print(f"   • [{doc['doc_type']}] {doc['title']} (Score: {doc['score']:.2f})")

    # Step 2: Generate answer with Claude
    print("\n🤖 Claude analysiert...\n")
    answer = ask_claude(query, docs)
    print("=" * 60)
    print(answer)
    print("=" * 60)


if __name__ == "__main__":
    main()
