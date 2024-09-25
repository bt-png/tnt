import streamlit as st
import pandas as pd
from firestore_lockers import post_locker_data
from firestore_lockers import post_locker_assignments
from firestore_lockers import get_locker_assignments
from pages.Lockers_KOGA import load_df


def import_csv(uploaded_file):
    upload = pd.read_csv(uploaded_file)
    df = pd.DataFrame({
        'Locker': [],
        'Start': [],
        'Current': [],
        'Combinations': [],
        'Assigned': [],
        'Comments': []
    })
    df['Locker'] = upload['Locker #']
    df['Start'] = [x if x != 'UNKNOWN' else 1 for x in upload['2024 Combo in Use']]
    df['Current'] = df['Start']
    df['Combinations'] = [[a, b, c, d, e] for a, b, c, d, e in zip(upload['Green Combo 1'], upload['Purple Combo 2'], upload['Mauve Combo 3'], upload['Orange Combo 4'], upload['Blue Combo 5'])]
    df['Assigned'] = upload['Family Name']
    df['Comments'] = upload['Does the Locker Open']
    return df

if __name__ == '__main__':
    st.set_page_config(
        page_title='KOGA Locker Assignment | Admin',
        layout='wide'
    )
    if 'df' not in st.session_state:
        st.session_state.df = load_df()
    with open('style_lockers.css') as css:
        st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)
    if 'admin_user' not in st.session_state:
        st.session_state.admin_user = False
    if st.session_state.admin_user:
        df = st.session_state.df
        # if 'df_assigned' not in st.session_state:
        #     df_assigned = get_locker_assignments()
        #     st.session_state.df_assigned = df_assigned
        uploaded_file = st.file_uploader('Upload Locker File')
        if uploaded_file != None:
            if uploaded_file.type == 'text/csv':
                new_df = import_csv(uploaded_file)
                st.dataframe(new_df.head())
                col1, col2 = st.columns([1,1])
                if col1.button('Update Locker Assignments', use_container_width=True):
                    _df = new_df[new_df['Assigned'].notna()].reindex(columns = ['Locker', 'Assigned'])
                    _df.set_index('Locker', inplace=True)
                    if post_locker_assignments(_df.transpose().to_dict()):
                        col1.success('Assignments Updated')
                if col2.button('Update Locker Combinations', use_container_width=True):
                    _df = new_df.copy()
                    _df.set_index('Locker', inplace=True)
                    success = []
                    for idx, row in _df.iterrows():
                        success.append(post_locker_data(idx, row.transpose().to_dict()))
                    if all(success):
                        col2.success('Assignments Updated')
        # st.text(st.session_state.df_assigned)
        col1, col2, col3 = st.columns([1,5,1])
        col2.link_button('GoTo Locker Combination Page', 'pages/Lockers_KOGA', use_container_width=True)
    else:
        password = st.text_input('Credentials', type='password')
        if 'locker_admin' in st.secrets:
            if st.secrets.locker_admin == password:
                st.session_state.admin_user = True
                st.rerun()
                