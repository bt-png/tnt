import streamlit as st
import streamlit_authentication as st_auth
from company import publish


def authenticated_menu():
    if 'updatedsomething' not in st.session_state:
        st.session_state['updatedsomething'] = False
    # Show a navigation menu for authenticated users
    st.sidebar.header('Hello ' + st.session_state.user_info + '!')
    st.sidebar.markdown('---')
    st.sidebar.page_link("main.py", label="Home")
    if st.session_state['username'] in st.secrets['admin_user']:
        st.sidebar.page_link("pages/admin.py", label="Administration")
    st.sidebar.markdown('---')
    if len(st.session_state['company']) > 0:
        st.sidebar.header(st.session_state['company'])
        st.sidebar.page_link('pages/tipping0.py', label='Import Data')  #, icon='💣')
        st.sidebar.page_link("pages/tipping1.py", label="a. Distribution")
        st.sidebar.page_link("pages/tipping2.py", label="b. Eligibility")
        st.sidebar.page_link("pages/tipping3.py", label="c. Summary")
        
        if st.session_state['updatedsomething']:
            st.sidebar.warning('Changes to data made on this page may not be available \
                               to reference if you navigate to other pages!')
            col1, col2 = st.sidebar.columns([1, 9])
            if col2.button('Publish Data'):
                publish()
            st.sidebar.caption('Please \'Publish Data\' to make sure it is not lost. \
                               If your browser refreshes, the data will be lost.')

    # if st.session_state.role in ["admin", "super-admin"]:
    #     st.sidebar.page_link("ti/admin.py", label="Manage users")
    #     st.sidebar.page_link(
    #         "pages/super-admin.py",
    #         label="Manage admin access",
    #         disabled=st.session_state.role != "super-admin",
    #     )
    st.sidebar.markdown('---')
    st_auth.logout(st.session_state['auth'])
    st.sidebar.markdown('---')
    # if len(st.session_state['company']) > 0:
    #     st.sidebar.header('')
    #     st.sidebar.page_link('pages/tipping0.py', label='Import Data', icon='💣')
    #     st.sidebar.header('')
    #     st.sidebar.markdown('---')


def unauthenticated_menu():
    # Show a navigation menu for unauthenticated users
    st.sidebar.page_link("main.py", label="Log in")


def menu():
    # Determine if a user is logged in or not, then show the correct
    # Show user information
    if 'authentication_status' not in st.session_state or st.session_state['authentication_status'] is None:
        unauthenticated_menu()
        return
    authenticated_menu()


def menu_with_redirect():
    # Redirect users to the main page if not logged in, otherwise continue to
    # render the navigation menu
    if 'authentication_status' not in st.session_state or st.session_state['authentication_status'] is None:
        st.switch_page("main.py")
    menu()
