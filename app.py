import streamlit as st
import requests
from datetime import datetime

# Configure page
st.set_page_config(
    page_title="🔍 FinePrint AI",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS for better mobile display
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
    }
    .stDownloadButton>button {
        width: 100%;
    }
    @media (max-width: 768px) {
        .stMarkdown h1 {
            font-size: 1.5rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Header with logo
col1, col2 = st.columns([1, 4])
with col1:
    st.image("https://via.placeholder.com/100x100?text=FP", width=80)
with col2:
    st.title("FinePrint AI")
    st.caption("Spot shady contract clauses in seconds")

# File upload
uploaded_file = st.file_uploader(
    "**Upload your contract (PDF)**",
    type="pdf",
    help="We never store your files after analysis"
)

if uploaded_file:
    with st.spinner("🔍 Scanning your contract..."):
        # Send to backend
        response = requests.post(
            "http://0.0.0.0:5000/analyze",  # Change to your Replit URL
            files={"file": uploaded_file},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Success display
            st.success("Analysis complete!")
            
            # Results tabs
            tab1, tab2 = st.tabs(["📋 Plain English Summary", "📊 Detailed Analysis"])
            
            with tab1:
                st.markdown(data["result_text"])
                
                # Viral sharing
                st.divider()
                st.markdown("**Found something shady?**")
                cols = st.columns(3)
                cols[0].button("Tweet This Clause 🐦", 
                              help="Share your worst clause")
                cols[1].button("Copy as Email 📧", 
                              help="Paste into an email to negotiate")
                cols[2].download_button(
                    "Save as PDF 💾",
                    data=data["result_text"],
                    file_name=f"contract-analysis-{datetime.now().date()}.txt",
                    mime="text/plain"
                )
            
            with tab2:
                st.json(data["result_json"])
            
            # Conversion upsell
            st.divider()
            st.markdown("""
            <div style="background-color:#f0f2f6;padding:20px;border-radius:10px">
            <h4 style="color:#1e3a8a">🔓 Want More Power?</h4>
            <ul>
                <li>Unlimited contract scans</li>
                <li>Pre-written negotiation emails</li>
                <li>Priority support</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.link_button(
                "Get Premium ($5/month)",
                "https://gumroad.com/yourlink",
                type="primary"
            )
            
        else:
            st.error(f"Error {response.status_code}: {response.text}")

# Sidebar for user feedback
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
