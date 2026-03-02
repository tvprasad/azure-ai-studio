# Azure AI Studio

Enterprise-grade AI services powered by Azure Cognitive Services.

🔗 **Live Demo:** [https://tvprasad-azure-ai-studio.streamlit.app](https://tvprasad-azure-ai-studio.streamlit.app)

## Features

### 🧠 Language Intelligence

| Feature | Description |
|---------|-------------|
| **Sentiment Analysis** | Detect positive, negative, neutral, or mixed sentiment |
| **Entity Recognition** | Extract people, places, organizations, dates |
| **Key Phrase Extraction** | Identify main topics and themes |
| **Language Detection** | Identify the language of input text |

### 🔮 Coming Soon

- **Vision:** Image analysis, OCR, object detection
- **Speech:** Speech-to-text, text-to-speech
- **Document Intelligence:** Form extraction, document parsing

## Architecture

Built with production patterns, not demo code:

```
┌─────────────────────────────────────────┐
│            Streamlit UI                 │
├─────────────────────────────────────────┤
│         Service Abstraction             │
│  ┌─────────────────────────────────┐    │
│  │     AzureLanguageClient         │    │
│  │  • Retry logic (429, 5xx)       │    │
│  │  • Timeout handling             │    │
│  │  • Request tracing              │    │
│  └─────────────────────────────────┘    │
├─────────────────────────────────────────┤
│  Telemetry (AzureCallMeta)              │
│  • Request ID, latency, status          │
├─────────────────────────────────────────┤
│  Caching (@st.cache_data)               │
│  • TTL-based response caching           │
└─────────────────────────────────────────┘
```

### Key Design Decisions

- **Service Layer:** `AzureLanguageClient` encapsulates all API logic with retries, timeouts, and structured responses
- **Telemetry:** Every API call returns `AzureCallMeta` for observability
- **Resilience:** Automatic retry on transient failures (429, 500-504)
- **Diagnostics:** Sidebar panel shows last API call metrics

## Tech Stack

- **Frontend:** Streamlit
- **AI/ML:** Azure Cognitive Services (Language)
- **Deployment:** Streamlit Cloud

## Local Development

### Prerequisites

- Python 3.10+
- Azure subscription with Language resource

### Setup

```bash
git clone https://github.com/tvprasad/azure-ai-studio.git
cd azure-ai-studio

pip install -r requirements.txt

mkdir -p .streamlit
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit .streamlit/secrets.toml with your Azure credentials

streamlit run app.py
```

## Deployment

### Streamlit Cloud

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo
4. Add secrets in dashboard:
   - `AZURE_LANGUAGE_ENDPOINT`
   - `AZURE_LANGUAGE_KEY`

## Azure Setup

```bash
# Language resource (Free tier)
az cognitiveservices account create \
  --name your-language-resource \
  --resource-group your-rg \
  --kind TextAnalytics \
  --sku F0 \
  --location eastus

# Get endpoint
az cognitiveservices account show \
  --name your-language-resource \
  --resource-group your-rg \
  --query "properties.endpoint" -o tsv

# Get key
az cognitiveservices account keys list \
  --name your-language-resource \
  --resource-group your-rg \
  --query "key1" -o tsv
```

## Author

**Prasad T** — Principal Software Engineer | AI Engineer

Building production-grade AI infrastructure.

[GitHub](https://github.com/tvprasad) | [LinkedIn](https://linkedin.com/in/-Prasad)

## License

MIT
