from __future__ import annotations

from pathlib import Path

import streamlit as st

from aviation_rag.assistant import ResearchAssistant
from aviation_rag.retrieval import HybridIndex

st.set_page_config(page_title="AeroEvidence", page_icon="✈️", layout="wide")
st.markdown(
    """
    <style>
      .block-container {max-width: 1180px; padding-top: 2rem;}
      [data-testid="stMetric"] {background:#f5f7fb;border:1px solid #e4e8f0;padding:14px;border-radius:12px;}
      .eyebrow {color:#3157a4;font-size:.78rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;}
      .notice {padding:12px 16px;border-left:4px solid #3157a4;background:#f5f7fb;border-radius:6px;}
      .source-card {padding:14px;border:1px solid #e4e8f0;border-radius:10px;margin-bottom:10px;}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def load_assistant() -> ResearchAssistant:
    return ResearchAssistant(HybridIndex.load(Path("data/index/index.json")))


try:
    assistant = load_assistant()
except FileNotFoundError:
    st.error("Index not found. Run `python scripts/build_index.py` first.")
    st.stop()

index = assistant.index
st.markdown('<div class="eyebrow">Independent AI research project</div>', unsafe_allow_html=True)
st.title("AeroEvidence")
st.subheader("Citation-first research across official NTSB aviation reports")
st.markdown(
    '<div class="notice">Research use only. Answers summarize retrieved NTSB records and are not '
    'operational, legal, or safety advice. Always verify the linked final report.</div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Search controls")
    categories = ["Any"] + index.facet_values("aircraft_category")
    weather_options = ["Any"] + index.facet_values("weather_conditions")
    status_options = ["Any"] + index.facet_values("record_status")
    category = st.selectbox("Aircraft category", categories)
    weather = st.selectbox("Weather condition", weather_options)
    record_status = st.selectbox("Report status", status_options)
    date_range = st.slider("Event year", 2009, 2026, (2009, 2026))
    top_k = st.slider("Evidence passages", 2, 10, 5)
    st.divider()
    st.caption(f"{index.document_count} official reports · {len(index.chunks)} searchable passages")
    st.caption("Corpus retrieved from the National Transportation Safety Board.")

examples = [
    "What factors contributed to spatial disorientation in the helicopter accident?",
    "Compare the two runway incursions and their contributing factors.",
    "What mechanical evidence explained the engine power loss?",
    "What does the icing report say about stall risk and deice boots?",
]
selected_example = st.selectbox("Example research questions", ["Choose an example…"] + examples)
default_question = "" if selected_example == "Choose an example…" else selected_example
question = st.text_area(
    "Ask a question about the indexed reports",
    value=default_question,
    placeholder="Ask about weather, causal factors, aircraft, flight phases, or safety controls…",
    height=100,
)

if st.button("Search the evidence", type="primary", use_container_width=True, disabled=not question.strip()):
    filters: dict[str, object] = {
        "event_date": {"$gte": f"{date_range[0]}-01-01", "$lte": f"{date_range[1]}-12-31"}
    }
    if category != "Any":
        filters["aircraft_category"] = category
    if weather != "Any":
        filters["weather_conditions"] = weather
    if record_status != "Any":
        filters["record_status"] = record_status
    with st.spinner("Retrieving and checking evidence…"):
        result = assistant.ask(question.strip(), filters=filters, top_k=top_k)

    st.divider()
    st.subheader("Research synthesis")
    if result.grounded:
        st.success(result.answer)
    else:
        st.warning(result.answer)

    first, second, third, fourth = st.columns(4)
    first.metric("Reports", len({source["document_id"] for source in result.sources}))
    second.metric("Passages", len(result.sources))
    third.metric("Retrieval", f"{result.retrieval_ms:.1f} ms")
    fourth.metric("Citation check", "Passed" if result.grounded else "Abstained")

    st.subheader("Evidence trail")
    for source in result.sources:
        metadata = source["metadata"]
        with st.expander(
            f"[{source['label']}] {source['title']} · relevance {source['score']:.2f}"
        ):
            st.write(source["excerpt"])
            cols = st.columns(4)
            cols[0].caption(f"NTSB NUMBER\n\n{metadata.get('ntsb_number', '—')}")
            cols[1].caption(f"EVENT DATE\n\n{metadata.get('event_date', '—')}")
            cols[2].caption(f"LOCATION\n\n{metadata.get('location', '—')}")
            cols[3].caption(f"STATUS\n\n{metadata.get('record_status', '—')}")
            if source["source_url"]:
                st.link_button("Open official NTSB report", source["source_url"])

with st.expander("About this project"):
    st.write(
        "AeroEvidence ingests official final reports, cleans and chunks their text, combines lexical "
        "and semantic retrieval, applies structured metadata filters, and produces answers with an "
        "inspectable evidence trail. It abstains when the corpus lacks sufficient support."
    )
    st.caption("Not affiliated with or endorsed by the NTSB, FAA, or any employer.")

