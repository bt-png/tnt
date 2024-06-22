import streamlit as st


def apply_css():
    with open('style.css') as css:
        st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)
