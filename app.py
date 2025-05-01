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

# CSS (same as before)
st.markdown(...)

# Header with logo
col1, col2 = st.columns([1, 4])
with col1:
    st.image("https://via.placeholder.com/100x100?text=FP", width=90) # Slightly larger logo
with col2:
    st.markdown("<h1>FinePrint AI</h1>", unsafe_allow_html=True) # Larger title
    st.caption("<p style='font-size: 0.9em; color: #777;'>Spot shady contract clauses in seconds</p>", unsafe_allow_html=True) # Subtler caption

# File upload
uploaded_file = st.file_uploader(
    "**Select a PDF Contract to Analyze**", # More explicit label
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
                        # ... (rest of tab1 code) ...

                    with tab2:
                        # ... (rest of tab2 code) ...

                    st.divider()
                    st.markdown(""" ... """, unsafe_allow_html=True)

                else:
                    st.error(f"Error: Could not analyze contract. Status code: {response.status_code}")
            except requests.exceptions.ConnectionError as e:
                st.error(f"Connection error. Please check your internet connection and try again later.")
            except Exception as e:  # <---- ENSURE THIS LINE ENDS WITH A COLON (:)
                st.error(f"An unexpected error occurred: {e}")

# Sidebar and Footer (same as before)
with st.sidebar:
    # ...

st.markdown("---")
st.markdown(...)

if __name__ == '__main__':
    main()
