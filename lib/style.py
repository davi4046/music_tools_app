import streamlit as st

def style():
    st.markdown(
            """
        <style>
        div.stButton button {
            width: 100%;
        }
        </style>
        """,
            unsafe_allow_html=True,
    )