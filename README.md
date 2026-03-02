# Azure AI Studio

Enterprise-grade AI services powered by Azure Cognitive Services.

🔗 **Live Demo:** [https://azure-ai.streamlit.app](https://azure-ai.streamlit.app)

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

### 🔊 Speech Services

| Feature | Description |
|---------|-------------|
| **Speech to Text** | Fast transcription from WAV audio files |
| **Text to Speech** | Neural voice synthesis with SSML support |

### 📄 Document Intelligence

| Feature | Description |
|---------|-------------|
| **Prebuilt Read** | Extract text content from PDFs and images |

## Architecture

```
┌──────────────────────────────────────────────────────┐
│                   Streamlit UI                       │
├──────────────────────────────────────────────────────┤
│               Service Abstraction                    │
│  ┌────────────────────────────────────────────────┐  │
│  │              AzureBaseClient                   │  │
│  │  • Retry logic (429, 5xx)                      │  │
│  │  • Timeout handling                            │  │
│  │  • Request tracing (x-client-request-id)       │  │
│  └──────────┬──────────────────┬──────────────────┘  │
│             │                  │                     │
│    ┌────────┴──────┐  ┌────────┴──────┐              │
│    │LanguageClient │  │ VisionClient  │              │
│    └───────────────┘  └───────────────┘              │
│    ┌───────────────┐  ┌───────────────┐              │
│    │ SpeechClient  │  │DocIntelClient │              │
│    └───────────────┘  └───────────────┘              │
├──────────────────────────────────────────────────────┤
│  Telemetry (AzureCallMeta)                           │
│  • Service, operation, latency, status, request ID   │
└──────────────────────────────────────────────────────┘
```

### Design Principles

- **Service Abstraction:** Shared base client with retry/timeout logic; per-service subclasses
- **Structured Telemetry:** Every API call returns `AzureCallMeta` (request ID, latency, status)
- **Resilience:** Automatic retry on transient failures (429, 500–504)
- **Observability:** Sidebar diagnostics panel with call history

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Streamlit |
| Language AI | Azure AI Language (2023-04-01) |
| Vision AI | Azure AI Vision (2024-02-01) |
| Speech AI | Azure AI Speech REST (2025-10-15) |
| Document AI | Azure Document Intelligence (2024-11-30) |
| Deployment | Streamlit Cloud |

## Configuration

Copy the example secrets file and fill in your Azure credentials:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

| Secret | Required | Description |
|--------|----------|-------------|
| `AZURE_LANGUAGE_ENDPOINT` | ✅ | Azure AI Language endpoint |
| `AZURE_LANGUAGE_KEY` | ✅ | Azure AI Language API key |
| `AZURE_VISION_ENDPOINT` | Optional | Azure AI Vision endpoint |
| `AZURE_VISION_KEY` | Optional | Azure AI Vision API key |
| `AZURE_SPEECH_REGION` | Optional | Azure Speech region (e.g. `eastus`) |
| `AZURE_SPEECH_KEY` | Optional | Azure Speech API key |
| `AZURE_DOCINTEL_ENDPOINT` | Optional | Azure Document Intelligence endpoint |
| `AZURE_DOCINTEL_KEY` | Optional | Azure Document Intelligence API key |

## Local Development

```bash
git clone https://github.com/tvprasad/azure-ai-studio.git
cd azure-ai-studio
pip install -r requirements.txt

cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit with your Azure credentials

streamlit run app.py
```

## Changelog
### v0.5.0
- Added **Speech Services**: fast Speech-to-Text transcription and neural Text-to-Speech synthesis
- Added **Document Intelligence**: prebuilt-read model for PDF and image extraction
- Promoted `AzureBaseClient` shared retry/timeout/telemetry base class
- Updated sidebar diagnostics with total call counter
- Updated architecture and configuration documentation

### v0.4.0
- Added **AI Governance layer**: `GovernanceLayer` class with per-request cost estimation and session-level usage aggregation
- Added **Governance sidebar panel**: real-time usage metrics showing total calls, session cost, and per-service breakdown
- Expanded `AzureCallMeta` with `estimated_cost_usd` field populated on every API call
- Added `_GOVERNANCE_PRICING` table (Azure retail pricing, 2026-Q1) covering all four services
- Updated `AzureSpeechClient.fast_transcribe` and `synthesize` to return `(result, AzureCallMeta)` tuples
- Enhanced diagnostics panel to include estimated cost per call
- Cost captions added to all service result views
- Billing unit semantics: Language=text record, Vision=transaction, Speech STT=minute, Speech TTS=character, Document Intelligence=page

### v0.3.0
- Added **Vision Intelligence**: image analysis, tagging, OCR via Azure AI Vision
- Added `AzureBaseClient` with shared retry and telemetry logic
- Introduced `AzureVisionClient`

### v0.2.0
- Enterprise service layer: `AzureLanguageClient` with retry, timeout, and request tracing
- Structured telemetry: `AzureCallMeta` dataclass
- Sidebar diagnostics panel
- Caching via `st.cache_data`

### v0.1.0
- Initial release: Language Intelligence (Sentiment, Entities, Key Phrases, Language Detection)

## Author

**Prasad Thiriveedi**

20+ years in distributed event-driven systems. Now leading teams and architecting enterprise AI infrastructure.

[GitHub](https://github.com/tvprasad) | [LinkedIn](https://linkedin.com/in/-Prasad)

## License

MIT
