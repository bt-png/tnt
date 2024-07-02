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
        options = np.setdiff1d(st.session_state['tipdata']['Employees Worked'], chefs)
    else:
        options = df['Eployee Name'].unique()
    if len(exempt) == 0:
        exempt = None
    options = np.concatenate([options, list(exempt)])
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
    col1, col2 = st.columns([1,1])
    with col1:
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
    with col2:
        chefPercent = int(
            st.number_input('#### Chef Percentage (%) of Regular Pool',
                            value=int(st.session_state['tipdata'].get('Chef Percent', 18)), min_value=0, max_value=100, step=2,
                            key='ChefPercent0', on_change=syncInput, args=('ChefPercent0', 'Chef Percent')))/100
        st.session_state['tipdata']['Chef Pool'] = round(chefPercent * st.session_state['tipdata']['Regular Pool'], 2)
        if chefPercent > 0:
            sliderenabled = False
            if st.session_state['tipdata']['Event Tip'] == 0:
                st.session_state['tipdata']['Chef Slider'] = 100
                sliderenabled = True
            elif st.session_state['tipdata']['Regular Pool'] == 0:
                st.session_state['tipdata']['Chef Slider'] = 0
                sliderenabled = True
            col10, col20 = st.columns([1,1])
            chefslider = col10.slider('#### Percentage from Regular Pool', max_value=100, min_value=0, disabled=sliderenabled,
                                  value=int(st.session_state['tipdata'].get('Chef Slider', 75)), step=5, 
                                  key='Chef Slider', on_change=syncInput, args=('Chef Slider', 'Chef Slider'))  # , label_visibility='collapsed')
            with col20.container(border=True):
                chefDrawRegular = st.session_state['tipdata']['Chef Pool'] * chefslider/100
                st.session_state['tipdata']['Chef Draw Regular'] = round(chefDrawRegular, 2)
                chefDrawGarden = st.session_state['tipdata']['Chef Pool'] - st.session_state['tipdata']['Chef Draw Regular']
                st.session_state['tipdata']['Chef Draw Garden'] = round(chefDrawGarden, 2)
                st.markdown(f"Total Chef Tip Pool = ${st.session_state['tipdata']['Chef Pool']}")
                st.markdown(f" From Garden Tip Pool = ${st.session_state['tipdata']['Chef Draw Garden']}")
                st.markdown(f" From Regular Tip Pool = ${st.session_state['tipdata']['Chef Draw Regular']}")
                # st.markdown('<div style="float:left; text-align:left">Garden Pool</div><div style="float:right; text-align:right">Regular Pool</div>', unsafe_allow_html=True)
        else:
            st.session_state['tipdata']['Chef Draw Garden'] = 0
            st.session_state['tipdata']['Chef Draw Regular'] = 0



def helperPool():
    if 'Helper Pool' not in st.session_state['tipdata']:
        st.session_state['tipdata']['Helper Pool'] = 0.00
    col1, col2 = st.columns([1,1])
    with col1:
        # st.markdown('#### Helper Pool Employees')
        if 'helperEmployeeNamepool' not in st.session_state['tipdata']:
            st.session_state['tipdata']['helperEmployeeNamepool'] = []
        pool = st.multiselect(
                        "#### Helper Pool Employees",
                        st.session_state['tipdata']['Tip Eligible Employees'],
                        default=st.session_state['tipdata']['helperEmployeeNamepool'], placeholder='Select Employees to add to the Helper Pool',
                        key='helperpoolemployees', on_change=syncInput, args=('helperpoolemployees', 'helperEmployeeNamepool')
                    )
        if 'Helper Pool Employees' in st.session_state['tipdata']:
            df = st.session_state['tipdata']['Helper Pool Employees']
            for idx, row in df.iterrows():
                if row['Employee Name'] not in pool:
                    df.drop(idx, inplace=True)
            for name in pool:
                if name not in df['Employee Name'].to_list():
                    df.loc[len(df.index)] = [name, True]
        else:
            df = pd.DataFrame({
                'Employee Name': pool,
                'Remain in Tip Pool': [True for x in pool]
                })
        st.session_state['tipdata']['Helper Pool Employees'] = df.copy()
        if len(st.session_state['tipdata']['Helper Pool Employees']) > 0:
            st.write('')
            edited_data = st.data_editor(st.session_state['tipdata']['Helper Pool Employees'], hide_index=True, num_rows='fixed', column_config={
                    'Employee Name': st.column_config.TextColumn(disabled=True),
                    'Remain in Tip Pool': st.column_config.CheckboxColumn()
                    }
                )
            syncDataEditor(edited_data, 'Helper Pool Employees')
    with col2:
        if len(st.session_state['tipdata']['Helper Pool Employees']) > 0:
            # st.markdown('#### Distribute')
            pool = float(st.text_input('#### Helper Pool ($)',
                            value=st.session_state['tipdata'].get('Helper Pool', 0.00),
                            key='HelperPool0', on_change=syncInput, args=('HelperPool0', 'Helper Pool')))
            if pool > 0:
                col10, col20 = st.columns([1,1])
                sliderenabled = False
                if st.session_state['tipdata']['Event Tip'] == 0:
                    st.session_state['tipdata']['Helper Slider'] = 0
                    sliderenabled = True
                elif st.session_state['tipdata']['Regular Pool'] == 0:
                    st.session_state['tipdata']['Helper Slider'] = 100
                    sliderenabled = True
                slider = col10.slider('#### Percentage from Garden Pool', max_value=100, min_value=0, disabled=sliderenabled,
                                    value=int(st.session_state['tipdata'].get('Helper Slider', 75)), step=5, 
                                    key='Helper Slider', on_change=syncInput, args=('Helper Slider', 'Helper Slider'))  # , label_visibility='collapsed')
                with col20.container(border=True):
                    helperDrawGarden = pool * slider/100
                    st.session_state['tipdata']['Helper Draw Garden'] = round(helperDrawGarden, 2)
                    helperDrawRegular = pool - st.session_state['tipdata']['Helper Draw Garden']
                    st.session_state['tipdata']['Helper Draw Regular'] = helperDrawRegular
                    st.markdown(f" From Garden Tip Pool = ${st.session_state['tipdata']['Helper Draw Garden']}")
                    st.markdown(f" From Regular Tip Pool = ${st.session_state['tipdata']['Helper Draw Regular']}")
                    # st.markdown('<div style="float:left; text-align:left">Garden Pool</div><div style="float:right; text-align:right">Regular Pool</div>', unsafe_allow_html=True)
            else:
                st.session_state['tipdata']['Helper Draw Garden'] = 0
                st.session_state['tipdata']['Helper Draw Regular'] = 0
        else:
            st.session_state['tipdata']['Helper Draw Garden'] = 0
            st.session_state['tipdata']['Helper Draw Regular'] = 0


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
        with st.container(border=True):
            col1, col2 = st.columns([1,1])
            with col1:
                st.markdown(f"#### Total Event\'s Tip Pool = ${st.session_state['tipdata']['Event Tip']}")
                # st.text_input('#### Event\'s Pool ($)',
                #              value=st.session_state['tipdata']['Event Tip'], disabled=True,
                #              key='EventTip0')
            with col2:
                st.markdown(f"#### Total Regular Tip Pool = ${st.session_state['tipdata']['Regular Pool']}")
                # st.text_input('#### Regular Pool ($)',
                #             value=st.session_state['tipdata']['Regular Pool'], disabled=True,
                #             key='RegularTip0')
        # st.markdown('---')
        st.markdown('### Helper Pool')
        helperPool()
        # st.markdown('---')
        st.markdown('### Chef Pool')
        chefsPool()
        # st.markdown('---')
        with st.container(border=True):
            st.markdown('#### Remaining Available Tip Pool')
            col1, col2 = st.columns([1,1])
            with col1:
                baseGardenTip = st.session_state['tipdata'].get('Base Garden Tip', 0.00)
                extraGardenTip = st.session_state['tipdata'].get('Extra Garden Tip', 0.00)
                chefGardenCut = st.session_state['tipdata'].get('Chef Draw Garden', 0.00)
                helperGardenCut = st.session_state['tipdata'].get('Helper Draw Garden', 0.00)
                distributions = chefGardenCut + helperGardenCut
                GardenTip = baseGardenTip + extraGardenTip - distributions
                st.session_state['tipdata']['Avail Event Tip'] = round(GardenTip, 2)
                st.markdown(f"#### Event Days = ${st.session_state['tipdata']['Avail Event Tip']}")
                if 'GardenDates' in st.session_state['tipdata']:
                    _str = 'Held on | '
                    for days in st.session_state['tipdata']['GardenDates']['Dates']:
                        _str += "{:%m/%d/%Y}".format(days) + ' | '
                    st.write(_str)
            with col2:
                regularTip = st.session_state['tipdata']['Regular Pool']
                chefRegularCut = st.session_state['tipdata'].get('Chef Draw Regular', 0.00)
                helperRegularCut = st.session_state['tipdata'].get('Helper Draw Regular', 0.00)
                distributions = chefRegularCut + helperRegularCut
                RegularTip = regularTip - distributions
                st.session_state['tipdata']['Avail Regular Pool'] = round(RegularTip, 2)
                st.markdown(f"#### Regular Days= ${st.session_state['tipdata']['Avail Regular Pool']}")
        dictionary = {}
        dictionary['Garden'] = st.session_state['tipdata']['Avail Event Tip']
        dictionary['Regular'] = st.session_state['tipdata']['Avail Regular Pool']
        dictionary['Helper'] = st.session_state['tipdata']['Helper Pool']
        dictionary['Chefs'] = st.session_state['tipdata']['Chef Pool']
        st.session_state['tipdata']['tippool'] = dictionary
        st.session_state['tipdata']['tiptotals'] = st.session_state['tipdata']['Total Pool'] + st.session_state['tipdata'].get('Extra Garden Tip', 0.00)
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
        st.switch_page("main.py")
    apply_css()
    if 'tipdata' not in st.session_state:
        # st.session_state['tipdata'] = {}
        st.session_state['tipdata'] = servertipdata()
    run()
    menu_with_redirect()
