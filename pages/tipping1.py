import streamlit as st
import numpy as np
import pandas as pd
from menu import menu_with_redirect
from company import publish
from company import servertipdata
from company import clientGetValue
from style import apply_css
from sync import syncInput
from sync import syncDataEditor


def tipIneligible():
    chefs = clientGetValue(st.session_state['company'], 'chefs')
    df = st.session_state['tipdata']['df_work_hours'].copy()
    if 'Tip Exempt Employees' in st.session_state['tipdata']:
        exempt = st.session_state['tipdata']['Tip Exempt Employees']
    else:
        exempt = clientGetValue(st.session_state['company'], 'tipexempt')
    if 'Employees Worked' in st.session_state['tipdata']:
        exempt = set(exempt).intersection(st.session_state['tipdata']['Employees Worked'])
    if len(exempt) == 0:
        exempt = None
    options = np.setdiff1d(st.session_state['tipdata']['Employees Worked'], chefs)
    col20, col21, col22, col23 = st.columns([1, .1, 1, .1])
    try:
        user_not_tipped = col20.multiselect(
                    "Employee's with job classification not eligible for tips",
                    options,
                    default=exempt,
                    key='exempt1', on_change=syncInput, args=('exempt1', 'Tip Exempt Employees')
                )
    except Exception:
        st.error('All names within "Tip_Exempt_Employees.md" must match')
        user_not_tipped = col20.multiselect(
                    "Employee's with job classification not eligible for tips",
                    st.session_state['tipdata']['Employees Worked'],
                    key='exempt2', on_change=syncInput, args=('exempt2', 'Tip Exempt Employees')
                    )
    user_not_tipped = user_not_tipped + chefs
    df_tipEligible = df[~df['Employee Name'].isin(user_not_tipped)].copy()
    df_tipInEligible = df[df['Employee Name'].isin(user_not_tipped)].copy()
    st.session_state['tipdata']['Tip Eligible Employees'] = df_tipEligible['Employee Name'].unique()
    st.session_state['tipdata']['ORIGINAL_WorkedHoursDataUsedForTipping'] = df_tipEligible.copy()
    # st.session_state['tipdata']['WorkedHoursDataUsedForTipping'] = df_tipEligible.copy()
    # st.session_state['tipdata']['Tip Exempt Employees'] = user_not_tipped
    col22.caption('Tip Eligible Employees')
    with col22:
        _str = ' | '
        for names in st.session_state['tipdata']['Tip Eligible Employees']:
            _str += names + ' | '
        st.write(_str)


def chefsPool():
    if 'chefEmployeePool' not in st.session_state['tipdata']:
    #     data = st.session_state['tipdata']['chefEmployeePool']
    # else:
        chefs = clientGetValue(st.session_state['company'], 'chefs')
        data = pd.DataFrame({'Employee Name': chefs, 'Directed': [0.0 for x in chefs]})
        if 'updated_work_shifts' in st.session_state['tipdata']:
            df_tmp = st.session_state['tipdata']['updated_work_shifts'].copy()
            data = pd.merge(left=data, left_on='Employee Name', right=df_tmp, right_on='Employee Name', how='left')
        elif 'work_shifts' in st.session_state['tipdata']:
            df_tmp = st.session_state['tipdata']['work_shifts'].copy()
            data = pd.merge(left=data, left_on='Employee Name', right=df_tmp, right_on='Employee Name', how='left')
        else:
            data['Shifts Worked'] = [0 for x in chefs]
        st.session_state['tipdata']['chefEmployeePool'] = data.copy()
    edited_data = st.data_editor(
        st.session_state['tipdata']['chefEmployeePool'],
        num_rows='fixed' if len(st.session_state['tipdata']['chefEmployeePool']['Employee Name'].to_list()) > 0 else 'dynamic',
        hide_index=True,
        column_order=['Employee Name', 'Shifts Worked', 'Directed'],
        column_config={
            'Employee Name': st.column_config.TextColumn(width='medium', disabled=True),
            'Shifts Worked': st.column_config.NumberColumn(),
            'Directed': st.column_config.NumberColumn(format='$%.2f')
            }
        )
    syncDataEditor(edited_data, 'chefEmployeePool')
    if 'work_shifts' in st.session_state['tipdata']:
        # Convey changes from this table to the total employee worked dataframe
        st.session_state['tipdata']['work_shifts'].update(edited_data.set_index('Employee Name'))
    if 'updated_work_shifts' in st.session_state['tipdata']:
        st.session_state['tipdata']['updated_work_shifts'].update(edited_data.set_index('Employee Name'))
    # if not st.session_state['tipdata']['chefEmployeePool'].equals(st.session_state['tipdata']['updated_chefEmployeePool']):
    #     st.warning('Before navigating to another page, be sure to \'Publish Data\'.')


def run():
    # with st.container(height=650):
    if 'tipdata' not in st.session_state:
        st.session_state['tipdata'] = servertipdata()
    col1, col2 = st.columns([8, 2])
    with col1:
        st.header(st.session_state['company'])
    #     if upload():
    #         st.caption('The data uploaded has been cached for preview on this page only! \
    #                 It will not be available to reference if you navigate to other pages, unless you \'Publish\'. \
    #                 If you navigate to another page or the browser refreshes, the data will be lost. \
    #                 If you uploaded a file, but would like to show the previous data instead, \
    #                 you may remove the files from the upload pop-up.')
    #         st.write('')
    #         st.write('If you would like the data to persist to be referenced on other pages, please \'Publish\'.')
    #         st.session_state['updatetipdata'] = True
    with col2:
        st.caption('')
        publishbutton = st.empty()
    if 'df_work_hours' in st.session_state['tipdata']:
        st.markdown('---')
        st.markdown('### Exclude Employees')
        tipIneligible()
        st.markdown('### Chef Pool Shifts')
        chefsPool()
        # st.write(st.session_state['tipdata'])
        # Publish needs to be at the end to allow for updates read in-line. st.empty container saves the space
        if st.session_state['updatedsomething']:
            if publishbutton.button('Publish Data', key='fromtipping0'):
                publish()
    else:
        st.write('You must first upload and publish Work Hour Data')


if __name__ == '__main__':
    st.set_page_config(
        page_title='TNT Consulting',
        # page_icon='🚊',
        layout='wide'
    )
    if 'company' not in st.session_state:
        st.switch_page("app.py")
    apply_css()
    if 'tipdata' not in st.session_state:
        # st.session_state['tipdata'] = {}
        st.session_state['tipdata'] = servertipdata()
    run()
    menu_with_redirect()
