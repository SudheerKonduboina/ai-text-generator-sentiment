from transformers import pipeline
import streamlit as st
import re

# Instruction-tuned model for text generation
GENERATION_MODEL = "google/flan-t5-small"
SENTIMENT_MODEL = "distilbert-base-uncased-finetuned-sst-2-english"

@st.cache_resource
def load_models():
    """
    Load sentiment analysis and text generation models.
    """
    try:
        sentiment_pipe = pipeline(
            "sentiment-analysis",
            model=SENTIMENT_MODEL,
            device=-1  # CPU; change to 0 for GPU
        )
        gen_pipe = pipeline(
            "text2text-generation",
            model=GENERATION_MODEL,
            device=-1
        )
        return {"sentiment": sentiment_pipe, "generator": gen_pipe}
    except Exception as e:
        st.error(f"Error loading models: {e}")
        return None

def craft_prompt(user_prompt: str, sentiment_label: str) -> str:
    """
    Create a clear instruction prompt for the generation model.
    """
    tone_map = {
        "POSITIVE": "joyful and uplifting",
        "NEGATIVE": "melancholic and reflective",
        "NEUTRAL": "neutral and descriptive"
    }
    tone = tone_map.get(sentiment_label.upper(), "neutral and descriptive")
    return f"Write a single, coherent paragraph in a {tone} tone about the following topic:\n{user_prompt}"

def analyze_sentiment_and_generate(models, prompt: str, max_length: int = 200):
    """
    Detect sentiment and generate aligned text.
    """
    if not models:
        return "ERROR", "Models not loaded."

    if not prompt.strip():
        return "NEUTRAL", "Please provide a prompt."

    # 1. Sentiment detection
    sentiment_result = models["sentiment"](prompt[:512])
    label = sentiment_result[0]["label"]
    score = sentiment_result[0]["score"]

    # If confidence is low, treat as NEUTRAL
    if score < 0.75:
        label = "NEUTRAL"

    # 2. Create generation prompt
    gen_prompt = craft_prompt(prompt, label)

    # 3. Generate text
    outputs = models["generator"](
        gen_prompt,
        max_new_tokens=max_length,
        do_sample=True,
        top_k=50,
        top_p=0.95,
        temperature=0.8,
        num_return_sequences=1
    )
    generated = outputs[0]["generated_text"]

    # 4. Cleanup repetitive/junk text
    generated = re.sub(r"\s+---.*", "", generated)
    generated = generated.strip()
    return label, generated
