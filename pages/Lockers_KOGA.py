import streamlit as st
import numpy as np
import pandas as pd
from firestore_lockers import get_locker_assignments
from firestore_lockers import get_locker_data
from firestore_lockers import post_locker_data
from firestore_lockers import reset_locker_data
from firestore_lockers import post_locker_assignments
from firestore_lockers import revoke_locker_assignment
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
    if combinations is None or active is None:
        return None
    else:
        return combinations[active]


def show_combination(locker_num, verified_combination):
    combo = return_combination(locker_num)
    if combo is not None:
        col1, col2, col3, col4, col5 = st.columns([3,1,3,1,3])
        a, b, c = combo.split('-')
        if verified_combination:
            col1.success(a)
            col3.success(b)
            col5.success(c)
        else:
            col1.warning(a)
            col3.warning(b)
            col5.warning(c)
        return combo
    else:
        st.warning('That Locker Number is not found.')
        st.stop()



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


def locker_instructions_cols(numbers: bool):
    if numbers:
        return st.columns([.15,.75,.1])
    else:
        return st.columns([.15,.85])


def locker_instructions(combo):
    if combo is not None:
        a, b, c = combo.split('-')
    st.markdown('---')
    st.write('#### ' + '<div style="text-align:center">'+'General Instructions'+'</div>', unsafe_allow_html=True)
    st.markdown('#### Step 1 - CLEAR')
    col_S1 = locker_instructions_cols(combo is not None)
    col_S1[1].markdown('##### Spin the dial at least three times to the right, to clear.')
    st.markdown('#### Step 2 - RIGHT')
    col_S2 = locker_instructions_cols(combo is not None)
    col_S2[1].markdown('##### Turn the dial to the RIGHT and stop on the first number of the sequence.')
    st.markdown('#### Step 3 - LEFT')
    col_S3 = locker_instructions_cols(combo is not None)
    col_S3[1].markdown('##### Turn the dial to the LEFT, going past zero and the first number of the sequence. Then stop on the second number.')
    st.markdown('#### Step 4 - RIGHT')
    col_S4 = locker_instructions_cols(combo is not None)
    col_S4[1].markdown('##### Turn the dial to the RIGHT and stop directly on the third number of the sequence.')
    st.markdown('#### Step 5 - OPEN!')
    col_S5 = locker_instructions_cols(combo is not None)
    col_S5[1].markdown('##### Pull up on the lift handle.')
    # Images
    col_S1[0].image('images/Step1.png', width=80)
    col_S2[0].image('images/Step2.png', width=80)
    col_S3[0].image('images/Step3.png', width=80)
    col_S4[0].image('images/Step4.png', width=80)
    col_S5[0].image('images/Step5.png', width=80)
    if combo is not None:
        if st.session_state.worked:
            col_S2[2].success(a)
            col_S3[2].success(b)
            col_S4[2].success(c)
        else:
            col_S2[2].warning(a)
            col_S3[2].warning(b)
            col_S4[2].warning(c)
    st.markdown('---')
    # st.link_button('Masterlock Video Tutorial', url='https://youtu.be/vhdbz1ZmxTo?si=yAxgUIaTCjmfDJXc', use_container_width=True)
    col1, col2, col3 = st.columns([1,1,1])
    col2.video(data='https://youtu.be/vhdbz1ZmxTo?si=yAxgUIaTCjmfDJXc')


def show_locker_combo(locker_num):
    # INFO
    # st.text(st.session_state.locker_data)
    _df = pd.DataFrame()
    if st.session_state.toomanytries:
        if st.session_state.admin_user:
            st.warning('Looks like something may be wrong.')
        else:
            st.warning('Looks like something may be wrong. Please visit the front office.')
    else:
        if st.session_state.worked:
            col1, col2 = st.columns([2,1])
            if st.session_state.opened == True:
                st.markdown('---')
                if st.session_state.serialprovided:
                    st.write('##### Yeah! Please visit the Google Form linked below to complete your registration.')
                    col1, col2, col3 = st.columns([1,5,1])
                    col2.link_button(
                        ':memo: Locker Agreement Form',
                        'https://docs.google.com/forms/d/e/1FAIpQLSc0jER8RakKZrZYbmKsqIurjaFj_H6d8njJZ-6DetI5lHtdZQ/viewform'
                        , use_container_width=True)
                else:
                    sn = input_serial()
                    col1, col2 = st.columns([1,1])
                    if col1.button(':white_check_mark: Confirm Serial', use_container_width=True):
                        if len(sn) > 0:
                            post_locker_data(locker_num, {'SerialNumber': sn})
                            clear_locker_data()
                            st.rerun()
                        else:
                            col1.warning('Please enter a serial number')
                    if col2.button(':x: Not Readable', use_container_width=True):
                        post_locker_data(locker_num, {'SerialNumber': 'issue reading'})
                        clear_locker_data()
                        st.rerun()
            elif st.session_state.opened == False:
                st.warning('Please visit the front office for assistance.')
            if st.session_state.opened == None:
                st.markdown('---')
                st.write('''Thank you for confirming the locker combination for our records.
                         Did the Locker open as well?''')
                col1, col2 = st.columns([1,1])
                if col1.button(':white_check_mark: Yes, no issues', use_container_width=True):
                    post_locker_data(locker_num, {'Comments': 'Combo Verified, No Issues'})
                    clear_locker_data()
                    st.rerun()
                if col2.button(':x: No, its stuck', use_container_width=True):
                    post_locker_data(locker_num, {'Comments': 'Cannot Open Door'})
                    clear_locker_data()
                    st.rerun()
            st.markdown('---')
            st.write('#### ' + '<div style="text-align:center">'+'Your Combination is'+'</div>', unsafe_allow_html=True)
            combo = show_combination(locker_num, True)
        else:
            st.markdown('---')
            st.write('#### ' + '<div style="text-align:center">'+'Combination'+'</div>', unsafe_allow_html=True)
            combo = show_combination(locker_num, False)
            st.caption('''
                       Try a few times following the instructions provided at the bottom of this page.  
                       If the lock continues to not unlock, let's try a different combination.
                       ''')
            col1, col2 = st.columns([1,1])
            if col1.button(":x: Try a different combination", use_container_width=True):
                next_combination(locker_num)
                if active_combination(locker_num) == initial_combination(locker_num):
                    post_locker_data(locker_num, {'Comments': 'All Combos Failed'})
                    clear_locker_data()
                st.rerun()
            if col2.button(":white_check_mark: Lock Opened!", use_container_width=True):
                    post_locker_data(locker_num, {
                        'Comments': 'Combo Verified',
                        'Current': active_combination(locker_num),
                        'Start': active_combination(locker_num),
                        'Verified': datetime.now()})
                    clear_locker_data()
                    st.rerun()
        locker_instructions(combo)


def clear_locker_data():
    if 'locker_data' in st.session_state:
        st.session_state.pop('locker_data')
    if st.session_state.toomanytries:
        st.session_state.toomanytries = False
    # if st.session_state.worked:
    #     st.session_state.worked = False
    # if 'opened' in st.session_state:
    #     st.session_state.opened = None


def locker_data(locker):
    if 'locker_data' not in st.session_state:
        st.session_state.locker_data = get_locker_data(locker)
        verified = st.session_state.locker_data.get('Verified', '')
        if isinstance(verified, datetime):
            if verified.timestamp() > datetime.today().replace(year=datetime.today().year-1).timestamp():
                st.session_state.worked = True
        comments = st.session_state.locker_data.get('Comments', '')
        if type(comments) is str:
            if 'No Issues' in comments:
                st.session_state.worked = True
                st.session_state.opened = True
            elif 'All Combos Failed' in comments:
                st.session_state.toomanytries = True
            elif 'Cannot Open Door' in comments:
                st.session_state.toomanytries = True
            if 'Combo Verified' in comments:
                st.session_state.worked = True
        else:
            st.session_state.worked = False
            st.session_state.opened = None
        st.session_state.serialprovided = len(st.session_state.locker_data.get('SerialNumber', '')) > 0


def input_family(default=''):
    col1, col2 = st.columns([.2,.8])
    col1.write('#### ' + '<div style="text-align:center">'+'Family Name'+'</div>', unsafe_allow_html=True)
    if len(default) > 0:
        col2.text_input('Family Name', label_visibility='collapsed', value=default, disabled=True)
    else:
        val = col2.text_input('Family Name', label_visibility='collapsed')
        return val


def input_locker():
    col1, col2 = st.columns([.2,.8])
    col1.write('#### ' + '<div style="text-align:center">'+'Locker Number'+'</div>', unsafe_allow_html=True)
    val = col2.text_input('Locker Number', label_visibility='collapsed', on_change=clear_locker_data)
    return val


def input_serial():
    col1, col2 = st.columns([.2,.8])
    col1.write('#### ' + '<div style="text-align:center">'+'Lock Serial Number'+'</div>', unsafe_allow_html=True)
    val = col2.text_input('Lock Serial Number', label_visibility='collapsed', on_change=clear_locker_data)
    return val


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
    if 'serialprovided' not in st.session_state:
        st.session_state.serialprovided = False
    # df = st.session_state.df
    if st.session_state.admin_user:
        st.write('### ' + '<div style="text-align:center">'+'Administrative View'+'</div>', unsafe_allow_html=True)
        locker = input_locker()
        if locker != '' and locker.isnumeric:
            locker = int(locker)
            family = st.session_state.df_assigned.get(str(locker), '')
            if len(family) > 0:
                input_family(family)
                if st.button(':x: Revoke Family Locker Assignment'):
                    if revoke_locker_assignment(locker):
                        st.session_state.df_assigned.pop(str(locker))
                        st.rerun()
            else:
                family = input_family()
                if st.button(':white_check_mark: Assign Locker to Family'):
                    update = {}
                    val = {'Assigned': family}
                    update[str(locker)] = val
                    if post_locker_assignments(update):
                        st.session_state.df_assigned[str(locker)] = family
                        st.rerun()
                if st.button(':x: Mark "Out of Order"'):
                    update = {}
                    val = {'Assigned': "Out of Order"}
                    update[str(locker)] = val
                    if post_locker_assignments(update):
                        st.session_state.df_assigned[str(locker)] = "Out of Order"
                        st.rerun()
            if st.button(':repeat: Reset Locker Data'):
                reset_locker_data(locker)    
                clear_locker_data()
                st.rerun()
            locker_data(locker)
            show_locker_combo(locker)
    else:
        family = input_family()
        locker = input_locker()
        if locker != '' and locker.isnumeric and family != '':
            locker = int(locker)
            # if locker in df['Locker'].to_list():
            #     row = df[df['Locker'] == locker]
            if st.session_state.df_assigned.get(str(locker)) == family:
                locker_data(locker)
                show_locker_combo(locker)
            else:
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
