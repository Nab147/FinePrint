import streamlit as st
import requests
from datetime import datetime
import streamlit.components.v1 as components

# Configure page
st.set_page_config(page_title="🔍 FinePrint AI", page_icon="📄", layout="wide", initial_sidebar_state="expanded")

# Modern styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
:root {
    --primary: #1e3a8a;
    --secondary: #f0f2f6;
    --accent: #3b82f6;
}
body, .stMarkdown, .stButton>button {
    font-family: 'Inter', sans-serif;
}
.stButton>button {
    background-color: var(--accent);
    color: white;
    border-radius: 8px;
    padding: 12px;
    width: 100%;
}
.stButton>button:hover {
    transform: scale(1.05);
    transition: transform 0.2s;
}
@media (max-width: 768px) {
    .stMarkdown h1 { font-size: 1.5rem !important; }
}
</style>
""", unsafe_allow_html=True)

# Header
col1, col2 = st.columns([1, 4])
with col1:
    st.image("logo.png", width=80, caption="FinePrint AI Logo")
with col2:
    st.title("FinePrint AI")
    st.caption("Spot shady contract clauses in seconds")

# File upload
st.markdown('<label for="file-upload" class="sr-only">Upload your contract PDF</label>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("**Upload your contract (PDF)**", type="pdf", key="file-upload", help="We never store your files after analysis")

if uploaded_file:
    if uploaded_file.size > 10 * 1024 * 1024:
        st.warning("File size exceeds 10MB. Please upload a smaller file.")
    else:
        with st.spinner("🔍 Scanning your contract..."):
            progress = st.progress(0)
            progress.progress(33)
            try:
                response = requests.post("https://fineprint.onrender.com/analyze", files={"file": uploaded_file}, timeout=30)
                progress.progress(66)
                if response.status_code == 200:
                    progress.progress(100)
                    data = response.json()
                    st.success("Analysis complete!")
                    
                    # Tabs
                    tab1, tab2 = st.tabs(["📋 Plain English Summary", "📊 Detailed Analysis"])
                    
                    with tab1:
                        for i, clause in enumerate(data["result_json"]["unfair_clauses"]):
                            with st.expander(f"Clause {i+1}: {clause['clause'][:50]}..."):
                                st.markdown(f"**Risk:** {clause['risk']}")
                                st.markdown(f"**Fix:** {clause['fix']}")
                        
                        st.divider()
                        st.markdown("**Found something shady?**")
                        cols = st.columns(3)
                        
                        # Share (placeholder)
                        cols[0].button("Share Analysis 🔗")
                        
                        # Copy
                        def copy_to_clipboard(text):
                            components.html(f"""
                            <button onclick="copyText()">Copy Results 📋</button>
                            <script>
                            function copyText() {{
                                navigator.clipboard.writeText(`{text}`);
                                alert("Results copied to clipboard!");
                            }}
                            </script>
                            """, height=50)
                        cols[1].button("Copy Results 📋", on_click=copy_to_clipboard, args=(data["result_text"],))
                        
                        # Download
                        cols[2].download_button(
                            "Save as PDF 💾",
                            data=data["result_text"],
                            file_name=f"contract-analysis-{datetime.now().date()}.txt",
                            mime="text/plain"
                        )
                    
                    with tab2:
                        st.json(data["result_json"])
                
                else:
                    st.error("Error: Could not analyze contract.")
                    if st.button("Retry"):
                        st.experimental_rerun()
            except Exception as e:
                st.error(f"Connection error: {str(e)}")
                if st.button("Retry"):
                    st.experimental_rerun()

# Sidebar feedback
with st.sidebar:
    st.markdown("### Help Improve FinePrint")
    with st.form(key='feedback'):
        rating = st.slider("How useful was this?", 1, 5, 3)
        comments = st.text_area("What could be better?")
        submitted = st.form_submit_button("Submit Feedback")
        if submitted:
            st.success("Thanks! We'll use this to improve.")

# Footer
st.markdown("---")
st.markdown("""
<small>
⚠️ Disclaimer: FinePrint AI provides educational insights only, not legal advice. 
Consult an attorney for contract review.
</small>
""", unsafe_allow_html=True)
