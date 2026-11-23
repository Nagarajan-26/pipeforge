import streamlit as st

from pipeforge import __version__
from pipeforge.config import PRODUCT_NAME

st.set_page_config(
    page_title=PRODUCT_NAME,
    page_icon="🔬",
    layout="wide",
)

st.title("PipeForge")
st.subheader(PRODUCT_NAME)

st.caption(
    f"Visual AI Benchmarking for Enterprise Data Operations · v{__version__}"
)

st.info(
    "The benchmark factory is under construction. "
    "Our first milestone is deterministic incident generation and validation."
)

col1, col2, col3 = st.columns(3)

col1.metric("Incident categories", "4", "Planned")
col2.metric("Pipeline topologies", "3", "Planned")
col3.metric("Benchmark tasks", "0", "Not generated yet")

st.markdown("### Development milestones")
st.markdown(
    """
    - [ ] Scenario generation
    - [ ] Incident board rendering
    - [ ] Question and ground-truth generation
    - [ ] Independent validation
    - [ ] Incident Twin Challenge
    - [ ] Multimodal model evaluation
    """
)
