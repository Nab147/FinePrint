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
    st.info(f"Uploaded file: {uploaded_file.name}") # Visual feedback of uploaded file
    with st.spinner("🔍 Scanning your contract..."):
        # ... (rest of your backend call and response handling) ...

        if response.status_code == 200:
            data = response.json()
            st.success("✅ Analysis complete!") # More engaging success icon

            tab1, tab2 = st.tabs(["📋 Plain English Summary", "📊 Detailed Analysis"])

            with tab1:
                if "result_text" in data:
                    st.markdown(data["result_text"]) # Assuming backend might format with Markdown
                else:
                    st.info("No plain English summary available.")

                st.divider()
                st.markdown("**Found something shady?**")
                cols = st.columns(3)
                cols[0].button("🔗 Share", help="Share your analysis") # Icon
                cols[1].button("📋 Copy", help="Copy to clipboard") # Icon
                cols[2].download_button(
                    "💾 Save as PDF", # Icon
                    data=data.get("result_text", "No analysis available."),
                    file_name=f"contract-analysis-{datetime.now().date()}.txt",
                    mime="text/plain"
                )

            with tab2:
                st.subheader("Detailed Analysis (JSON)") # More explicit title
                st.json(data["result_json"])

            st.divider()
            st.markdown("""
            <div style="background-color:#f0f2f6;padding:20px;border-radius:10px">
            <h4 style="color:#1e3a8a">🔓 Coming Soon</h4>
            <ul>
                <li>🚀 Batch contract analysis</li>
                <li>⚙️ Custom templates</li>
                <li>📊 Advanced reporting</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)

        else:
            st.error(f"Error: Could not analyze contract. Please try again.")
    except Exception as e:
        st.error(f"Connection error. Please try again later.")

# Sidebar and Footer (same as before)
with st.sidebar:
    # ...

st.markdown("---")
st.markdown(...)

if __name__ == '__main__':
    main()
