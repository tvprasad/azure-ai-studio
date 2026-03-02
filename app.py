"""
Azure AI Studio
A Streamlit app showcasing Azure Cognitive Services.

Features:
- Sentiment Analysis
- Entity Recognition  
- Key Phrase Extraction
- Language Detection
"""

import streamlit as st
import requests

# Page config
st.set_page_config(
    page_title="Azure AI Studio",
    page_icon="🧠",
    layout="wide"
)

# Load secrets
ENDPOINT = st.secrets["AZURE_LANGUAGE_ENDPOINT"]
API_KEY = st.secrets["AZURE_LANGUAGE_KEY"]


def call_language_api(text: str, kind: str) -> dict:
    """Call Azure AI Language API."""
    url = f"{ENDPOINT}/language/:analyze-text?api-version=2023-04-01"
    
    headers = {
        "Ocp-Apim-Subscription-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "kind": kind,
        "parameters": {"modelVersion": "latest"},
        "analysisInput": {
            "documents": [{"id": "1", "language": "en", "text": text}]
        }
    }
    
    response = requests.post(url, headers=headers, json=payload)
    return response.json()


def render_sentiment(result: dict):
    """Render sentiment analysis results."""
    try:
        doc = result["results"]["documents"][0]
        sentiment = doc["sentiment"]
        confidence = doc["confidenceScores"]
        
        emoji = {"positive": "😊", "negative": "😞", "neutral": "😐", "mixed": "🤔"}
        
        st.subheader(f"Overall: {sentiment.upper()} {emoji.get(sentiment, '')}")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Positive", f"{confidence['positive']:.1%}")
        col2.metric("Neutral", f"{confidence['neutral']:.1%}")
        col3.metric("Negative", f"{confidence['negative']:.1%}")
        
        if doc.get("sentences"):
            st.markdown("---")
            st.markdown("**Sentence-level breakdown:**")
            for sent in doc["sentences"]:
                st.write(f"{emoji.get(sent['sentiment'], '')} _{sent['text']}_")
                
    except KeyError as e:
        st.error(f"Error parsing response: {e}")
        st.json(result)


def render_entities(result: dict):
    """Render entity recognition results."""
    try:
        entities = result["results"]["documents"][0]["entities"]
        
        if not entities:
            st.info("No entities detected.")
            return
        
        by_category = {}
        for ent in entities:
            cat = ent["category"]
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(ent)
        
        for category, ents in by_category.items():
            st.markdown(f"**{category}**")
            for ent in ents:
                conf = ent.get("confidenceScore", 0)
                st.write(f"• {ent['text']} ({conf:.0%} confidence)")
            st.markdown("")
            
    except KeyError as e:
        st.error(f"Error parsing response: {e}")
        st.json(result)


def render_key_phrases(result: dict):
    """Render key phrase extraction results."""
    try:
        phrases = result["results"]["documents"][0]["keyPhrases"]
        
        if not phrases:
            st.info("No key phrases detected.")
            return
        
        st.markdown(" ".join([f"`{phrase}`" for phrase in phrases]))
        
    except KeyError as e:
        st.error(f"Error parsing response: {e}")
        st.json(result)


def render_language_detection(result: dict):
    """Render language detection results."""
    try:
        lang = result["results"]["documents"][0]["detectedLanguage"]
        
        st.metric(
            label="Detected Language",
            value=lang["name"],
            delta=f"ISO: {lang['iso6391Name']} | Confidence: {lang['confidenceScore']:.0%}"
        )
        
    except KeyError as e:
        st.error(f"Error parsing response: {e}")
        st.json(result)


# App UI
st.title("🧠 Azure AI Studio")
st.markdown("Enterprise-grade AI services powered by Azure Cognitive Services.")

# Sidebar
st.sidebar.header("Services")
service = st.sidebar.radio(
    "Select a service:",
    ["Language Intelligence", "Vision (Coming Soon)", "Speech (Coming Soon)"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Built by**")
st.sidebar.markdown("[Prasad T](https://github.com/tvprasad)")
st.sidebar.markdown("Principal Software Engineer")

if service == "Language Intelligence":
    st.header("🗣️ Language Intelligence")
    st.markdown("Analyze text using Azure AI Language.")
    
    # Sample texts
    sample_texts = {
        "Product Review": "I absolutely love this product! The quality is amazing and shipping was super fast. Would definitely recommend to anyone looking for a reliable solution.",
        "News Article": "Microsoft announced today that it will acquire a leading AI startup based in San Francisco for $2 billion. CEO Satya Nadella said the deal will close in Q3 2026.",
        "Technical Log": "The Kubernetes cluster experienced pod eviction due to memory pressure on node worker-3. The incident was resolved by scaling the deployment horizontally.",
        "Custom": ""
    }
    
    selected_sample = st.selectbox("Choose sample text or write your own:", list(sample_texts.keys()))
    
    if selected_sample == "Custom":
        text_input = st.text_area("Enter your text:", height=150, placeholder="Type or paste text here...")
    else:
        text_input = st.text_area("Enter your text:", value=sample_texts[selected_sample], height=150)
    
    if text_input:
        tab1, tab2, tab3, tab4 = st.tabs(["😊 Sentiment", "🏷️ Entities", "🔑 Key Phrases", "🌍 Language"])
        
        with tab1:
            if st.button("Analyze Sentiment", key="sentiment"):
                with st.spinner("Analyzing..."):
                    result = call_language_api(text_input, "SentimentAnalysis")
                    render_sentiment(result)
        
        with tab2:
            if st.button("Extract Entities", key="entities"):
                with st.spinner("Analyzing..."):
                    result = call_language_api(text_input, "EntityRecognition")
                    render_entities(result)
        
        with tab3:
            if st.button("Extract Key Phrases", key="keyphrases"):
                with st.spinner("Analyzing..."):
                    result = call_language_api(text_input, "KeyPhraseExtraction")
                    render_key_phrases(result)
        
        with tab4:
            if st.button("Detect Language", key="language"):
                with st.spinner("Analyzing..."):
                    result = call_language_api(text_input, "LanguageDetection")
                    render_language_detection(result)
    else:
        st.info("👆 Enter some text above to get started.")

else:
    st.header("🚧 Coming Soon")
    st.markdown("""
    Additional Azure AI services will be added:
    
    - **Vision:** Image analysis, OCR, object detection
    - **Speech:** Speech-to-text, text-to-speech  
    - **Document Intelligence:** Form extraction, document parsing
    """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>Azure AI Studio — Built with Streamlit & Azure Cognitive Services</div>",
    unsafe_allow_html=True
)
