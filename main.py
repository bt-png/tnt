import streamlit as st
import streamlit_authentication as st_auth
from firestore import openconfig
from firestore import userAssociatedCompanies
from company import cpmain
from company import publisharchive
from company import loadarchive
from company import deletearchive
from firestore import listclientArchive
from menu import menu
from style import apply_css


def selectCompany():
    clist = userAssociatedCompanies(st.session_state['username'])
    if len(clist) == 1:
        cpmain(clist[0])
    elif len(clist) > 1:
        clist = list(clist)
        clist.insert(0, '')
        chosen = st.selectbox('Please Select a Company', options=clist, index=clist.index(st.session_state['company']))
        if len(chosen) > 0:
            cpmain(chosen)
        else:
            st.session_state['company'] = ''
    else:
        st.session_state['company'] = ''
        st.write('Please contact support. Your username (',
                 st.session_state['username'],
                 ') is not associated with any companies!')


def updateUser():
    st.markdown('---')
    with st.expander('Update Your Profile', expanded=False):
        st_auth.resetpassword(st.session_state['auth'], st.session_state['config'])
        st_auth.updateuser(st.session_state['auth'], st.session_state['config'])


def loginstatus():
    do_you_have_an_account = st.empty()
    do_you_have_an_account = st.selectbox(
        label='Start here',
        options=('Sign in', 'Sign up', 'I forgot my password', 'I forgot my username'), key='mainone'
        )
    if do_you_have_an_account == 'Sign in':
        user, status, username = st_auth.login(auth)
    elif do_you_have_an_account == 'Sign up':
        email, username, user = st_auth.register(auth, config)
    elif do_you_have_an_account == 'I forgot my password':
        username, email, new_random_password = st_auth.forgotpassword(auth, config)
    elif do_you_have_an_account == 'I forgot my username':
        username, email = st_auth.forgotusername(auth)
    if 'authentication_status' in st.session_state:
        if st.session_state['authentication_status']:
            st.session_state.user_info = user
            st.rerun()
        elif st.session_state['authentication_status'] is False:
            st.sidebar.error('Username/password is incorrect')
        elif st.session_state['authentication_status'] is None and do_you_have_an_account == 'Sign in':
            st.sidebar.warning('Please enter your username and password')


def set_role():
    # Callback function to save the role selection to Session State
    st.session_state.role = st.session_state._role


def archive():
    with st.expander('Archive', expanded = False):
        with st.form('ArchiveForm', clear_on_submit=True):
            st.write('Save an Archive')
            archstring = st.text_input('Name of Archive')
            if st.form_submit_button('Archive'):
                if len(archstring) == 0:
                    st.warning('Please input a name')
                else:
                    publisharchive(archstring)
        with st.form('LoadArchiveFrom', clear_on_submit=True):
            st.write('Load an Archive')
            archload = st.selectbox(
                label='Name of Archive',
                options = listclientArchive(st.session_state['company'])
                )
            if st.form_submit_button('Load'):
                if archload is None:
                    st.warning('Please select an archive')
                else:
                    loadarchive(archstring)
        with st.form('DeleteArchiveFrom', clear_on_submit=True):
            st.write('Delete an Archive')
            archdelete = st.selectbox(
                label='Name of Archive',
                options = listclientArchive(st.session_state['company'])
                )
            if st.form_submit_button('Delete'):
                if archdelete is None:
                    st.warning('Please select an archive')
                else:
                    deletearchive(archdelete)


def home():
    # Launch Page - Not Logged in
    st.header('Payroll Tipping Portal')
    st.write('provided by, TNT Consulting.')
    if 'user_info' not in st.session_state:
        loginstatus()
    else:
        if st.session_state['authentication_status'] is None:
            # Logged out
            st.session_state.clear()
            st.rerun()
        else:
            selectCompany()
            updateUser()
    if st.session_state['username'] in st.secrets['admin_user'] and len(st.session_state['company']) > 0:
        archive()
    menu()  # Render the dynamic menu!

    # st.selectbox(
    #     "Select your role:",
    #     [None, "user", "admin", "super-admin"],
    #     key="_role",
    #     on_change=set_role,
    # )


if __name__ == '__main__':
    st.set_page_config(
        page_title='TNT Consulting',
        # page_icon='🚊',
        layout='wide'
    )
    apply_css()
    config = openconfig()
    st.session_state['config'] = config
    auth = st_auth.authenticate(config)
    st.session_state['auth'] = auth
    # # Initialize st.session_state.role to None
    if 'company' not in st.session_state:
        st.session_state['company'] = ''
    # # Retrieve the role from Session State to initialize the widget
    # st.session_state._role = st.session_state.role
    home()
