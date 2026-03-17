# Technical Overview Diagram

```mermaid
flowchart LR
    A["AI Session<br/>Claude / ChatGPT / Other"] --> B["save.py<br/>Detect topic + summarize"]
    B --> C["Structured YAML Artifacts<br/>decisions, next steps, metadata"]
    C --> D["Git Versioning<br/>traceable history"]
    C --> E["resume.py<br/>compact restart context"]
    C --> F["Optional Cloud Layer<br/>Azure Blob + AI Search"]
    E --> G["Next Session<br/>focused working context"]
    F --> H["search.py<br/>selective retrieval"]
    H --> G

    classDef core fill:#eef6ff,stroke:#1d4ed8,stroke-width:1.5px,color:#0f172a;
    classDef local fill:#f0fdf4,stroke:#16a34a,stroke-width:1.5px,color:#0f172a;
    classDef cloud fill:#fff7ed,stroke:#ea580c,stroke-width:1.5px,color:#0f172a;

    class A,B,C,D core;
    class E,G,H local;
    class F cloud;
```

## Message

- raw chat becomes structured artifacts with metadata
- `save.py` and `resume.py` separate persistence from restart context
- Git preserves auditability and change history
- Azure Blob Storage and Azure AI Search are optional for backup, sync, and retrieval
- `search.py` returns only relevant context to the next session
