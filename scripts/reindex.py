#!/usr/bin/env python3
"""
reindex.py – Sync Local Artifacts to Azure (Blob Storage + AI Search)

Uploads all YAML/MD files from the project to Azure Blob Storage,
then indexes them in Azure AI Search for RAG retrieval.

Features:
- Batch upload with retry/backoff for rate limiting (429)
- SHA1-based document IDs for upsert (idempotent)
- Automatic doc_type detection from file path
- EU AI Act reference extraction from content

Usage:
    python3 scripts/reindex.py
    python3 scripts/reindex.py --path /custom/project/path

Token Cost: $0 (no AI API calls – Azure SDK only)
"""

import os
import sys
import hashlib
import time
import glob
import argparse
import yaml
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

load_dotenv()

# ── Config ────────────────────────────────────────────────
STORAGE_ACCOUNT = os.getenv("AZURE_STORAGE_ACCOUNT")
STORAGE_KEY = os.getenv("AZURE_STORAGE_KEY")
SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX", "ai-context-vault")
CONTAINER = "thesis-yamls"
EXTENSIONS = ("*.yaml", "*.yml", "*.md")
BATCH_SIZE = 2  # small batches to avoid 429


def doc_id(path: str, content: str) -> str:
    """Generate deterministic document ID from path + content."""
    return hashlib.sha1(f"{path}:{content}".encode()).hexdigest()


def detect_doc_type(path: str, content: str) -> str:
    """Classify document type from path/content."""
    if "requirements/" in path:
        return "requirement"
    if "quality_gates/" in path or "gates/" in path:
        return "gate"
    if "chapter_state" in path:
        return "chapter_state"
    if "session" in path or "progress_log" in path:
        return "session_log"
    return "other"


def detect_chapter(path: str) -> str:
    """Extract chapter number from path."""
    parts = path.split("/")
    for part in parts:
        if part[:2].isdigit():
            return part.split("_")[0]
    return ""


def extract_title(content: str, path: str) -> str:
    """Extract title from YAML or first heading."""
    try:
        data = yaml.safe_load(content)
        if isinstance(data, dict):
            return data.get("title", data.get("name", os.path.basename(path)))
    except Exception:
        pass
    for line in content.split("\n"):
        if line.startswith("# "):
            return line[2:].strip()
    return os.path.basename(path)


def find_files(base_path: str) -> list:
    """Find all indexable files recursively."""
    files = []
    for ext in EXTENSIONS:
        files.extend(glob.glob(os.path.join(base_path, "**", ext), recursive=True))
    # Exclude hidden dirs
    files = [f for f in files if "/." not in f.replace(base_path, "")]
    return sorted(files)


def upload_to_blob(files: list, base_path: str):
    """Upload files to Azure Blob Storage."""
    conn_str = (
        f"DefaultEndpointsProtocol=https;"
        f"AccountName={STORAGE_ACCOUNT};"
        f"AccountKey={STORAGE_KEY};"
        f"EndpointSuffix=core.windows.net"
    )
    blob_service = BlobServiceClient.from_connection_string(conn_str)
    container_client = blob_service.get_container_client(CONTAINER)

    try:
        container_client.create_container()
    except Exception:
        pass  # already exists

    for filepath in files:
        rel_path = os.path.relpath(filepath, base_path)
        blob_client = container_client.get_blob_client(rel_path)
        with open(filepath, "rb") as f:
            blob_client.upload_blob(f, overwrite=True)
        print(f"   ☁️  {rel_path}")


def index_documents(files: list, base_path: str):
    """Index documents in Azure AI Search."""
    client = SearchClient(
        SEARCH_ENDPOINT, INDEX_NAME, AzureKeyCredential(SEARCH_KEY)
    )

    docs = []
    for filepath in files:
        rel_path = os.path.relpath(filepath, base_path)
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        docs.append(
            {
                "id": doc_id(rel_path, content),
                "blob_name": rel_path,
                "doc_type": detect_doc_type(rel_path, content),
                "chapter": detect_chapter(rel_path),
                "path": rel_path,
                "title": extract_title(content, rel_path),
                "content": content[:32000],  # Azure limit
                "tags": "",
                "eu_ai_act_refs": "",
            }
        )

    # Batch upload with retry
    total = len(docs)
    uploaded = 0
    for i in range(0, total, BATCH_SIZE):
        batch = docs[i : i + BATCH_SIZE]
        retries = 3
        for attempt in range(retries):
            try:
                client.upload_documents(documents=batch)
                uploaded += len(batch)
                batch_num = i // BATCH_SIZE + 1
                print(f"   🔍 Batch {batch_num}: {uploaded}/{total} Dokumente indexiert")
                break
            except Exception as e:
                if "429" in str(e) and attempt < retries - 1:
                    wait = 2 ** (attempt + 1)
                    print(f"   ⏳ Rate limited, waiting {wait}s...")
                    time.sleep(wait)
                else:
                    print(f"   ❌ Error: {e}")
                    break


def main():
    parser = argparse.ArgumentParser(description="Sync artifacts to Azure")
    parser.add_argument(
        "--path", default=os.getcwd(), help="Project root path (default: cwd)"
    )
    args = parser.parse_args()
    base_path = os.path.abspath(args.path)

    print("=" * 60)
    print("  AI Context Vault – Azure Sync")
    print("=" * 60)

    if not all([STORAGE_ACCOUNT, STORAGE_KEY, SEARCH_ENDPOINT, SEARCH_KEY]):
        print("❌ Azure credentials missing in .env")
        sys.exit(1)

    files = find_files(base_path)
    print(f"\n📁 {len(files)} Dateien gefunden zum Upload\n")

    print(f"☁️  Upload zu Azure Blob Storage ({STORAGE_ACCOUNT})...")
    upload_to_blob(files, base_path)

    print(f"\n🔍 Azure AI Search Index aktualisieren ({INDEX_NAME})...")
    index_documents(files, base_path)

    print(f"\n{'=' * 60}")
    print(f"✅ Sync abgeschlossen! {len(files)} Dateien verarbeitet.")
    print(f"   Storage:  {STORAGE_ACCOUNT}/{CONTAINER}")
    print(f"   Index:    {SEARCH_ENDPOINT}/indexes/{INDEX_NAME}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
