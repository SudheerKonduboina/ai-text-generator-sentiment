import streamlit as st
from utils import load_models, analyze_and_generate
import time
import os

st.set_page_config(page_title="Sentiment-Aligned AI Writer", layout="wide")

# Load models once
models = load_models()

# Initialize chat history
if "history" not in st.session_state:
    st.session_state.history = []

# Layout
col_left, col_main = st.columns([1, 3])

# Left: Chat History
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

# Right: Main App
with col_main:
    st.title("Sentiment-Aligned AI Writer")
    st.markdown("Enter a short prompt. The app will detect the sentiment and generate creative text.")

    prompt = st.text_area("Your prompt", placeholder="e.g. Describe a rainy afternoon...", height=120)
    length_option = st.selectbox("Output length", ["Short (~50 words)", "Medium (~120 words)", "Long (~220 words)"], index=1)
    max_tokens_map = {"Short (~50 words)": 80, "Medium (~120 words)": 200, "Long (~220 words)": 380}
    max_tokens = max_tokens_map[length_option]

    if st.button("Start Generation"):
        if not prompt.strip():
            st.warning("Please enter a prompt before starting.")
        else:
            with st.spinner("Analyzing sentiment and generating text..."):
                detected, generated = analyze_and_generate(models, prompt, max_tokens=max_tokens)
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                item = {
                    "prompt": prompt,
                    "detected_sentiment": detected,
                    "generated_text": generated,
                    "timestamp": timestamp,
                }
                st.session_state.history.append(item)

                st.success(f"Detected sentiment: {detected}")
                st.subheader("Generated paragraph")
                st.write(generated)
                st.download_button(
                    label="Download generated text",
                    data=generated.encode("utf-8"),
                    file_name=f"generated_{detected.lower()}_{int(time.time())}.txt",
                    mime="text/plain",
                )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    st.run(host="0.0.0.0", port=port)
