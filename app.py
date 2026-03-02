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
VISION_ENDPOINT = st.secrets.get("AZURE_VISION_ENDPOINT", "")
VISION_KEY = st.secrets.get("AZURE_VISION_KEY", "")

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


class AzureServiceError(RuntimeError):
    pass

class AzureBaseClient:
    """
    Shared Azure base client with retry, timeout, and telemetry support.
    """

    def __init__(
        self,
        endpoint: str,
        api_key: str,
        timeout_s: float = 10.0,
        max_retries: int = 2,
        session: Optional[requests.Session] = None,
    ):
        self.endpoint = endpoint.rstrip("/")
        self.api_key = api_key
        self.timeout_s = timeout_s
        self.max_retries = max_retries
        self.session = session or requests.Session()


    def _request(self, method: str, url: str, service: str, operation: str, **kwargs):

        request_id = str(uuid.uuid4())

        headers = kwargs.pop("headers", {})
        headers.update({
            "Ocp-Apim-Subscription-Key": self.api_key,
            "x-client-request-id": request_id
        })

        for attempt in range(self.max_retries + 1):
            start = time.perf_counter()

            try:
                response = self.session.request(
                    method,
                    url,
                    headers=headers,
                    timeout=self.timeout_s,
                    **kwargs
                )

                elapsed_ms = int((time.perf_counter() - start) * 1000)

                meta = AzureCallMeta(
                    request_id=request_id,
                    kind=f"{service}:{operation}",
                    status_code=response.status_code,
                    elapsed_ms=elapsed_ms,
                    endpoint=self.endpoint
                )

                if 200 <= response.status_code < 300:
                    return response, meta

                retryable = response.status_code in (429, 500, 502, 503, 504)

                if retryable and attempt < self.max_retries:
                    time.sleep(0.4 * (attempt + 1))
                    continue

                raise AzureServiceError(
                    f"{service} API error {response.status_code}: {response.text[:500]}"
                )

            except (requests.Timeout, requests.ConnectionError) as e:
                if attempt < self.max_retries:
                    time.sleep(0.3 * (attempt + 1))
                    continue
                raise AzureServiceError(f"Network error: {e}") from e

        raise AzureServiceError("Azure API failed after retries.")


class AzureVisionClient(AzureBaseClient):

    def analyze_image(self, image_data: bytes, features: list[str]):

        url = f"{self.endpoint}/computervision/imageanalysis:analyze?api-version=2024-02-01"
        url += f"&features={','.join(features)}"

        response, meta = self._request(
            "POST",
            url,
            service="Vision",
            operation="ImageAnalysis",
            data=image_data,
            headers={"Content-Type": "application/octet-stream"}
        )

        return response.json(), meta

# -----------------------------
# Service Layer (Architect-Level)
# -----------------------------
class AzureLanguageClient(AzureBaseClient):

    def analyze(self, text: str, kind: str, language: str = "en"):

        url = f"{self.endpoint}/language/:analyze-text?api-version=2023-04-01"

        payload = {
            "kind": kind,
            "parameters": {"modelVersion": "latest"},
            "analysisInput": {
                "documents": [{"id": "1", "language": language, "text": text}]
            }
        }

        response, meta = self._request(
            "POST",
            url,
            service="Language",
            operation=kind,
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        return response.json(), meta

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
    ["Language Intelligence", "Vision Intelligence", "Speech (Coming Soon)"]
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
        st.write(f"Total Calls: {len(st.session_state.telemetry)}")
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
            except AzureServiceError as e:
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
elif service == "Vision Intelligence":
    st.header("👁️ Vision Intelligence")
    
    if not VISION_ENDPOINT or not VISION_KEY:        
        st.warning("Vision not configured. Add AZURE_VISION_ENDPOINT and AZURE_VISION_KEY to secrets.")
    else:
        uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])
        
        if uploaded_file:
            col1, col2 = st.columns(2)
            with col1:
                st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
            with col2:
                if st.button("Analyze Image"):
                    client = AzureVisionClient(VISION_ENDPOINT, VISION_KEY)
                    result, meta = client.analyze_image(
                        uploaded_file.getvalue(),
                        features=["Caption", "Tags", "Objects", "Read"]
                    )
                    
                    st.session_state.telemetry.append(meta)
                    st.caption(f"{meta.status_code} • {meta.elapsed_ms} ms • {meta.request_id}")


                    # Display OCR text
                    if "readResult" in result and result["readResult"]:
                        st.markdown("### 📝 OCR Extracted Text")

                        read_blocks = result["readResult"].get("blocks", [])

                        if not read_blocks:
                            st.info("No readable text detected.")
                        else:
                            full_text = []

                            for block in read_blocks:
                                for line in block.get("lines", []):
                                    text = line.get("text", "")
                                    confidence = line.get("confidence", None)

                                    if confidence:
                                        st.write(f"{text}  _(conf: {confidence:.2f})_")
                                    else:
                                        st.write(text)

                                    full_text.append(text)

                            # Optional: Collapsible full text view
                            with st.expander("View Full Extracted Text"):
                                st.text("\n".join(full_text))
                               
                    
                    # Display caption
                    if "captionResult" in result:
                        st.write(f"**Caption:** {result['captionResult']['text']}")
                    # Display tags
                    if "tagsResult" in result:
                        tags = [t["name"] for t in result["tagsResult"]["values"][:8]]
                        st.write(f"**Tags:** {', '.join(tags)}")
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