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
        st.markdown('#### Chef Pool')
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
        st.caption('Directed tips are not deducted from the available Tipping Pool. If needing to take from Tipping Pool, it will appear as a negative adjustment.')
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
            st.number_input('#### Chef Percentage (%) of Total Pool',
                            value=int(st.session_state['tipdata'].get('Chef Percent', 18)), min_value=0, max_value=100, step=2,
                            key='ChefPercent0', on_change=syncInput, args=('ChefPercent0', 'Chef Percent')))/100
        totalpool = st.session_state['tipdata']['Event Tip'] + st.session_state['tipdata']['Regular Pool']
        st.session_state['tipdata']['Chef Pool'] = round(chefPercent * totalpool, 2)
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


def prepaidPool():
    # st.markdown('#### Prepaid Employees')
    if 'Prepaid Pool' not in st.session_state['tipdata']:
        st.session_state['tipdata']['Prepaid Pool'] = 0.00
    if 'prepaidEmployeeNamepool' not in st.session_state['tipdata']:
        st.session_state['tipdata']['prepaidEmployeeNamepool'] = []
    col1, col2 = st.columns([1,1])
    with col1:
        prepaidpool = st.multiselect(
                        "#### Prepaid Employees",
                        st.session_state['tipdata']['Tip Eligible Employees'],
                        default=st.session_state['tipdata']['prepaidEmployeeNamepool'], placeholder='Select Employees who have been prepaid tips',
                        key='prepaidpoolemployees', on_change=syncInput, args=('prepaidpoolemployees', 'prepaidEmployeeNamepool')
                    )
        if 'Prepaid Pool Employees' in st.session_state['tipdata']:
            df = st.session_state['tipdata']['Prepaid Pool Employees']
            for idx, row in df.iterrows():
                if row['Employee Name'] not in prepaidpool:
                    df.drop(idx, inplace=True)
            for name in prepaidpool:
                if name not in df['Employee Name'].to_list():
                    df.loc[len(df.index)] = [name, 0.0]
        else:
            df = pd.DataFrame({
                'Employee Name': prepaidpool,
                'Prepaid': [0.00 for x in prepaidpool]
                })
        st.session_state['tipdata']['Prepaid Pool Employees'] = df.copy()
        if len(st.session_state['tipdata']['Prepaid Pool Employees']) > 0:
            st.write('')
            edited_data = st.data_editor(st.session_state['tipdata']['Prepaid Pool Employees'], hide_index=True, num_rows='fixed', column_config={
                    'Employee Name': st.column_config.TextColumn(width='medium',disabled=True),
                    'Prepaid': st.column_config.NumberColumn(format='$%.2f')
                    }
                )
            syncDataEditor(edited_data, 'Prepaid Pool Employees')


def helperPool():
    if 'Helper Pool' not in st.session_state['tipdata']:
        st.session_state['tipdata']['Helper Pool'] = 0.00
    col1, col2 = st.columns([1,1])
    with col1:
        commissioned = clientGetValue(st.session_state['company'], 'commission')
        elligible = st.session_state['tipdata']['Tip Eligible Employees']
        elligible = list(set(list(elligible) + commissioned))
        if 'helperEmployeeNamepool' not in st.session_state['tipdata']:
            st.session_state['tipdata']['helperEmployeeNamepool'] = commissioned
        # st.write(st.session_state['tipdata']['helperEmployeeNamepool'])
        helppool = st.multiselect(
                        "#### Directed Tips",
                        elligible,
                        default=st.session_state['tipdata']['helperEmployeeNamepool'], placeholder='Select Employees to add to the Helper Pool',
                        key='helperpoolemployees', on_change=syncInput, args=('helperpoolemployees', 'helperEmployeeNamepool')
                    )
        if 'Helper Pool Employees' in st.session_state['tipdata']:
            df = st.session_state['tipdata']['Helper Pool Employees']
            for idx, row in df.iterrows():
                if row['Employee Name'] not in helppool:
                    df.drop(idx, inplace=True)
            for name in helppool:
                if name not in df['Employee Name'].to_list():
                    df.loc[len(df.index)] = [name, True, 0.00]
        else:
            df = pd.DataFrame({
                'Employee Name': helppool,
                'Remain in Tip Pool': [True for x in helppool],
                'Directed': [0.0 for x in helppool]
                })
        st.session_state['tipdata']['Helper Pool Employees'] = df.copy()
        if len(st.session_state['tipdata']['Helper Pool Employees']) > 0:
            st.write('')
            edited_data = st.data_editor(st.session_state['tipdata']['Helper Pool Employees'], hide_index=True, num_rows='fixed', column_config={
                    'Employee Name': st.column_config.TextColumn(width='medium',disabled=True),
                    'Remain in Tip Pool': st.column_config.CheckboxColumn(),
                    'Directed': st.column_config.NumberColumn(format='$%.2f')
                }
                )
            syncDataEditor(edited_data, 'Helper Pool Employees')
        else:
            edited_data = pd.DataFrame()
    with col2:
        if not edited_data.empty:
        # if len(st.session_state['tipdata']['Helper Pool Employees']) > 0:
            # st.markdown('#### Distribute')
            pool = edited_data['Directed'].sum()
            st.markdown(f"#### Total Directed= ${'{0:.2f}'.format(pool)}")
            # pool = st.text_input('#### Total Directed ($)',
            #                 value=st.session_state['tipdata'].get('Helper Pool', 0.00),
            #                 key='HelperPool0', on_change=syncInput, args=('HelperPool0', 'Helper Pool'))
            try:
                pool = float(pool)
            except Exception:
                pool = 0.0
            st.session_state['tipdata']['Helper Pool'] = pool
            if pool != 0:
                col10, col20 = st.columns([1,1])
                sliderenabled = False
                if st.session_state['tipdata']['Event Tip'] == 0:
                    st.session_state['tipdata']['Helper Slider'] = 0
                    sliderenabled = True
                elif st.session_state['tipdata']['Regular Pool'] == 0:
                    st.session_state['tipdata']['Helper Slider'] = 100
                    sliderenabled = True
                slider = col10.slider('#### Percentage from Garden Pool', max_value=100, min_value=0, disabled=sliderenabled,
                                    value=int(st.session_state['tipdata'].get('Helper Slider', 75)), step=2, 
                                    key='Helper Slider', on_change=syncInput, args=('Helper Slider', 'Helper Slider'))  # , label_visibility='collapsed')
                with col20.container(border=True):
                    helperDrawGarden = pool * slider/100
                    st.session_state['tipdata']['Helper Draw Garden'] = round(helperDrawGarden, 2)
                    helperDrawRegular = pool - st.session_state['tipdata']['Helper Draw Garden']
                    st.session_state['tipdata']['Helper Draw Regular'] = round(helperDrawRegular, 2)
                    st.markdown(f" From Garden Tip Pool = ${'{0:.2f}'.format(st.session_state['tipdata']['Helper Draw Garden'])}")
                    st.markdown(f" From Regular Tip Pool = ${'{0:.2f}'.format(st.session_state['tipdata']['Helper Draw Regular'])}")
                    # st.markdown('<div style="float:left; text-align:left">Garden Pool</div><div style="float:right; text-align:right">Regular Pool</div>', unsafe_allow_html=True)
            else:
                st.session_state['tipdata']['Helper Draw Garden'] = 0
                st.session_state['tipdata']['Helper Draw Regular'] = 0
        else:
            st.session_state['tipdata']['Helper Draw Garden'] = 0
            st.session_state['tipdata']['Helper Draw Regular'] = 0


def gardenDatesPicker():
    st.markdown('---')
    st.write('Tips related to Large Events')
    if 'GardenDates' not in st.session_state['tipdata']:
    #     data = st.session_state['tipdata']['GardenDates']
    # else:
        data = pd.DataFrame({'Dates': []})
        data['Dates'] = data['Dates'].astype('datetime64[as]')
        st.session_state['tipdata']['GardenDates'] = data
    dfDates = st.data_editor(st.session_state['tipdata']['GardenDates'], num_rows='dynamic', key='GardenDates', column_config={
        'Dates': st.column_config.DateColumn('Large Event Days', format='MM/DD/YYYY')
        }).dropna()
    dfDates.reset_index(drop=True, inplace=True)
    syncDataEditor(dfDates.copy(), 'GardenDates')
    # if 'GardenDates' in st.session_state['tipdata']:
    #     if st.session_state['tipdata']['GardenDates']['Dates'].to_list() != dfDates['Dates'].to_list():
    #         st.session_state['updatedsomething'] = True
            # # warning.warning('Before navigating to another page, be sure to \'Publish Data\'.')
            # st.session_state['tipdata']['GardenDates'] = dfDates.copy()
    # elif not dfDates.empty:
    #    st.session_state['updatedsomething'] = True
    #    warning.warning('Before navigating to another page, be sure to \'Publish Data\'.')
    #    st.session_state['tipdata']['GardenDates'] = dfDates.copy()
    try:
        dfDates['str'] = ["{:%m/%d/%Y}".format(date) for date in dfDates['Dates']]
    except Exception:
        dfDates['str'] = None
    dfDates['str'] = dfDates['str'].astype(str)
    df = st.session_state['tipdata']['df_sales'].copy()
    df = df.reset_index()
    df = pd.merge(left=df, left_on='index', right=dfDates, right_on='str', how='inner')
    tip = round(df['Tip'].sum(), 2)
    st.write(f"Tips generated from selected dates = ${format(tip,',')}")
    # if 'Extra Garden Tip' not in st.session_state['tipdata']:
    #     st.session_state['tipdata']['Extra Garden Tip'] = 0.0
    st.markdown('##### Tip Adjustments (+/-)')
    col1, col2 = st.columns([1,1])
    with col1:
        extratip = st.text_input(
            'Large Events',
            value=st.session_state['tipdata'].get('Extra Garden Tip', 0.0),
            key='extragardentips',
            on_change=syncInput, args=('extragardentips', 'Extra Garden Tip')
            )
        try:
            extratip = float(extratip)
        except Exception:
            extratip = 0.0
            st.session_state['tipdata']['Extra Garden Tip'] = extratip
    with col2:
        serviceadjustment = st.text_input(
            'Regular Days',
            value=st.session_state['tipdata'].get('Service Charge Adjustment', 0.0),
            key='serviceadjustment',
            on_change=syncInput, args=('serviceadjustment', 'Service Charge Adjustment')
            )
        try:
            serviceadjustment = float(serviceadjustment)
        except Exception:
            serviceadjustment = 0.0
            st.session_state['tipdata']['Service Charge Adjustment'] = serviceadjustment
    # if extratip != st.session_state['tipdata']['Extra Garden Tip']:
    #     warning.warning('Before navigating to another page, be sure to \'Publish Data\'.')
    #     st.session_state['tipdata']['Extra Garden Tip'] = extratip
    totaltip = round(tip + extratip, 2)
    # st.write(st.session_state['tipdata']['GardenDates'])
    if not dfDates.equals(st.session_state['tipdata']['GardenDates']):
        st.session_state['tipdata']['Base Garden Tip'] = tip
    # if 'Event Tip' not in st.session_state['tipdata']:
    # baseGardenTip = st.session_state['tipdata'].get('Base Garden Tip', 0.00)
    # extraGardenTip = st.session_state['tipdata'].get('Extra Garden Tip', 0.00)
    eventTip = tip + extratip
    st.session_state['tipdata']['Event Tip'] = round(eventTip, 2)
    # if 'Regular Pool' not in st.session_state['tipdata']:
    dfSales = st.session_state['tipdata']['df_sales']
    rawTip = round(dfSales['Tip'].sum(), 2)
    st.session_state['tipdata']['Raw Pool'] = rawTip
    totalTip = round(rawTip + serviceadjustment, 2)
    st.session_state['tipdata']['Total Pool'] = totalTip
    # totalTip = st.session_state['tipdata'].get('Total Pool', 0.00)
    baseRegularTip = totalTip - tip
    st.session_state['tipdata']['Regular Pool'] = round(baseRegularTip, 2)


def HouseTip():
    # st.caption('House Tip')
    if 'housetipsforemployees' not in st.session_state['tipdata']:
        df = pd.DataFrame({'Employee Name': st.session_state['tipdata']['Employees Worked']})
        df['House Tip'] = 0.0
        st.session_state['tipdata']['housetipsforemployees'] = df.copy()
    df = st.session_state['tipdata']['housetipsforemployees'].copy()
    # current_list_of_employees = st.session_state['tipdata']['WorkedHoursDataUsedForTipping']['Employee Name'].unique()
    current_list_of_employees = st.session_state['tipdata']['ORIGINAL_WorkedHoursDataUsedForTipping']['Employee Name'].unique()
    
    Height = int(35.2 * (len(current_list_of_employees) + 1))
    edited_data = st.data_editor(
        st.session_state['tipdata']['housetipsforemployees'][st.session_state['tipdata']['housetipsforemployees']['Employee Name'].isin(current_list_of_employees)],
        hide_index=True, num_rows='fixed', height=Height,
        column_config={
            'Employee Name': st.column_config.TextColumn(disabled=True),
            'House Tip': st.column_config.NumberColumn(format='$%.2f')
        }
        )
    df.update(edited_data)
    syncDataEditor(df, 'housetipsforemployees')


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
        if 'loadedarchive' in st.session_state:
            st.caption(f'Loaded from Archive: {st.session_state["loadedarchive"]}')
        publishbutton = st.empty()
    if 'df_work_hours' in st.session_state['tipdata']:
        st.markdown('---')
        st.markdown('### Exclude Employees')
        tipIneligible()
        st.markdown('---')
        col1, cola, col2 = st.columns([2,0.1,1])
        with col1:
            st.markdown('### Large Events Breakout')
            st.write(f"Total Tipping Pool from Import Data= ${format(st.session_state['tipdata']['Raw Pool'], ',')}")
            extratips = st.empty()
            adjustments = st.empty()
            gardenDatesPicker()
            if st.session_state['tipdata'].get('Extra Garden Tip', 0.00) != 0.00:
                total = st.session_state['tipdata']['Raw Pool'] + st.session_state['tipdata']['Extra Garden Tip']
                total += st.session_state['tipdata'].get('Service Charge Adjustment', 0.00)
                extratips.write(f"New Tipping Pool = ${format(round(total, 2), ',')}")
            with st.container(border=True):
                col11, col12 = st.columns([1,1])
                with col11:
                    st.markdown(f"#### Total Event\'s Tip Pool = ${st.session_state['tipdata']['Event Tip']}")
                    # st.text_input('#### Event\'s Pool ($)',
                    #              value=st.session_state['tipdata']['Event Tip'], disabled=True,
                    #              key='EventTip0')
                with col12:
                    st.markdown(f"#### Total Regular Tip Pool = ${st.session_state['tipdata']['Regular Pool']}")
                    # st.text_input('#### Regular Pool ($)',
                    #             value=st.session_state['tipdata']['Regular Pool'], disabled=True,
                    #             key='RegularTip0')
        with col2:
            st.markdown('### House Tip Entry')
            HouseTip()
        # st.markdown('---')
        st.markdown('### Specialty Pools')
        helperPool()
        prepaidPool()
        # st.markdown('---')
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
                    if len(st.session_state['tipdata']['GardenDates']['Dates']) > 0:
                        _str = 'Dates | '
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
