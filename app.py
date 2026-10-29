"""Streamlit learning interface for the hybrid knowledge router."""

from pathlib import Path

import streamlit as st

from hybrid_knowledge import HybridKnowledgeBase


PROJECT_DIR = Path(__file__).resolve().parent
knowledge = HybridKnowledgeBase(
    PROJECT_DIR / "okf_knowledge",
    PROJECT_DIR / "rag_knowledge",
)

st.set_page_config(page_title="Hybrid AI Knowledge", page_icon="AI", layout="centered")
st.title("Hybrid AI Knowledge")
st.write(
    "Explore how explicit structured knowledge and semantic retrieval can work "
    "together."
)

with st.expander("How the hybrid architecture works", expanded=True):
        st.code(
                """User question
            |
            v
     Router
     /   \\
    /     \\
OKF     RAG
route   route
    |       |
Markdown  Local text
metadata  similarity
    |       |
    +--- Answer + evidence ---+""",
                language="text",
        )
        st.markdown(
                "**OKF route:** explicit keywords select structured Markdown knowledge.  "
                "**RAG route:** exploratory questions select the closest local text chunk."
        )

example = st.selectbox(
    "Try an example",
    [
        "Choose an example...",
        "What is the authentication protocol?",
        "What fields are in the user schema?",
        "Why is the dashboard incomplete?",
        "What changed after the nightly refresh?",
    ],
)
query = st.text_area(
    "Ask a question",
    value="" if example == "Choose an example..." else example,
    placeholder="For example: What is the authentication protocol?",
    height=90,
)

if st.button("Run query", type="primary"):
    if not query.strip():
        st.warning("Enter a question first.")
    else:
        result = knowledge.route(query)
        st.subheader(result.route)
        st.info(result.reason)

        st.markdown("### Answer")
        st.write(result.answer)

        first_column, second_column = st.columns(2)
        with first_column:
            st.metric("Source", result.source or "None")
        with second_column:
            score = "Not applicable" if result.similarity is None else result.similarity
            st.metric("Similarity", score)

        if result.metadata:
            with st.expander("Inspect structured metadata"):
                st.json(result.metadata)

with st.sidebar:
    st.header("Route guide")
    st.markdown(
        "**Deterministic OKF**\n\n"
        "Used for APIs, protocols, schemas, and rules.\n\n"
        "**Semantic RAG**\n\n"
        "Used for conversational and exploratory questions."
    )

st.divider()
st.caption(
    "Learning principle: use deterministic logic where correctness matters, "
    "and semantic retrieval where discovery matters."
)
