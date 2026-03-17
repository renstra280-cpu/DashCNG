import streamlit as st
import base64

def load_layout():
    # =======================
    # PAGE CONFIG
    # =======================
    st.set_page_config(
        page_title="PT Cipta Nirmala",
        layout="wide"
    )

    # =======================
    # BACKGROUND
    # =======================
    st.markdown("""
    <style>
    html, body, [data-testid="stApp"] {
        background-color: #E8F5BD;
    }
    .block-container {
        background-color: #E8F5BD;
    }
    section.main {
        background-color: transparent;
    }
    </style>
    """, unsafe_allow_html=True)

    # =======================
    # HEADER
    # =======================
    col1, col2 = st.columns([1, 25])
    with col1:
        logo = base64.b64encode(
            open("assets/logo_cn_fix.png", "rb").read()
        ).decode()

        st.markdown(f"""
        <div style="margin-top:-3px;">
            <img src="data:image/png;base64,{logo}" width="35">
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="font-family:Arial; margin-top:5px; margin-right:20px;">
            <div style="font-size:15px; font-weight:600; color:#000000;">
                PT CIPTA NIRMALA GROUP
            </div>
        </div>
        """, unsafe_allow_html=True)