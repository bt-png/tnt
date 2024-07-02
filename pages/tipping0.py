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


dfs = ['df_sales', 'df_schedule', 'df_work_hours']


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


def loadTotalWorkedHours():
    df = st.session_state['tipdata']['df_work_hours']
    st.session_state['tipdata']['Total Hours Worked'] = round(df['Regular'].sum(), 2)
    st.session_state['tipdata']['Employees Worked'] = df['Employee Name'].unique()
    st.session_state['tipdata']['Total Wages Paid'] = df['Paid Total'].sum()


def loadWorkPositionList():
    df = st.session_state['tipdata']['df_work_hours']
    workedpositions = list(df['Position'].dropna().unique())
    defaultpositions = clientGetValue(st.session_state['company'], 'overridepositions')
    allpositions = list(set(workedpositions + defaultpositions))
    allpositions.sort()
    st.session_state['tipdata']['Available Work Positions'] = allpositions


def loadTotalTips():
    df = st.session_state['tipdata']['df_sales']
    st.session_state['tipdata']['Total Pool'] = round(df['Tip'].sum(), 2)


def loadShiftsWorked():
    dataframe = st.session_state['tipdata']['df_schedule'].copy()
    dataframe = dataframe.groupby(['Employee Name']).agg({'Shifts Worked': 'sum'})
    dataframe.sort_values(by=['Employee Name'], inplace=True)
    st.session_state['tipdata']['work_shifts'] = dataframe.copy()  # to_dict()


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
        if 'Sales' == dataframe.columns[0]:
            dataframe = dataframe.set_index('Sales').transpose()
            for col in dataframe.columns:
                dataframe[col] = dataframe[col].str.replace('$', '', regex=False)
                dataframe[col] = dataframe[col].str.replace(',', '', regex=False)
                dataframe[col] = dataframe[col].astype(float)
                dataframe[col] = dataframe[col].replace(np.nan, 0)
                tmpcol = dataframe.pop('Tip')
                dataframe.insert(0, 'Tip', tmpcol)
            if not dataframe.equals(st.session_state['tipdata']['df_sales']):
                st.session_state['updatedsomething'] = True
                st.session_state['tipdata']['df_sales'] = dataframe.copy()
                loadTotalTips()
        elif 'Schedule' == dataframe.columns[0]:
            # dataframe = dataframe.transpose()
            dataframe['Employee Name'] = dataframe['First Name'] + ' ' + dataframe['Last Name']
            dataframe.drop(columns=[
                'Employee ID', 'Unpaid Breaks', 'Hourly Rate',
                'Total', 'Total Hours'
                ], inplace=True)  # Drop data with numbers to not alter the shift counts
            dataframe.insert(0, 'Employee Name [Position]', dataframe['Employee Name'] + ' [' + dataframe['Position'] + ']')
            dataframe.sort_values(by=['Employee Name [Position]'], inplace=True)
            dataframe.replace(0, np.nan, inplace=True)
            dataframe.insert(1, 'Shifts Worked', dataframe.count(axis=1, numeric_only=True))
            dataframe.drop(columns=[
                'Schedule', 'Site', 'Position', 'First Name', 'Last Name', 'Email'
                ], inplace=True)  # Drop other columns not necessary
            dataframe.set_index(['Employee Name [Position]'], drop=True, inplace=True)
            if not dataframe.equals(st.session_state['tipdata']['df_schedule']):
                st.session_state['updatedsomething'] = True
                st.session_state['tipdata']['df_schedule'] = dataframe.copy()
                loadShiftsWorked()
        elif 'First Name' == dataframe.columns[0]:
            # st.session_state['val'] = file
            dataframe.insert(0,'Employee Name', dataframe['First Name'] + ' ' + dataframe['Last Name'])
            if not dataframe.equals(st.session_state['tipdata']['df_work_hours']):
                st.session_state['updatedsomething'] = True
                st.session_state['tipdata']['df_work_hours'] = dataframe.copy()
                loadTotalWorkedHours()
                loadWorkPositionList()


def allDataFramesLoaded():
    checkSum = 0
    if st.session_state['tipdata']['df_sales'] is not None:
        checkSum += 1
    else:
        st.warning('Sales Data has not been loaded.')
    if st.session_state['tipdata']['df_work_hours'] is not None:
        checkSum += 1
    else:
        st.warning('Tipping Data has not been loaded.')
    if st.session_state['tipdata']['df_schedule'] is not None:
        checkSum += 1
    else:
        st.warning('Shifts Worked has not been loaded.')
    if checkSum == len(dfs):
        st.success('All Data has been loaded!')
        return True
    return False


def gardenDatesPicker():
    st.markdown('---')
    st.write('Tips related to Garden Events')
    if 'GardenDates' not in st.session_state['tipdata']:
    #     data = st.session_state['tipdata']['GardenDates']
    # else:
        data = pd.DataFrame({'Dates': []})
        data['Dates'] = data['Dates'].astype('datetime64[as]')
        st.session_state['tipdata']['GardenDates'] = data
    dfDates = st.data_editor(st.session_state['tipdata']['GardenDates'], num_rows='dynamic', key='GardenDates', column_config={
        'Dates': st.column_config.DateColumn('Garden Event Days', format='MM/DD/YYYY')
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
    extratip = float(st.text_input(
        'Additional Garden Tips received',
        value=st.session_state['tipdata'].get('Extra Garden Tip', 0.0),
        key='extragardentips',
        on_change=syncInput, args=('extragardentips', 'Extra Garden Tip')
        ))
     serviceadjustment = float(st.text_input(
        'Service Charge Adjustment',
        value=st.session_state['tipdata'].get('Service Charge Adjustment', 0.0),
        key='serviceadjustment',
        on_change=syncInput, args=('serviceadjustment', 'Service Charge Adjustment')
        ))
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
    totalTip = st.session_state['tipdata'].get('Total Pool', 0.00)
    baseRegularTip = totalTip - tip + serviceadjustment
    st.session_state['tipdata']['Regular Pool'] = round(baseRegularTip, 2)


def upload():
    col1, col2 = st.columns([1, 1])
    with col1.popover('Upload New Files'):
        files = st.file_uploader('Upload Files', type=['csv', 'xlsx'], accept_multiple_files=True, key='fileuploader')
        if len(files) > 0:
            loadFilestoSessionState(files)
            if allDataFramesLoaded():
                return True
                # _process.continue_run(st.session_state['df_work_hours'])
            return True
    return False


def showdata():
    if st.session_state['tipdata']['df_schedule'] is not None:
        st.markdown('---')
        st.markdown('### Schedule Data')
        col1, col2 = st.columns([4, 6])
        col1.write('Update Shifts Worked')
        # data = st.session_state['tipdata']['work_shifts'].copy()
        edited_data = col1.data_editor(st.session_state['tipdata']['work_shifts'], num_rows='fixed', key='work_shifts', column_config={
            'Employee Name': st.column_config.TextColumn(width='medium', disabled=True),
            'Shifts Worked': st.column_config.NumberColumn()
        })
        syncDataEditor(edited_data, 'work_shifts')
        col2.write('Raw Data')
        col2.dataframe(st.session_state['tipdata']['df_schedule'])
    if st.session_state['tipdata']['df_sales'] is not None:
        st.markdown('---')
        st.markdown('### Sales Data')
        col1, col2 = st.columns([4, 6])
        with col1:
            st.write(f"Total Tipping Pool from Raw Data= ${format(st.session_state['tipdata']['Total Pool'], ',')}")
            extratips = st.empty()
            gardenDatesPicker()
            if 'Extra Garden Tip' in st.session_state['tipdata']:
                if st.session_state['tipdata']['Extra Garden Tip'] > 0:
                    total = st.session_state['tipdata']['Total Pool'] + st.session_state['tipdata']['Extra Garden Tip']
                    extratips.write(f"New Total Tipping Pool = ${format(round(total, 2), ',')}")
        col2.write('Raw Data')
        col2.dataframe(st.session_state['tipdata']['df_sales'])
    if st.session_state['tipdata']['df_work_hours'] is not None:
        st.markdown('---')
        st.markdown('### Work Hours Data')
        # col1, col2 = st.columns([4, 6])
        # with col1:
        #     st.write(f"A total of {st.session_state['tipdata']['Total Hours Worked']} hrs were reported \
        #             by {len(st.session_state['tipdata']['Employees Worked'])} employees, \
        #             totaling ${format(st.session_state['tipdata']['Total Wages Paid'], ',')}")
        #     # revisePositionsWorked()
        st.write('Raw Data')
        st.dataframe(st.session_state['tipdata']['df_work_hours'])


def run():
    # with st.container(height=650):
    # st.session_state['tipdata'] = servertipdata()
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
            if publishbutton.button('Publish Data', key='fromtipping0'):
                publish()
                # st.switch_page("pages/tipping0.py")


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
