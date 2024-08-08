import streamlit as st
from menu import menu_with_redirect
from style import apply_css
import company as cp


def run():
    st.header('Administration Portal')
    with st.expander('New Client Information', expanded=False):
        st.markdown('#### Create a new Client')
        with st.form('New Client', clear_on_submit=True, border=True):
            cp.newClient()
    with st.expander('Existing Clients', expanded=True):
        st.markdown('#### Get Client Information')
        clients = cp.readClients()
        client = st.selectbox('Client', options=list(clients.keys()), placeholder='Choose a company', index=1)
        with st.container(height=600):
            cp.updateEmailsUsers(client)
            col1, col2 = st.columns([1, 1])
            with col1:
                cp.updateTipExemptEmployees(client)
            with col2:
                cp.updateChefEmployees(client)
            col1, col2 = st.columns([1, 1])
            with col1:
                cp.updateTipPoolNames(client)
            with col2:
                cp.updateOverridePositions(client)
            col1, col2 = st.columns([1, 1])
            with col1:
                cp.updateTipPositions(client)
            with col2:
                cp.updatePositionSplits(client)
        # with st.expander('Register New Username/Email to Client', expanded=False):
        with st.form('Register New Username with Email to Client', clear_on_submit=False, border=True):
            st.subheader('Register New Username with Email')
            email = st.text_input('Email')
            username = st.text_input('Username')
            if st.form_submit_button('Save'):
                cp.associateEmail(email, username)


if __name__ == '__main__':
    apply_css()
    menu_with_redirect()
    run()
