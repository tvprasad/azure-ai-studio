# Azure AI Studio

Enterprise-grade AI services powered by Azure Cognitive Services.

🔗 **Live Demo:** [https://azure-ai.streamlit.app.streamlit.app](https://azure-ai.streamlit.app.streamlit.app)

## Services

### 🗣️ Language Intelligence

| Feature | Description |
|---------|-------------|
| **Sentiment Analysis** | Detect positive, negative, neutral, or mixed sentiment |
| **Entity Recognition** | Extract people, places, organizations, dates |
| **Key Phrase Extraction** | Identify main topics and themes |
| **Language Detection** | Identify the language of input text |

### 👁️ Vision Intelligence

| Feature | Description |
|---------|-------------|
| **Image Analysis** | Auto-generate captions, detect objects, identify people |
| **Tagging** | Extract visual tags with confidence scores |
| **OCR** | Extract text from images |

### 🔮 Coming Soon

- **Speech:** Speech-to-text, text-to-speech
- **Document Intelligence:** Form extraction, document parsing

## Architecture
```
┌─────────────────────────────────────────────┐
│              Streamlit UI                   │
├─────────────────────────────────────────────┤
│           Service Abstraction               │
│  ┌───────────────────────────────────────┐  │
│  │         AzureBaseClient               │  │
│  │  • Retry logic (429, 5xx)             │  │
│  │  • Timeout handling                   │  │
│  │  • Request tracing                    │  │
│  └───────────────┬───────────────────────┘  │
│          ┌───────┴───────┐                  │
│          ▼               ▼                  │
│  ┌──────────────┐ ┌──────────────┐          │
│  │LanguageClient│ │ VisionClient │          │
│  └──────────────┘ └──────────────┘          │
├─────────────────────────────────────────────┤
│  Telemetry (AzureCallMeta)                  │
│  • Service, operation, latency, status      │
└─────────────────────────────────────────────┘
```

### Design Principles

- **Service Abstraction:** Base client with shared retry/timeout logic
- **Structured Telemetry:** Every API call returns `AzureCallMeta`
- **Resilience:** Automatic retry on transient failures (429, 500-504)
- **Observability:** Sidebar diagnostics panel

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Streamlit |
| AI Services | Azure Cognitive Services (Language, Vision) |
| Deployment | Streamlit Cloud |

## Local Development
```bash
git clone https://github.com/tvprasad/azure-ai-studio.git
cd azure-ai-studio
pip install -r requirements.txt

mkdir -p .streamlit
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit with your Azure credentials

streamlit run app.py
```

## Author

**Prasad Thiriveedi**

20+ years in distributed event-driven systems. Now leading teams and architecting enterprise AI infrastructure.

[GitHub](https://github.com/tvprasad) | [LinkedIn](https://linkedin.com/in/-Prasad)

## License

MIT