import streamlit as st
import pandas as pd
import numpy as np
import datetime
import re
from datetime import timedelta
from company import publish
from company import servertipdata
from company import clientGetValue
from menu import menu_with_redirect
from style import apply_css
from sync import syncInput
from sync import syncDataEditor


dfs = ['df_accruals_invoices']


def dataframe_with_selections(df, key_name, default=False):
    df_with_selections = df.copy()
    df_with_selections.insert(0, "Select", default)

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
    return ['Invoice ID', 'Customer Name', 'Invoice Title', 'Status', 'Due Date', 'Last Payment Date', 'Payment Month', 'Amount Paid', 'Event date', 'Event Month', 'Inv Num']


def string_list(data, before, after):
    if len(data)>0:
        val = ', '.join(data.sort_values().to_list())
        val = before + val + after
        return val
    return ''


def filter_RawData(df):
    _df = df.copy()
    col1, col2 = st.columns([8,2])
    col2.write('Apply filters')
    to_filter_columns = ('Event Year', 'Inv Num', 'Customer Name', 'Status', 'Payment Month', 'Event Month')#st.multiselect("Filter dataframe on", df.columns)
    for column in to_filter_columns:
        user_cat_input = col2.multiselect(
            f"Filter on {column}",
            _df[column].unique(),
        )
        if len(user_cat_input) > 0:
            _df = _df[_df[column].isin(user_cat_input)]
    Height = int(35.2 * (12 + 1))
    col1.dataframe(_df, height=Height, hide_index=True, column_order=InvoiceColumns())
    

def show_AR(df_, ardate, armonth, formdata):
    st.markdown('## AR')
    datefilter = datetime.date(ardate.year + ardate.month // 12, ardate.month % 12 + 1, 1)
    # st.markdown('---')
    # st.write('Pending Payment')
    df_Pending = df_[ 
        (df_['Event Month'] == armonth) &
        (df_['Payment Month'] != df_['Event Month'])
                     ]
    # st.dataframe(df_Pending, column_order=InvoiceColumns())
    # st.markdown('---')

    # st.markdown('---')
    # st.write('Payment On Prior Events')
    df_Prior = df_[ 
        (df_['Payment Month'] == armonth) &
        (df_['Event date'].dt.date < datefilter) &
        (df_['Payment Month'] != df_['Event Month'])
                     ]
    # st.dataframe(df_Prior, column_order=InvoiceColumns())
    # st.markdown('---')
    df_sorted = pd.concat([df_Prior, df_Pending], ignore_index=True)
    df_sorted.reset_index(inplace=True)
    df_sorted = df_sorted.groupby('Last Payment for Event Date').agg(
        RequestedTotal=('Requested Amount', 'sum'),
        Counts=('Requested Amount', 'count')).reset_index()
    col1, col2 = st.columns([3,8])
    with col1:
        selection = dataframe_with_selections(df_sorted, 'ar')
    with col2:
        st.write("Your selection:")
        union_df = pd.merge(selection, df_, on='Last Payment for Event Date', how='inner')
        st.dataframe(union_df, column_order=InvoiceColumns(), width=1200)
        st.write(f" Selected Requested: ${format(union_df['Requested Amount'].sum(),',.2f')}")
    col1, col2 = st.columns([3,8])
    with col1:
        # st.write('Payment On Prior Events')
        val_PaymentOn = df_Prior['Requested Amount'].sum()
        st.markdown(f"##### Prior Requested Total: ${format(round(val_PaymentOn,2),',.2f')}") 
    with col2:
        # st.write('Pending Payment')
        val_PendingPayment = df_Pending['Requested Amount'].sum()
        st.markdown(f"##### Pending Requested Total: ${format(val_PendingPayment,',.2f')}")
    formdata['Debit'].iloc[4] = format(val_PaymentOn,'0.2f')
    formdata['Credit'].iloc[3] = format(val_PaymentOn,'0.2f')
    formdata['Memo'].iloc[3] = string_list(df_Prior['Inv Num'],'payment on '+ armonth+ ' events (Inv #',')')
    formdata['Memo'].iloc[4] = formdata['Memo'].iloc[3]
    formdata['Debit'].iloc[15] = format(val_PendingPayment,'0.2f')
    formdata['Credit'].iloc[16] = format(val_PendingPayment,'0.2f')
    formdata['Memo'].iloc[15] = string_list(df_Pending['Inv Num'],'Pending payment on '+ armonth+ ' events (Inv #',')')
    formdata['Memo'].iloc[16] = formdata['Memo'].iloc[15]


def show_FuturePE(df_, ardate, armonth, formdata):
    st.markdown('---')
    st.markdown('## Future PE Deposit')
    datefilter = datetime.date(ardate.year + ardate.month // 12, ardate.month % 12 + 1, 1)
    df_Accrual = df_[
        (df_['Event date'].dt.date >= datefilter) & 
        (df_['Payment Month'] == armonth) &
        (df_['Payment Month'] != df_['Event Month'])
                     ].groupby('Last Payment for Event Date').agg(
        PaidTotal=('Amount Paid', 'sum'),
        Counts=('Amount Paid', 'count')).reset_index()
    col1, col2 = st.columns([3,8])
    with col1:
        selection = dataframe_with_selections(df_Accrual, 'futurepe')
    with col2:
        st.write("Your selection:")
        union_df = pd.merge(selection, df_, on='Last Payment for Event Date', how='inner')
        st.dataframe(union_df, column_order=InvoiceColumns(), width=1200)
        st.write(f" Selected Paid: ${format(union_df['Amount Paid'].sum(),',.2f')}")
    val = df_Accrual['PaidTotal'].sum()
    st.markdown(f"##### Total Paid Future PE: ${format(val,',.2f')}")
    formdata['Debit'].iloc[13] = format(val,'0.2f')
    formdata['Credit'].iloc[12] = format(val,'0.2f')
    formdata['Memo'].iloc[12] = 'Deposit for Future PE'
    formdata['Memo'].iloc[13] = formdata['Memo'].iloc[12]


def show_EventCount(df_, ardate, armonth, formdata):
    st.markdown('---')
    st.markdown('## Event Count')
    col1, col2, col3 = st.columns([1,1,6])
    with col1:
        deposit = st.number_input('Event Deposit', value=500)
    datefilter = datetime.date(ardate.year + ardate.month // 12, ardate.month % 12 + 1, 1)
    df_Accrual = df_[df_['Event Month'] == armonth].reset_index(drop=True)
    # col1, col2 = st.columns([3,8])
    # with col1:
    selection = dataframe_with_selections(df_Accrual, 'eventcounts', True)
    st.write(f" Total Events: {format(len(selection),'0.0f')}")
    # with col2:
        # st.write("Your selection:")
        # st.dataframe(df_Accrual, column_order=InvoiceColumns(), width=1200)
    val = deposit * len(selection)
    st.markdown(f"##### Total Deposits Paid: ${format(val,',.2f')}")
    formdata['Debit'].iloc[9] = format(val,'0.2f')
    formdata['Credit'].iloc[10] = format(val,'0.2f')
    formdata['Memo'].iloc[9] = 'Deposits from ' + armonth + ' Events'
    formdata['Memo'].iloc[10] = formdata['Memo'].iloc[9]
    

def show_ARForm(formdata, armonth):
    st.markdown('---')
    st.markdown('## AR Form for ' + armonth)
    formdata['Memo'].iloc[0] = 'Invoice ____forfeit'
    formdata['Memo'].iloc[1] = formdata['Memo'].iloc[0]
    formdata['Memo'].iloc[6] = armonth + 'GC Sales (SQ + gift up!)'
    formdata['Memo'].iloc[7] = formdata['Memo'].iloc[6]
    Height = int(35.2 * (len(formdata) + 1))
    st.dataframe(formdata, hide_index=True, width=800, height=Height)


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
                    df_invoice['Requested Amount'] = df_invoice['Requested Amount'].str.replace('$', '', regex=False)
                    df_invoice['Requested Amount'] = df_invoice['Requested Amount'].str.replace(',', '', regex=False)
                    df_invoice['Requested Amount'] = df_invoice['Requested Amount'].astype(float)
                    df_invoice['Requested Amount'] = df_invoice['Requested Amount'].replace('', 0)
                    pattern = r'(\d+)'
                    df_invoice['Inv Num'] = df_invoice['Invoice ID'].astype(str).str.extract(pattern, expand=False)
                    condition = df_invoice['Inv Num'].notna()
                    df_invoice.loc[condition, 'Inv Num'] = \
                        df_invoice.loc[condition, 'Inv Num'].astype(float).astype(int).astype(str)
                except Exception:
                    pass
                df_invoice = addMonthName(df_invoice, 'Last Payment Date', 'Payment Month')
                # Adjustment for payment processing delay
                df_invoice['Last Payment Date Processed'] = df_invoice['Last Payment Date'] + timedelta(days=3)
                df_invoice = addMonthName(df_invoice, 'Last Payment Date Processed', 'Payment Month')
                # st.dataframe(df_invoice)
                df_invoice = addMonthName(df_invoice, 'Event date', 'Event Month')
                # col1, col2, col3 = st.columns([1,1,6])
                # with col1:
                #     eventyear = st.number_input('Filter by Event Year', step=1, value=2025)
                # df_invoice = df_invoice[df_invoice['Event date'].dt.year.astype(str) == str(eventyear)]
                # df_invoice.reset_index(drop=True, inplace=True)
                st.write('Raw Data')
                # filter_RawData(df_invoice)
                # st.dataframe(df_invoice, column_order=InvoiceColumns(), width=1200)
                df_invoice['Event Year'] = df_invoice['Event date'].dt.year.astype(str)
                df_invoice['Last Payment for Event Date'] = df_invoice['Payment Month'] + ' for ' + df_invoice['Event Month']
                filter_RawData(df_invoice)
                st.markdown('---')
                col1, col2, col3 = st.columns([1,1,6])
                with col1:
                    ardate = st.date_input('Active AR Month') #, value=df_['Event date'].iloc[-1].date())
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
                show_AR(df_invoice, ardate, armonth, formdata)
                show_FuturePE(df_invoice, ardate, armonth, formdata)
                show_EventCount(df_invoice, ardate, armonth, formdata)
                show_ARForm(formdata, armonth)
    

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
