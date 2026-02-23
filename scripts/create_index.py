#!/usr/bin/env python3
"""
create_index.py – Create Azure AI Search Index Schema

Creates a search index with fields optimized for AI context retrieval:
- Full-text search on content, title, tags
- Filterable metadata (doc_type, chapter)
- EU AI Act reference tracking

Usage:
    python3 scripts/create_index.py

Run once to initialize the index. Safe to re-run (updates existing).
"""

import os
import sys
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    SearchFieldDataType,
)

load_dotenv()

ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
KEY = os.getenv("AZURE_SEARCH_KEY")
INDEX = os.getenv("AZURE_SEARCH_INDEX", "ai-context-vault")


def create_index():
    """Create or update the Azure AI Search index."""
    if not ENDPOINT or not KEY:
        print("❌ AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_KEY required in .env")
        sys.exit(1)

    client = SearchIndexClient(ENDPOINT, AzureKeyCredential(KEY))

    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SimpleField(
            name="blob_name",
            type=SearchFieldDataType.String,
            filterable=True,
        ),
        SimpleField(
            name="doc_type",
            type=SearchFieldDataType.String,
            filterable=True,
            facetable=True,
        ),
        SimpleField(
            name="chapter",
            type=SearchFieldDataType.String,
            filterable=True,
            facetable=True,
        ),
        SearchableField(name="path", type=SearchFieldDataType.String),
        SearchableField(name="title", type=SearchFieldDataType.String),
        SearchableField(name="content", type=SearchFieldDataType.String),
        SearchableField(name="tags", type=SearchFieldDataType.String),
        SearchableField(name="eu_ai_act_refs", type=SearchFieldDataType.String),
    ]

    index = SearchIndex(name=INDEX, fields=fields)
    result = client.create_or_update_index(index)
    print(f"✅ Index '{result.name}' erstellt/aktualisiert!")
    print(f"   Felder: {len(result.fields)}")
    print(f"   URL: {ENDPOINT}/indexes/{INDEX}")


if __name__ == "__main__":
    create_index()
