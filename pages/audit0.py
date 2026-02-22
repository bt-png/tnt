import streamlit as st
import pandas as pd
import numpy as np
from company import publish
from company import servertipdata
from company import clientGetValue
from menu import menu_with_redirect
from style import apply_css
from sync import syncInput
from sync import syncDataEditor


dfs = ['df_audit_sales', 'df_audit_deposits']


# def clear_save_data():
#     # st.session_state['newtipdata'] = {}
#     bitfile = None  # json.dumps(st.session_state['newdict'])
#     # Save locally during testing
#     try:
#         with open('current_save.csv', 'w') as file:
#             file.write(bitfile)
#         st.success('Save Data Has been Saved')
#     except Exception:
#         st.warning('Something went wrong')
#     st.session_state['tipdata'] = {}


# def loadTotalWorkedHours():
#     df = st.session_state['tipdata']['df_work_hours']
#     st.session_state['tipdata']['Total Hours Worked'] = round(df['Regular'].sum(), 2)
#     st.session_state['tipdata']['Employees Worked'] = df['Employee Name'].unique()
#     st.session_state['tipdata']['Total Wages Paid'] = df['Paid Total'].sum()


# def loadWorkPositionList():
#     df = st.session_state['tipdata']['df_work_hours']
#     workedpositions = list(df['Position'].dropna().unique())
#     defaultpositions = clientGetValue(st.session_state['company'], 'overridepositions')
#     allpositions = list(set(workedpositions + defaultpositions))
#     allpositions.sort()
#     st.session_state['tipdata']['Available Work Positions'] = allpositions


# def loadTotalTips():
#     df = st.session_state['tipdata']['df_sales']
#     st.session_state['tipdata']['Raw Pool'] = round(df['Tip'].sum(), 2)
#     st.session_state['tipdata']['Total Pool'] = round(df['Tip'].sum(), 2)


# def loadShiftsWorked():
#     dataframe = st.session_state['tipdata']['df_schedule'].copy()
#     dataframe = dataframe.groupby(['Employee Name']).agg({'Shifts Worked': 'sum'})
#     dataframe.sort_values(by=['Employee Name'], inplace=True)
#     st.session_state['tipdata']['work_shifts'] = dataframe.copy()  # to_dict()

# def updateChefShiftsWorked():
#     if 'work_shifts' not in st.session_state:
#         loadShiftsWorked()
#     df = st.session_state['tipdata']['work_shifts'].copy()
#     dataframe = st.session_state['tipdata']['df_schedule'].copy()
#     st.write(dataframe)



# def save_csv():
#     df = st.session_state['tipdata']['df_work_hours']
#     bitfile = df.to_csv()
#     # st.write(bitfile)
#     try:
#         with open('current_input.csv', 'w') as file:
#             file.write(bitfile)
#         st.success('Work Hours CSV has been Saved')
#     except Exception:
#         st.warning('Something went wrong')


def loadFilestoSessionState(files):
    for df in dfs:
        if df not in st.session_state['tipdata']:
            st.session_state['tipdata'][df] = None
    for file in files:
        try:
            dataframe = pd.read_csv(file)
        except Exception:
            dataframe = pd.read_excel(file)
        if 'Transaction Report' == dataframe.columns[0]:
            dfname = ''
            if 'Prepaid' in dataframe[dataframe.columns[0]][4]:
                dfname = 'df_audit_deposits'
            elif 'Sales' in dataframe[dataframe.columns[0]][4]:
                dfname = 'df_audit_sales'
            if len(dfname) > 0:
                dataframe.drop(labels=[0, 1, 2], axis=0, inplace=True)
                dataframe.drop(labels=dataframe.columns[0], axis=1, inplace=True)
                dataframe.columns = dataframe.iloc[0]
                dataframe.reset_index(drop=True, inplace=True)
                # dataframe.drop(labels=[5], axis=0, inplace=True)
                column_to_check = dataframe.columns[0]
                value_to_find = 'TOTAL'
                if column_to_check in dataframe.columns:
                    total_row_index = dataframe[dataframe[column_to_check].astype(str).str.contains(value_to_find, case=False, na=False)].index
                    if not total_row_index.empty:
                        first_total_idx = total_row_index[0]
                        dataframe = dataframe.loc[3:first_total_idx - 2]# dataframe = dataframe.loc[3:]
                dataframe.reset_index(drop=True, inplace=True)
                if not dataframe.equals(st.session_state['tipdata'][dfname]):
                    st.session_state['updatedsomething'] = True
                    st.session_state['tipdata'][dfname] = dataframe.copy()
                st.dataframe(dataframe)


def allDataFramesLoaded():
    checkSum = 0
    if st.session_state['tipdata']['df_audit_sales'] is not None:
        checkSum += 1
    else:
        st.warning('Sales Audit Data has not been loaded.')
    if st.session_state['tipdata']['df_audit_deposits'] is not None:
        checkSum += 1
    else:
        st.warning('Deposits Audit Data has not been loaded.')
    if checkSum == len(dfs):
        st.success('All Data has been loaded!')
        return True
    return False


# def gardenDatesPicker():
#     st.markdown('---')
#     st.write('Tips related to Garden Events')
#     if 'GardenDates' not in st.session_state['tipdata']:
#     #     data = st.session_state['tipdata']['GardenDates']
#     # else:
#         data = pd.DataFrame({'Dates': []})
#         data['Dates'] = data['Dates'].astype('datetime64[as]')
#         st.session_state['tipdata']['GardenDates'] = data
#     dfDates = st.data_editor(st.session_state['tipdata']['GardenDates'], num_rows='dynamic', key='GardenDates', column_config={
#         'Dates': st.column_config.DateColumn('Garden Event Days', format='MM/DD/YYYY')
#         }).dropna()
#     dfDates.reset_index(drop=True, inplace=True)
#     syncDataEditor(dfDates.copy(), 'GardenDates')
#     # if 'GardenDates' in st.session_state['tipdata']:
#     #     if st.session_state['tipdata']['GardenDates']['Dates'].to_list() != dfDates['Dates'].to_list():
#     #         st.session_state['updatedsomething'] = True
#             # # warning.warning('Before navigating to another page, be sure to \'Publish Data\'.')
#             # st.session_state['tipdata']['GardenDates'] = dfDates.copy()
#     # elif not dfDates.empty:
#     #    st.session_state['updatedsomething'] = True
#     #    warning.warning('Before navigating to another page, be sure to \'Publish Data\'.')
#     #    st.session_state['tipdata']['GardenDates'] = dfDates.copy()
#     try:
#         dfDates['str'] = ["{:%m/%d/%Y}".format(date) for date in dfDates['Dates']]
#     except Exception:
#         dfDates['str'] = None
#     dfDates['str'] = dfDates['str'].astype(str)
#     df = st.session_state['tipdata']['df_sales'].copy()
#     df = df.reset_index()
#     df = pd.merge(left=df, left_on='index', right=dfDates, right_on='str', how='inner')
#     tip = round(df['Tip'].sum(), 2)
#     st.write(f"Tips generated from selected dates = ${format(tip,',')}")
#     # if 'Extra Garden Tip' not in st.session_state['tipdata']:
#     #     st.session_state['tipdata']['Extra Garden Tip'] = 0.0
#     extratip = float(st.text_input(
#         'Venmo/Cash',
#         value=st.session_state['tipdata'].get('Extra Garden Tip', 0.0),
#         key='extragardentips',
#         on_change=syncInput, args=('extragardentips', 'Extra Garden Tip')
#         ))
#     serviceadjustment = float(st.text_input(
#         'Adjustment (+/-)',
#         value=st.session_state['tipdata'].get('Service Charge Adjustment', 0.0),
#         key='serviceadjustment',
#         on_change=syncInput, args=('serviceadjustment', 'Service Charge Adjustment')
#         ))
#     # if extratip != st.session_state['tipdata']['Extra Garden Tip']:
#     #     warning.warning('Before navigating to another page, be sure to \'Publish Data\'.')
#     #     st.session_state['tipdata']['Extra Garden Tip'] = extratip
#     totaltip = round(tip + extratip, 2)
#     # st.write(st.session_state['tipdata']['GardenDates'])
#     if not dfDates.equals(st.session_state['tipdata']['GardenDates']):
#         st.session_state['tipdata']['Base Garden Tip'] = tip
#     # if 'Event Tip' not in st.session_state['tipdata']:
#     # baseGardenTip = st.session_state['tipdata'].get('Base Garden Tip', 0.00)
#     # extraGardenTip = st.session_state['tipdata'].get('Extra Garden Tip', 0.00)
#     eventTip = tip + extratip
#     st.session_state['tipdata']['Event Tip'] = round(eventTip, 2)
#     # if 'Regular Pool' not in st.session_state['tipdata']:
#     dfSales = st.session_state['tipdata']['df_sales']
#     rawTip = round(dfSales['Tip'].sum(), 2)
#     st.session_state['tipdata']['Raw Pool'] = rawTip
#     totalTip = round(rawTip + serviceadjustment, 2)
#     st.session_state['tipdata']['Total Pool'] = totalTip
#     # totalTip = st.session_state['tipdata'].get('Total Pool', 0.00)
#     baseRegularTip = totalTip - tip
#     st.session_state['tipdata']['Regular Pool'] = round(baseRegularTip, 2)


def upload():
    col1, col2 = st.columns([1, 1])
    with col1.popover('Upload 2 Files'):
        files = st.file_uploader('Upload 2 Files', type=['csv', 'xlsx'], accept_multiple_files=True, key='fileuploader')
        if len(files) > 0:
            loadFilestoSessionState(files)
            if allDataFramesLoaded():
                return True
                # _process.continue_run(st.session_state['df_work_hours'])
            return True
    return False


def showdata():
    # if st.session_state['auditdata']['df_schedule'] is not None:
    #     st.markdown('---')
    #     st.markdown('### Schedule Data')
    #     col1, col2 = st.columns([4, 6])
    #     col1.write('Update Shifts Worked')
    #     # data = st.session_state['tipdata']['work_shifts'].copy()
    #     edited_data = col1.data_editor(st.session_state['tipdata']['work_shifts'], num_rows='fixed', key='work_shifts', column_config={
    #         'Employee Name': st.column_config.TextColumn(width='medium', disabled=True),
    #         'Shifts Worked': st.column_config.NumberColumn()
    #     })
    #     syncDataEditor(edited_data, 'work_shifts')
    #     col2.write('Raw Data')
    #     # df_tmp_sch = st.session_state['tipdata']['df_schedule']
    #     col2.dataframe(st.session_state['auditdata']['df_schedule'])
    #     # dfdays = pd.DataFrame({})
    #     # dfdays['Employee Name'] = df_tmp_sch['Employee Name'].unique()
    #     # st.dataframe(dfdays)
    if st.session_state['tipdata']['df_audit_sales'] is not None:
        st.markdown('---')
        st.markdown('### Sales Audit Data')
        # col1, col2 = st.columns([4, 6])
        # with col1:
            # st.write(f"Total Tipping Pool from Raw Data= ${format(st.session_state['tipdata']['Raw Pool'], ',')}")
            # extratips = st.empty()
            # adjustments = st.empty()
            # gardenDatesPicker()
            # if st.session_state['tipdata'].get('Extra Garden Tip', 0.00) != 0.00:
            #     total = st.session_state['tipdata']['Raw Pool'] + st.session_state['tipdata']['Extra Garden Tip']
            #     total += st.session_state['tipdata'].get('Service Charge Adjustment', 0.00)
            #     extratips.write(f"New Tipping Pool = ${format(round(total, 2), ',')}")

        st.write('Raw Data')
        st.dataframe(st.session_state['tipdata']['df_audit_sales'])
    if st.session_state['tipdata']['df_audit_deposits'] is not None:
        st.markdown('---')
        st.markdown('### Deposits Audit Data')
        # col1, col2 = st.columns([4, 6])
        # with col1:
        #     st.write(f"A total of {st.session_state['tipdata']['Total Hours Worked']} hrs were reported \
        #             by {len(st.session_state['tipdata']['Employees Worked'])} employees, \
        #             totaling ${format(st.session_state['tipdata']['Total Wages Paid'], ',')}")
        #     # revisePositionsWorked()
        st.write('Raw Data')
        st.dataframe(st.session_state['tipdata']['df_audit_deposits'])


def run():
    col1, col2 = st.columns([8, 2])
    with col1:
        st.header(st.session_state['company'])
        if upload():
            pass
            # st.session_state['updatedsomething'] = True
            # st.caption('The data uploaded has been cached for preview on this page only! \
            #         It will not be available to reference if you navigate to other pages, unless you \'Publish\'. \
            #         If you navigate to another page or the browser refreshes, the data will be lost. \
            #         If you uploaded a file, but would like to show the previous data instead, \
            #         you may remove the files from the upload pop-up.')
            # st.write('')
            # st.write('If you would like the data to persist to be referenced on other pages, please \'Publish\'.')
            # st.session_state['updatetipdata'] = True
    with col2:
        st.caption('')
        if 'loadedarchive' in st.session_state:
            st.caption(f'Loaded from Archive: {st.session_state["loadedarchive"]}')
        publishbutton = st.empty()
        if st.button('Clear Existing Data'):
            st.session_state['updatedsomething'] = True
            del st.session_state['tipdata']
            publish()
    if st.session_state['tipdata'] != {}:
        # with st.container(height=650):
        showdata()
        # Publish needs to be at the end to allow for updates read in-line. st.empty container saves the space
        if st.session_state['updatedsomething']:
            if publishbutton.button('Publish Data', key='fromaudit0'):
                publish()
                # st.switch_page("pages/tipping0.py")
    else:
        st.markdown('---')
        st.markdown('''
                    ### Instructions: 
                    #### Import 3 Files:  

                    **from When I Work** 
                    1. Timesheets for pay period (staff hours)  
                    2. Scheduler for pay period (chef shifts)   

                    **from Square Reports**  
                    3. Sales summary (broken daily) for time period  

                    #### Reminders:
                    - Once those are loaded - you can complete steps A-C using the 
                    [SOP](https://docs.google.com/document/d/15JG3qYbkNIFvSfBfSI-DMCrhkaO6uVV92cw2xg55URo/edit?usp=sharing).  
                    - You can publish your work to update tables, please do so before moving to new step.
                    ''')


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
        st.session_state['tipdata'] = servertipdata()
    run()
    menu_with_redirect()
