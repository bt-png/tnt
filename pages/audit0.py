import streamlit as st
import pandas as pd
import numpy as np
import datetime
from datetime import timedelta
from company import publish
from company import servertipdata
from company import clientGetValue
from menu import menu_with_redirect
from style import apply_css
from sync import syncInput
from sync import syncDataEditor


dfs = ['df_accruals_invoices']


def dataframe_with_selections(df, key_name):
    df_with_selections = df.copy()
    df_with_selections.insert(0, "Select", False)

    # Get dataframe row-selections from user with st.data_editor
    edited_df = st.data_editor(
        df_with_selections,
        hide_index=True,
        column_config={"Select": st.column_config.CheckboxColumn(required=True)},
        disabled=df.columns, key=key_name
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


# def loadFilestoSessionState(files):
#     for df in dfs:
#         if df not in st.session_state['tipdata']:
#             st.session_state['tipdata'][df] = None
#     for file in files:
#         try:
#             dataframe = pd.read_csv(file)
#         except Exception:
#             dataframe = pd.read_excel(file)
#         if 'Invoice Token' == dataframe.columns[0]:
#             if not dataframe.equals(st.session_state['tipdata']['df_accruals_invoices']):
#                     st.session_state['updatedsomething'] = True
#                     st.session_state['tipdata']['df_accruals_invoices'] = dataframe.copy()
#             st.dataframe(dataframe)
#         if 'Transaction Report' == dataframe.columns[0]:
#             dfname = ''
#             if 'Prepaid' in dataframe[dataframe.columns[0]][4]:
#                 dfname = 'df_audit_deposits'
#             elif 'Sales' in dataframe[dataframe.columns[0]][4]:
#                 dfname = 'df_audit_sales'
#             if len(dfname) > 0:
#                 dataframe.drop(labels=[0, 1, 2], axis=0, inplace=True)
#                 dataframe.drop(labels=dataframe.columns[0], axis=1, inplace=True)
#                 dataframe.columns = dataframe.iloc[0]
#                 dataframe.reset_index(drop=True, inplace=True)
#                 # dataframe.drop(labels=[5], axis=0, inplace=True)
#                 column_to_check = dataframe.columns[0]
#                 value_to_find = 'TOTAL'
#                 if column_to_check in dataframe.columns:
#                     total_row_index = dataframe[dataframe[column_to_check].astype(str).str.contains(value_to_find, case=False, na=False)].index
#                     if not total_row_index.empty:
#                         first_total_idx = total_row_index[0]
#                         dataframe = dataframe.loc[3:first_total_idx - 2]# dataframe = dataframe.loc[3:]
#                 dataframe.reset_index(drop=True, inplace=True)
#                 if not dataframe.equals(st.session_state['tipdata'][dfname]):
#                     st.session_state['updatedsomething'] = True
#                     st.session_state['tipdata'][dfname] = dataframe.copy()
#                 st.dataframe(dataframe)


# def allDataFramesLoaded():
#     checkSum = 0
#     if st.session_state['tipdata']['df_accruals_invoices'] is not None:
#         checkSum += 1
#     else:
#         st.warning('Invoices Data has not been loaded.')
#     # if st.session_state['tipdata']['df_audit_deposits'] is not None:
#     #     checkSum += 1
#     # else:
#     #     st.warning('Deposits Audit Data has not been loaded.')
#     if checkSum == len(dfs):
#         st.success('All Data has been loaded!')
#         return True
#     return False


# def upload():
#     col1, col2 = st.columns([1, 1])
#     with col1.popover('Upload 2 Files'):
#         files = st.file_uploader('Upload 2 Files', type=['csv', 'xlsx'], accept_multiple_files=True, key='fileuploader')
#         if len(files) > 0:
#             loadFilestoSessionState(files)
#             if allDataFramesLoaded():
#                 return True
#                 # _process.continue_run(st.session_state['df_work_hours'])
#             return True
#     return False

month_names = {
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    }


def addMonthName(df_, column_to_check, new_name):
    df_[column_to_check] = pd.to_datetime(df_[column_to_check], errors='coerce')
    df_ = df_.dropna(subset=[column_to_check]).copy()
    df_[new_name] = df_[column_to_check].dt.month
    
    df_[new_name] = df_[new_name].map(month_names) + '-' + df_[column_to_check].dt.year.astype(str)
    return df_


def InvoiceColumns():
    return ['Invoice ID', 'Customer Name', 'Invoice Title', 'Status', 'Due Date', 'Last Payment Date', 'Payment Month', 'Amount Paid', 'Event date', 'Event Month']


def show_AR(df_, ardate, armonth, formdata):
    st.markdown('## AR')
    datefilter = datetime.date(ardate.year + ardate.month // 12, ardate.month % 12 + 1, 1)
    df_Accrual = df_[ 
        (df_['Event Month'] == armonth) &
        (df_['Payment Month'] != df_['Event Month'])
                     ]
    df_sorted = df_Accrual.groupby('Last Payment for Event Date').agg(
        AccrualTotal=('Amount Paid', 'sum')).reset_index()
    col1, col2 = st.columns([3,8])
    with col1:
        selection = dataframe_with_selections(df_sorted, 'ar')
    with col2:
        st.write("Your selection:")
        union_df = pd.merge(selection, df_, on='Last Payment for Event Date', how='inner')
        st.dataframe(union_df, column_order=InvoiceColumns(), width=1200)
        st.write(f" Total Selected: ${format(union_df['Requested Amount'].sum(),',')}")
    col1, col2 = st.columns([3,8])
    with col1:
        st.write('Payment On')
        val_PaymentOn = df_Accrual[df_Accrual['Last Payment Date Processed'].dt.date < datefilter]['Requested Amount'].sum()
        st.write(f" Total Current: ${format(val_PaymentOn,',')}")
    with col2:
        st.write('Pending Payment')
        val_PendingPayment = df_Accrual[df_Accrual['Last Payment Date Processed'].dt.date >= datefilter]['Requested Amount'].sum()
        st.write(f" Total Pending: ${format(val_PendingPayment,',')}")
    formdata['Debit'].iloc[4] = val_PaymentOn
    formdata['Credit'].iloc[3] = val_PaymentOn
    formdata['Debit'].iloc[15] = val_PendingPayment
    formdata['Credit'].iloc[16] = val_PendingPayment


def show_FuturePE(df_, ardate, armonth, formdata):
    st.markdown('## Future PE Deposit')
    datefilter = datetime.date(ardate.year + ardate.month // 12, ardate.month % 12 + 1, 1)
    df_Accrual = df_[
        (df_['Event date'].dt.date >= datefilter) & 
        (df_['Payment Month'] == armonth) &
        (df_['Payment Month'] != df_['Event Month'])
                     ].groupby('Last Payment for Event Date').agg(
        AccrualTotal=('Amount Paid', 'sum')).reset_index()
    col1, col2 = st.columns([3,8])
    with col1:
        selection = dataframe_with_selections(df_Accrual, 'futurepe')
    with col2:
        st.write("Your selection:")
        union_df = pd.merge(selection, df_, on='Last Payment for Event Date', how='inner')
        st.dataframe(union_df, column_order=InvoiceColumns(), width=1200)
    val = df_Accrual['AccrualTotal'].sum()
    st.write(f" Total Future PE: ${format(val,',')}")
    formdata['Debit'].iloc[13] = val
    formdata['Credit'].iloc[12] = val


def show_EventCount(df_, ardate, armonth, formdata):
    st.markdown('## Event Count')
    col1, col2, col3 = st.columns([1,1,6])
    with col1:
        deposit = st.number_input('Event Deposit', value=500)
    datefilter = datetime.date(ardate.year + ardate.month // 12, ardate.month % 12 + 1, 1)
    df_Accrual = df_[df_['Event Month'] == armonth].reset_index()
    col1, col2 = st.columns([3,8])
    with col1:
        st.write(f" Total Events: {format(len(df_Accrual),',')}")
    with col2:
        st.write("Your selection:")
        st.dataframe(df_Accrual, column_order=InvoiceColumns(), width=1200)
    val = deposit * len(df_Accrual)
    st.write(f" Total Deposits: ${format(val,',')}")
    formdata['Debit'].iloc[9] = val
    formdata['Credit'].iloc[10] = val
    

def show_ARForm(formdata):
    st.markdown('## Form')
    st.dataframe(formdata, hide_index=True)


def InvoiceAccruals(files):
    for file in files:
        try:
            dataframe = pd.read_csv(file)
        except Exception:
            dataframe = pd.read_excel(file)
        if 'Invoice Token' == dataframe.columns[0]:
            st.markdown('---')
            st.markdown('### Invoice Accruals')
            df_invoice = dataframe.copy() 
            # st.write(df_invoice['Status'].unique())
            drop_list = ['Canceled', 'Refunded', 'Unpaid']
            df_invoice = df_invoice[~df_invoice['Status'].isin(drop_list)].reset_index(drop=True)
            if 'Amount Paid' in df_invoice.columns:
                try:
                    df_invoice['Amount Paid'] = df_invoice['Amount Paid'].str.replace('$', '', regex=False)
                    df_invoice['Amount Paid'] = df_invoice['Amount Paid'].str.replace(',', '', regex=False)
                    df_invoice['Amount Paid'] = df_invoice['Amount Paid'].astype(float)
                    df_invoice['Amount Paid'] = df_invoice['Amount Paid'].replace('', 0)
                except Exception:
                    pass
                df_invoice = addMonthName(df_invoice, 'Last Payment Date', 'Payment Month')
                # Adjustment for payment processing delay
                df_invoice['Last Payment Date Processed'] = df_invoice['Last Payment Date'] + timedelta(days=3)
                df_invoice = addMonthName(df_invoice, 'Last Payment Date Processed', 'Payment Month')
                # st.dataframe(df_invoice)
                df_invoice = addMonthName(df_invoice, 'Event date', 'Event Month')
                col1, col2, col3 = st.columns([1,1,6])
                with col1:
                    eventyear = st.number_input('Filter by Event Year', step=1, value=2025)
                df_invoice = df_invoice[df_invoice['Event date'].dt.year.astype(str) == str(eventyear)]
                df_invoice.reset_index(drop=True, inplace=True)
                st.write('Raw Data')
                st.dataframe(df_invoice, column_order=InvoiceColumns(), width=1200)
                df_inv_accr = df_invoice[df_invoice['Event date'].dt.year.astype(str) == str(eventyear)]
                df_inv_accr['Last Payment for Event Date'] = df_inv_accr['Payment Month'] + ' for ' + df_inv_accr['Event Month']
                st.markdown('---')
                col1, col2, col3 = st.columns([1,1,6])
                with col1:
                    ardate = st.date_input('Event Month') #, value=df_['Event date'].iloc[-1].date())
                st.markdown('---')
                armonth = month_names[ardate.month]+'-'+str(ardate.year)
                formdata = pd.DataFrame(
                    {'Chart of Accounts': [
                    '2. Prepaid Event Deposits', 'Classes & Prepaids', '', 
                    'Accounts Receivable', 'MGF Events', '',
                    'Unredeemed GCs liability', 'MGF Events', '',
                    'Advance Deposits', 'MGF Events', '',
                    'Advance Deposits', 'MGF Events', '',
                    'Accounts Receivable', 'MGF Events'
                    ],
                        'Debit': [0, '', '', '', 0, '', 0, '', '', 0, '', '', '', 0, '', 0, ''], 
                        'Credit': ['', 0, '', 0, '', '', '', 0, '', '', 0, '', 0, '', '', '', 0], 
                        'Memo': ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']}
                        )
                show_AR(df_inv_accr, ardate, armonth, formdata)
                show_FuturePE(df_inv_accr, ardate, armonth, formdata)
                show_EventCount(df_inv_accr, ardate, armonth, formdata)
                show_ARForm(formdata)
    

def run():
    if 'tipdata' not in st.session_state:
        st.session_state['tipdata'] = servertipdata()
    col1, col2 = st.columns([8, 2])
    with col1:
        st.header(st.session_state['company'])
    with col2:
        st.caption('')
    loadedfile = None
    files = st.file_uploader('Upload Accrual Files', type=['csv', 'xlsx'], accept_multiple_files=True, key='accrualfileuploader')
    if len(files) > 0:
        InvoiceAccruals(files)
    else:
        st.markdown('---')
        st.markdown('''
                    ### Instructions: 
                    #### Import Files:  
                    ''')
                    # **from When I Work** 
                    # 1. Timesheets for pay period (staff hours)  
                    # 2. Scheduler for pay period (chef shifts)   

                    # **from Square Reports**  
                    # 3. Sales summary (broken daily) for time period  

                    # #### Reminders:
                    # - Once those are loaded - you can complete steps A-C using the 
                    # [SOP](https://docs.google.com/document/d/15JG3qYbkNIFvSfBfSI-DMCrhkaO6uVV92cw2xg55URo/edit?usp=sharing).  
                    # - You can publish your work to update tables, please do so before moving to new step.
                    # ''')


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
