import streamlit as st
import requests
from datetime import datetime

# Configure page
st.set_page_config(
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS (same as before)
st.markdown(...)

# Header with logo
def main():
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image("https://via.placeholder.com/100x100?text=FP", width=80)
    with col2:
        st.title("FinePrint AI")
        st.caption("Spot shady contract clauses in seconds")

    # File upload
    uploaded_file = st.file_uploader(
        "**Upload your contract (PDF)**",
        type=["pdf"],
        help="We never store your files after analysis"
    )

    if uploaded_file:
        with st.spinner("🔍 Scanning your contract..."):
            try:
                response = requests.post(
                    "https://fineprint.onrender.com/analyze",
                    files={"file": uploaded_file},
                    timeout=30
                )

                if response.status_code == 200:
                    data = response.json()

                    st.success("Analysis complete!")

                    tab1, tab2 = st.tabs(["📋 Plain English Summary", "📊 Detailed Analysis"])

                    with tab1:
                        if data["document_type"] == "educational":
                            st.info("This document appears to be educational. The analysis below highlights potential drafting principles and anti-patterns.")
                            if data["result_text"]:
                                st.markdown(data["result_text"])
                        elif data["document_type"] == "contract":
                            st.markdown(data["result_text"])
                        else:
                            st.warning("Could not determine the document type for a plain English summary.")

                        st.divider()
                        st.markdown("**Found something shady?**")
                        cols = st.columns(3)
                        cols[0].button("Share Analysis 🔗", help="Share your analysis")
                        cols[1].button("Copy Results 📋", help="Copy to clipboard")
                        cols[2].download_button(
                            "Save as PDF 💾",
                            data=data.get("result_text", "No analysis available."),
                            file_name=f"contract-analysis-{datetime.now().date()}.txt",
                            mime="text/plain"
                        )

                    with tab2:
                        if data["document_type"] == "educational":
                            st.subheader("Educational Insights")
                            if data["result_json"].get("key_insights"):
                                st.json(data["result_json"]["key_insights"])
                            else:
                                st.info("No detailed educational insights found.")
                        elif data["document_type"] == "contract" and data["result_json"].get("unfair_clauses"):
                            st.subheader("Potentially Problematic Clauses")
                            for i, clause in enumerate(data["result_json"]["unfair_clauses"]):
                                with st.expander(f"Clause {i+1}: {clause['clause'][:100]}..."):
                                    st.markdown(f"**Quoted Text:**\n> {clause['clause']}")
                                    st.error(f"**Potential Risk:** {clause['risk']}")
                                    st.info(f"**Suggested Fix:** {clause['fix']}")
                        elif data["document_type"] == "contract":
                            st.info("No specific unfair clauses were identified in the detailed analysis.")
                        else:
                            st.warning("Detailed analysis is not available for this document type.")

                    st.divider()
                    st.markdown("""
                    <div style="background-color:#f0f2f6;padding:20px;border-radius:10px">
                    <h4 style="color:#1e3a8a">🔓 Coming Soon</h4>
                    <ul>
                        <li>Batch contract analysis</li>
                        <li>Custom templates</li>
                        <li>Advanced reporting</li>
                    </ul>
                    </div>
                    """, unsafe_allow_html=True)

                else:
                    st.error(f"Error: Could not analyze contract. Status code: {response.status_code}")
            except requests.exceptions.ConnectionError as e:
                st.error(f"Connection error. Please check your internet connection and try again later.")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

    # Sidebar and Footer (same as before)
    with st.sidebar:
        st.markdown("### Help Improve FinePrint")
        with st.form(key='feedback'):
            rating = st.slider("How useful was this?", 1, 5, 3)
            comments = st.text_area("What could be better?")
            submitted = st.form_submit_button("Submit Feedback")
            if submitted:
                st.success("Thanks! We'll use this to improve.")

    st.markdown("---")
    st.markdown("""
    <small>
    ⚠️ Disclaimer: FinePrint AI provides educational insights only, not legal advice.
    Consult an attorney for contract review.
    </small>
    """, unsafe_allow_html=True)

if __name__ == '__main__':
    main()
