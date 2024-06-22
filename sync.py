import streamlit as st
import pandas as pd


def updated():
    st.session_state['updatedsomething'] = True


def syncInput(widgetkey, tipdatakey):
    st.session_state['updatedsomething'] = True
    try:
        st.session_state['tipdata'][tipdatakey] = float(st.session_state[widgetkey])
    except TypeError:
        st.session_state['tipdata'][tipdatakey] = st.session_state[widgetkey]


def syncDataEditor(edited_df: pd.DataFrame, key: str):
    if 'tipdata' in st.session_state:
        if key in st.session_state['tipdata']:
            if edited_df.equals(st.session_state['tipdata'][key]):
                # Data is unchanged
                return
    st.session_state['updatedsomething'] = True
    st.session_state['tipdata']['updated_'+key] = edited_df


def syncdataframes():
    if 'tipdata' in st.session_state:
        dictionary = st.session_state['tipdata'].copy()
        for key in dictionary:
            if key.startswith('updated_'):
                nkey = key.replace('updated_', '')
                st.session_state['tipdata'][nkey] = dictionary[key]
                del st.session_state['tipdata'][key]
