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


dfs = ['df_accruals_invoices']


def dataframe_with_selections(df):
    df_with_selections = df.copy()
    df_with_selections.insert(0, "Select", False)

    # Get dataframe row-selections from user with st.data_editor
    edited_df = st.data_editor(
        df_with_selections,
        hide_index=True,
        column_config={"Select": st.column_config.CheckboxColumn(required=True)},
        disabled=df.columns,
    )

    # Filter the dataframe using the temporary column, then drop the column
    selected_rows = edited_df[edited_df.Select]
    return selected_rows.drop('Select', axis=1)


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
        if 'Invoice Token' == dataframe.columns[0]:
            if not dataframe.equals(st.session_state['tipdata']['df_accruals_invoices']):
                    st.session_state['updatedsomething'] = True
                    st.session_state['tipdata']['df_accruals_invoices'] = dataframe.copy()
            st.dataframe(dataframe)
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
    if st.session_state['tipdata']['df_accruals_invoices'] is not None:
        checkSum += 1
    else:
        st.warning('Invoices Data has not been loaded.')
    # if st.session_state['tipdata']['df_audit_deposits'] is not None:
    #     checkSum += 1
    # else:
    #     st.warning('Deposits Audit Data has not been loaded.')
    if checkSum == len(dfs):
        st.success('All Data has been loaded!')
        return True
    return False


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


def addMonthName(df_, column_to_check, new_name):
    df_[column_to_check] = pd.to_datetime(df_[column_to_check], errors='coerce')
    df_ = df_.dropna(subset=[column_to_check]).copy()
    df_[new_name] = df_[column_to_check].dt.month
    month_names = {
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    }
    df_[new_name] = df_[new_name].map(month_names) + '-' + df_[column_to_check].dt.year.astype(str)
    return df_


def InvoiceColumns():
    return ['Invoice ID', 'Customer Name', 'Invoice Title', 'Status', 'Due Date', 'Last Payment Date', 'Amount Paid', 'Event Date', 'Payment Month', 'Event Month']


def InvoiceAccruals():
    if st.session_state['tipdata']['df_accruals_invoices'] is not None:
        st.markdown('---')
        st.markdown('### Invoice Accruals')
        st.write('Raw Data')
        df_invoice = st.session_state['tipdata']['df_accruals_invoices']
        df_invoice['Amount Paid'] = df_invoice['Amount Paid'].str.replace('$', '', regex=False)
        df_invoice['Amount Paid'] = df_invoice['Amount Paid'].str.replace(',', '', regex=False)
        df_invoice['Amount Paid'] = df_invoice['Amount Paid'].astype(float)
        df_invoice['Amount Paid'] = df_invoice['Amount Paid'].replace(np.nan, 0)
        # df_invoice['Amount Paid'] = df_invoice['Amount Paid'].apply(lambda x: f'${x:,.2f}')
        st.dataframe(df_invoice)
        df_invoice = addMonthName(df_invoice, 'Last Payment Date', 'Payment Month')
        df_invoice = addMonthName(df_invoice, 'Event date', 'Event Month')
        
        df_inv_accr = df_invoice[df_invoice['Payment Month'] != df_invoice['Event Month']]
        df_inv_accr['grouping'] = df_inv_accr['Payment Month'] + ' for ' + df_inv_accr['Event Month']
        st.write('Accrual Items')
        # st.dataframe(df_inv_accr)
        df_Accrual = df_inv_accr.groupby('grouping').agg(
            AccrualTotal=('Amount Paid', 'sum')).reset_index()
        
        
        col1, col2 = st.columns([5,6])
        with col1:
            selection = dataframe_with_selections(df_Accrual)
        with col2:
            st.write("Your selection:")
            union_df = pd.merge(selection, df_inv_accr, on='grouping', how='inner')
            st.dataframe(union_df, column_order=InvoiceColumns(), width=1200)
        
        # Sum Requested Payment Date for Event Date


def showdata():
    InvoiceAccruals()
    

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
        # publishbutton = st.empty()
        # if st.button('Clear Existing Data'):
        #     st.session_state['updatedsomething'] = True
        #     del st.session_state['tipdata']
        #     publish()
    if st.session_state['tipdata'] != {}:
        # with st.container(height=650):
        showdata()
        # Publish needs to be at the end to allow for updates read in-line. st.empty container saves the space
        # if st.session_state['updatedsomething']:
        #     if publishbutton.button('Publish Data', key='fromaudit0'):
        #         publish()
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
