"""
Azure AI Studio
Enterprise-ready Streamlit integration for Azure Cognitive Services.

Architectural Improvements:
- Service abstraction layer
- Retry & timeout handling
- Structured telemetry
- Caching
- Diagnostics panel
"""

import streamlit as st
import requests
import time
import uuid
from dataclasses import dataclass
from typing import Any, Dict, Optional


# -----------------------------
# Page Configuration
# -----------------------------

st.set_page_config(
    page_title="Azure AI Studio",
    page_icon="🧠",
    layout="wide"
)

# -----------------------------
# Secrets
# -----------------------------

ENDPOINT = st.secrets["AZURE_LANGUAGE_ENDPOINT"]
API_KEY = st.secrets["AZURE_LANGUAGE_KEY"]


# -----------------------------
# Telemetry Model
# -----------------------------

@dataclass
class AzureCallMeta:
    request_id: str
    kind: str
    status_code: int
    elapsed_ms: int
    endpoint: str


class AzureLanguageError(RuntimeError):
    pass


# -----------------------------
# Service Layer (Architect-Level)
# -----------------------------

class AzureLanguageClient:
    """
    Enterprise-grade Azure Language wrapper.
    Encapsulates retries, timeouts, and structured telemetry.
    """

    def __init__(
        self,
        endpoint: str,
        api_key: str,
        api_version: str = "2023-04-01",
        timeout_s: float = 10.0,
        max_retries: int = 2,
        session: Optional[requests.Session] = None,
    ):
        self.endpoint = endpoint.rstrip("/")
        self.api_key = api_key
        self.api_version = api_version
        self.timeout_s = timeout_s
        self.max_retries = max_retries
        self.session = session or requests.Session()

    def analyze(self, text: str, kind: str, language: str = "en") -> tuple[Dict[str, Any], AzureCallMeta]:

        url = f"{self.endpoint}/language/:analyze-text?api-version={self.api_version}"

        request_id = str(uuid.uuid4())

        headers = {
            "Ocp-Apim-Subscription-Key": self.api_key,
            "Content-Type": "application/json",
            "x-client-request-id": request_id
        }

        payload = {
            "kind": kind,
            "parameters": {"modelVersion": "latest"},
            "analysisInput": {
                "documents": [{"id": "1", "language": language, "text": text}]
            }
        }

        for attempt in range(self.max_retries + 1):
            start = time.perf_counter()

            try:
                response = self.session.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout_s
                )

                elapsed_ms = int((time.perf_counter() - start) * 1000)

                meta = AzureCallMeta(
                    request_id=request_id,
                    kind=kind,
                    status_code=response.status_code,
                    elapsed_ms=elapsed_ms,
                    endpoint=self.endpoint
                )

                if 200 <= response.status_code < 300:
                    return response.json(), meta

                retryable = response.status_code in (429, 500, 502, 503, 504)

                if retryable and attempt < self.max_retries:
                    time.sleep(0.4 * (attempt + 1))
                    continue

                raise AzureLanguageError(
                    f"Azure API error {response.status_code}: {response.text[:500]}"
                )

            except (requests.Timeout, requests.ConnectionError) as e:
                if attempt < self.max_retries:
                    time.sleep(0.3 * (attempt + 1))
                    continue
                raise AzureLanguageError(f"Network error: {e}") from e

        raise AzureLanguageError("Azure API failed after retries.")


# -----------------------------
# Caching Layer
# -----------------------------

@st.cache_data(show_spinner=False, ttl=300)
def cached_analysis(endpoint, api_key, text, kind):
    client = AzureLanguageClient(endpoint, api_key)
    result, _ = client.analyze(text, kind)
    return result


# -----------------------------
# UI Rendering Functions
# -----------------------------

def render_sentiment(result: dict):
    doc = result["results"]["documents"][0]
    sentiment = doc["sentiment"]
    confidence = doc["confidenceScores"]

    emoji = {"positive": "😊", "negative": "😞", "neutral": "😐", "mixed": "🤔"}

    st.subheader(f"Overall: {sentiment.upper()} {emoji.get(sentiment, '')}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Positive", f"{confidence['positive']:.1%}")
    col2.metric("Neutral", f"{confidence['neutral']:.1%}")
    col3.metric("Negative", f"{confidence['negative']:.1%}")


def render_entities(result: dict):
    entities = result["results"]["documents"][0]["entities"]

    if not entities:
        st.info("No entities detected.")
        return

    grouped = {}
    for e in entities:
        grouped.setdefault(e["category"], []).append(e)

    for category, ents in grouped.items():
        st.markdown(f"**{category}**")
        for ent in ents:
            st.write(f"• {ent['text']} ({ent.get('confidenceScore', 0):.0%})")


def render_key_phrases(result: dict):
    phrases = result["results"]["documents"][0]["keyPhrases"]

    if not phrases:
        st.info("No key phrases detected.")
        return

    st.markdown(" ".join([f"`{p}`" for p in phrases]))


def render_language_detection(result: dict):
    lang = result["results"]["documents"][0]["detectedLanguage"]

    st.metric(
        "Detected Language",
        lang["name"],
        delta=f"ISO: {lang['iso6391Name']} | {lang['confidenceScore']:.0%}"
    )


# -----------------------------
# App UI
# -----------------------------

st.title("🧠 Azure AI Studio")
st.markdown("Enterprise-grade AI services powered by Azure Cognitive Services.")

if "telemetry" not in st.session_state:
    st.session_state.telemetry = []

# Sidebar
st.sidebar.header("Services")
service = st.sidebar.radio(
    "Select a service:",
    ["Language Intelligence", "Vision (Coming Soon)", "Speech (Coming Soon)"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Built by**")
st.sidebar.markdown("[Prasad T](https://github.com/tvprasad)")
st.sidebar.markdown("Principal Software Engineer | AI Engineer")

with st.sidebar.expander("Diagnostics"):
    if st.session_state.telemetry:
        last = st.session_state.telemetry[-1]
        st.write(f"Last Call: {last.kind}")
        st.write(f"Status: {last.status_code}")
        st.write(f"Latency: {last.elapsed_ms} ms")
        st.caption(f"Request ID: {last.request_id}")
    else:
        st.caption("No API calls yet.")


# -----------------------------
# Language Intelligence
# -----------------------------

if service == "Language Intelligence":

    st.header("🗣️ Language Intelligence")

    sample_texts = {
        "Product Review": "I absolutely love this product! The quality is amazing and shipping was super fast.",
        "News Article": "Microsoft announced today it will acquire a leading AI startup for $2 billion.",
        "Technical Log": "The Kubernetes cluster experienced memory pressure on node worker-3.",
        "Custom": ""
    }

    selected = st.selectbox("Choose sample or custom:", list(sample_texts.keys()))

    if selected == "Custom":
        text_input = st.text_area("Enter your text:", height=150)
    else:
        text_input = st.text_area("Enter your text:", value=sample_texts[selected], height=150)

    if text_input:

        client = AzureLanguageClient(ENDPOINT, API_KEY)

        tab1, tab2, tab3, tab4 = st.tabs(["😊 Sentiment", "🏷️ Entities", "🔑 Key Phrases", "🌍 Language"])

        def execute(kind, renderer):
            try:
                with st.spinner("Analyzing..."):
                    result, meta = client.analyze(text_input, kind)
                    st.session_state.telemetry.append(meta)
                    renderer(result)
                    st.caption(f"{meta.status_code} • {meta.elapsed_ms} ms • {meta.request_id}")
            except AzureLanguageError as e:
                st.error(str(e))

        with tab1:
            if st.button("Analyze Sentiment"):
                execute("SentimentAnalysis", render_sentiment)

        with tab2:
            if st.button("Extract Entities"):
                execute("EntityRecognition", render_entities)

        with tab3:
            if st.button("Extract Key Phrases"):
                execute("KeyPhraseExtraction", render_key_phrases)

        with tab4:
            if st.button("Detect Language"):
                execute("LanguageDetection", render_language_detection)

    else:
        st.info("Enter text to begin.")

else:
    st.header("🚧 Coming Soon")
    st.markdown("""
    - Vision Intelligence  
    - Speech Services  
    - Document Intelligence  
    """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:gray;'>Azure AI Studio — Built with Streamlit & Azure Cognitive Services</div>",
    unsafe_allow_html=True
)