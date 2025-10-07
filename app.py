import streamlit as st
import time
from utils import load_models, analyze_sentiment_and_generate

# Page config
st.set_page_config(page_title="Sentiment-Aligned AI Writer", layout="wide")

# Initialize session state for history
if "history" not in st.session_state:
    st.session_state.history = []

# Sidebar for chat history
col_left, col_main = st.columns([1, 3])

with col_left:
    st.markdown("### Chat History")
    if len(st.session_state.history) == 0:
        st.info("No interactions yet.")
    else:
        for i, item in enumerate(reversed(st.session_state.history)):
            with st.expander(f"{item['timestamp']} — {item['detected_sentiment']}", expanded=False):
                st.write("**Prompt:**")
                st.write(item["prompt"])
                st.write("**Generated:**")
                st.write(item["generated_text"])
                st.download_button(
                    label="Download this generation",
                    data=item["generated_text"].encode("utf-8"),
                    file_name=f"generation_{i+1}.txt",
                    mime="text/plain",
                )

# Main content
with col_main:
    st.title("Sentiment-Aligned AI Writer")
    st.markdown("Enter a short prompt. The app will detect the sentiment and generate creative text.")

    prompt = st.text_area("Your prompt", placeholder="e.g. Describe a rainy afternoon...", height=120)
    length_option = st.selectbox(
        "Output length",
        ["Short (~50 words)", "Medium (~120 words)", "Long (~220 words)"],
        index=1
    )
    max_length_map = {"Short (~50 words)": 80, "Medium (~120 words)": 200, "Long (~220 words)": 380}
    max_length = max_length_map[length_option]

    start_button = st.button("Start")

    if start_button:
        if not prompt.strip():
            st.warning("Please enter a prompt before starting.")
        else:
            with st.spinner("Loading model and generating text..."):
                models = load_models()  # Lazy load the models
                detected, generated = analyze_sentiment_and_generate(models, prompt, max_length=max_length)

                # Store in history
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.history.append({
                    "prompt": prompt,
                    "detected_sentiment": detected,
                    "generated_text": generated,
                    "timestamp": timestamp
                })

                # Display results
                st.success(f"Detected sentiment: {detected}")
                st.subheader("Generated paragraph")
                st.write(generated)
                st.download_button(
                    label="Download generated text",
                    data=generated.encode("utf-8"),
                    file_name="generated_paragraph.txt",
                    mime="text/plain",
                )
