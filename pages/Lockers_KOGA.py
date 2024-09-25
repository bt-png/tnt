import streamlit as st
import pandas as pd
from firestore_lockers import get_locker_assignments
from firestore_lockers import get_locker_data
from firestore_lockers import post_locker_data
from datetime import datetime, timedelta


def active_combination(locker_num):
    # return _df.loc[_df['Locker'] == locker_num]['Current'].values[0]
    return st.session_state.locker_data.get('Current')


def initial_combination(locker_num):
    return st.session_state.locker_data.get('Start')


def return_combination(locker_num):
    # combinations = _df.loc[_df['Locker'] == locker_num]['Combinations'].values[0]
    combinations = st.session_state.locker_data.get('Combinations')
    active = active_combination(locker_num)
    return combinations[active]


def show_combination(locker_num, verified_combination):
    col1, col2, col3, col4, col5 = st.columns([3,1,3,1,3])
    combo = return_combination(locker_num)
    a, b, c = combo.split('-')
    if verified_combination:
        col1.success(a)
        col3.success(b)
        col5.success(c)
    else:
        col1.warning(a)
        col3.warning(b)
        col5.warning(c)


def next_combination(locker_num):
    # st.text(_df.loc[_df[_df['Locker'] == locker_num].index, 'Current'][0])
    if active_combination(locker_num) == 4:
        st.session_state.locker_data['Current'] = 0
    else:
        st.session_state.locker_data['Current'] += 1
    st.caption('Please try the new combination')
    

def input_locker():
    return st.text_input('Locker Number')


# def load_df():
#     df = pd.DataFrame({
#         'Locker': [12, 13, 14, 15],
#         'Start': [1, 2, 1, 3],
#         'Current': [1, 2, 1, 3],
#         'Combinations': [['0-15-36','1-12-34','2-32-31','3-5-12','4-2-12'], ['0-15-36','1-12-34','2-32-31','3-5-12','4-2-12'], ['0-15-36','1-12-34','2-32-31','3-5-12','4-2-12'], ['0-15-36','1-12-34','2-32-31','3-5-12','4-2-12']],
#         'Assigned': ['Tharp', '', '', ''],
#         'Comments': ['', '', '', '']
#     })
#     df['Combinations'] = df['Combinations'].astype(str)
#     return df


def locker_instructions():
    st.write('''
             ---
             ### Step 1 - CLEAR  
             Spin the dial at least three times to the right, to clear.
             ### Step 2 - RIGHT
             Turn the dial to the RIGHT and stop at your first number.
             ### Step 3 - LEFT
             Turn the dial to the LEFT, going past zero and your first number.
             Then stop at your second number.
             ### Step 4 - RIGHT
             Turn the dial to the RIGHT and go directly to the last number.
             ### Step 5 - OPEN!
''')


def show_locker_combo(locker_num):
    _df = pd.DataFrame()
    if st.session_state.toomanytries:
        st.warning('Looks like something may be wrong. Please visit the front office.')
    else:
        if st.session_state.worked:
            st.subheader('Your locker combo is')
            col1, col2 = st.columns([2,1])
            with col1:
                show_combination(locker_num, True)
            if st.session_state.opened == True:
                st.success('Yeah! Please visit the Google Form linked below for the locker inspection sheet.')
                col1, col2, col3 = st.columns([1,5,1])
                col2.link_button(
                    'Google Form: KOGA Locker Inspection',
                    'https://docs.google.com/forms/d/e/1FAIpQLSc0jER8RakKZrZYbmKsqIurjaFj_H6d8njJZ-6DetI5lHtdZQ/viewform'
                    , use_container_width=True)
            elif st.session_state.opened == False:
                st.warning('Please visit the front office for assistance.')
            else:
                st.write('''Thank you for confirming the locker combination for our records.
                         Did the Locker open as well?''')
                col1, col2 = st.columns([1,1])
                if col1.button('Yes, no issues'):
                    st.session_state.opened = True
                    post_locker_data(locker_num, {'Comments': 'Combo Verified, No Issues'})
                    clear_locker_data()
                    st.rerun()
                if col2.button('No, its stuck'):
                    st.session_state.opened = False
                    post_locker_data(locker_num, {'Comments': 'Cannot Open Door'})
                    clear_locker_data()
                    st.rerun()
        else:
            col1, col2 = st.columns([2,1])
            with col1:
                st.subheader('Your locker combo may be:')
                show_combination(locker_num, False)
            with col2:
                st.container(height=50, border=False)
                if st.button("Lock Opened!"):
                    st.session_state.worked = True
                    post_locker_data(locker_num, {
                        'Comments': 'Combo Verified',
                        'Current': active_combination(locker_num),
                        'Start': active_combination(locker_num),
                        'Verified': datetime.now()})
                    clear_locker_data()
                    st.rerun()
            st.caption('''
                       Try a few times following the instructions provided at the bottom of this page.  
                       If the lock continues to not unlock, let's try a different combination.
                       ''')
            button = st.empty()
            if button.button("Try a different combination"):
                next_combination(locker_num)
                if active_combination(locker_num) == initial_combination(locker_num):
                    st.session_state.toomanytries = True
                    post_locker_data(locker_num, {'Comments': 'All Combos Failed'})
                    clear_locker_data()
                st.rerun()
            locker_instructions()


def clear_locker_data():
    if 'locker_data' in st.session_state:
        st.session_state.pop('locker_data')


def locker_data(locker):
    if 'locker_data' not in st.session_state:
        st.session_state.locker_data = get_locker_data(locker)
        verified = st.session_state.locker_data.get('Verified', '')
        if isinstance(verified, datetime):
            if verified.timestamp() > datetime.today().replace(year=datetime.today().year-1).timestamp():
                st.session_state.worked = True


def run():
    with open('style_lockers.css') as css:
        st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)
    if 'admin_user' not in st.session_state:
        st.session_state.admin_user = False
    # if 'df' not in st.session_state:
    #     st.session_state.df = load_df()
    if 'df_assigned' not in st.session_state:
        st.session_state.df_assigned = get_locker_assignments()
    if 'toomanytries' not in st.session_state:
        st.session_state.toomanytries = False
    if 'worked' not in st.session_state:
        st.session_state.worked = False
    if 'opened' not in st.session_state:
        st.session_state.opened = None
    # df = st.session_state.df
    if st.session_state.admin_user:
        locker = st.text_input('Locker Number')
        if locker != '' and locker.isnumeric:
            locker = int(locker)
            family = st.session_state.df_assigned.get(str(locker))
            if len(family) > 0:
                st.write(f'Assigned Family: {family}')
            else:
                family = st.text_input('Family Name')
                if st.button('Assign Locker to Family'):
                    st.warning('update')
            locker_data(locker)
            show_locker_combo(locker)
        else:
            clear_locker_data()
    else:
        family = st.text_input('Family Name')
        locker = st.text_input('Locker Number')
        if locker != '' and locker.isnumeric and family != '':
            locker = int(locker)
            # if locker in df['Locker'].to_list():
            #     row = df[df['Locker'] == locker]
            if st.session_state.df_assigned.get(str(locker)) == family:
                locker_data(locker)
                show_locker_combo(locker)
            else:
                clear_locker_data()
                st.warning('Locker number is not assigned')
            # else:
            #     st.warning('Locker number is not assigned')
        #st.dataframe(df)


if __name__ == '__main__':
    st.set_page_config(
        page_title='KOGA Locker Assignment',
        layout='wide'
    )
    run()
