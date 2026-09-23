import streamlit as st
import numpy as np
import pandas as pd
import re
from datetime import datetime
from menu import menu_with_redirect
from company import publish
from company import servertipdata
from company import clientGetValue
from style import apply_css
from sync import syncInput
from sync import syncDataEditor


def SalesFullColumns():
    return ['Num', 'Description', 'Amount']

def DepositFullColumns():
    return ['Transaction date', 'Description', 'Amount']

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


def salesloadfile(files):
    try:
        try:
            dataframe = pd.read_csv(files)
        except Exception:
            dataframe = pd.read_excel(files)
    # try:
    # if 'Sales' in dataframe[dataframe.columns[0]][4]:
        # dataframe.drop(labels=[0, 1, 2], axis=0, inplace=True)
        # dataframe.drop(labels=dataframe.columns[0], axis=1, inplace=True)
        # dataframe.columns = dataframe.iloc[0]
        # dataframe.reset_index(drop=True, inplace=True)
        
        # dataframe.drop(labels=[5], axis=0, inplace=True)
        # column_to_check = dataframe.columns[0]
        # value_to_find = 'TOTAL'
        # if column_to_check in dataframe.columns:
        #     total_row_index = dataframe[dataframe[column_to_check].astype(str).str.contains(value_to_find, case=False, na=False)].index
        #     if not total_row_index.empty:
        #         first_total_idx = total_row_index[0]
        #         dataframe = dataframe.loc[3:first_total_idx - 2]# dataframe = dataframe.loc[3:]
        # dataframe.reset_index(drop=True, inplace=True)
        # st.markdown('---')
        # st.markdown('### RawData')
        # st.write(dataframe)
    except Exception:
        dataframe = None
    return dataframe


def depositloadfile(files):
    try:
        try:
            dataframe = pd.read_csv(files)
        except Exception:
            dataframe = pd.read_excel(files)
    # if 'Deposits' in dataframe[dataframe.columns[0]][4]:
        # dataframe.drop(labels=[0, 1, 2], axis=0, inplace=True)
        # dataframe.drop(labels=dataframe.columns[0], axis=1, inplace=True)
        # dataframe.columns = dataframe.iloc[0]
        # dataframe.reset_index(drop=True, inplace=True)
        # # dataframe.drop(labels=[5], axis=0, inplace=True)
        # column_to_check = dataframe.columns[0]
        # value_to_find = 'TOTAL'
        # if column_to_check in dataframe.columns:
        #     total_row_index = dataframe[dataframe[column_to_check].astype(str).str.contains(value_to_find, case=False, na=False)].index
        #     if not total_row_index.empty:
        #         first_total_idx = total_row_index[0]
        #         dataframe = dataframe.loc[3:first_total_idx - 2]# dataframe = dataframe.loc[3:]
        dataframe.reset_index(drop=True, inplace=True)
    except Exception:
        dataframe = None
    return dataframe


def addMonthName(df_):
    column_to_check = df_.columns[0]
    df_[column_to_check] = pd.to_datetime(df_[column_to_check], errors='coerce')
    df_ = df_.dropna(subset=[column_to_check]).copy()
    df_['Trans Month'] = df_[column_to_check].dt.month
    month_names = {
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    }
    df_['Trans Month Name'] = df_['Trans Month'].map(month_names)
    df_['Trans Date'] = df_[column_to_check].dt.strftime('%Y-%m-%d')
    return df_


def addFromTo(df_):
    df_['FROM'] = \
        df_['Description'].astype(str).str.split('for', n=1, expand=True)[0].str.strip()
    df_['FROM'] = \
        df_['FROM'].astype(str).str.split(' ', n=1, expand=True)[0].str.strip()
    df_['TO'] = \
            df_['Description'].astype(str).str.split('for', n=1, expand=True)[1].str.strip()
    df_['TO'] = \
        df_['TO'].astype(str).str.split(' ', n=1, expand=True)[0].str.strip()
    return df_


def adjustMemo(df_):
    df_['Clean Memo'] = df_['Description'].astype(str).str.strip()
    pattern = r'(\d+)'
    df_['Extr Num'] = df_['Clean Memo'].astype(str).str.extract(pattern, expand=False)
    condition = df_['Extr Num'].notna()
    df_.loc[condition, 'Extr Num'] = \
        df_.loc[condition, 'Extr Num'].astype(float).astype(int).astype(str)
    df_.loc[condition, 'Clean Memo'] = df_.loc[condition, 'Extr Num']
    return df_


def show_groupNetJE(df_):
    col1, col2 = st.columns([5,6])
    with col1:
        JENet = df_.groupby('Clean Memo').agg(
            NetJETotal=('Amount', 'sum'),
            NetJECount=('Amount', 'count')
            ).reset_index()
        JENet = JENet[JENet['NetJETotal'] != 0]
        selection = dataframe_with_selections(JENet)
    with col2:
        st.write("Your selection:")
        union_df = pd.merge(selection, df_, on='Clean Memo', how='inner')
        st.dataframe(union_df, column_order=SalesFullColumns(), width=800)


def show_firstJE(df_):
    filtered_df = df_[df_['Extr Num'].notna()]
    first_rows = filtered_df.drop_duplicates(subset='Clean Memo', keep='first')
    
    st.dataframe(first_rows[first_rows['Amount'] < 0],
                 column_order=['Transaction date', 'Memo/Description', 'Amount'])


def show_MonthMatchesAmount(df_):
    filtered_from = df_[df_['FROM'] == df_['Trans Month Name']]
    from_df_errors = filtered_from[filtered_from['Amount'] < 0]
    if from_df_errors.empty:
        st.write('No Errors in Active Month')
    else:
        st.write('Active Month (Negative)')
        st.dataframe(from_df_errors,
                 column_order=['Transaction date', 'Memo/Description', 'Amount'])
    filtered_to = df_[df_['TO'] == df_['Trans Month Name']]
    to_df_errors = filtered_to[filtered_to['Amount'] > 0]
    if to_df_errors.empty:
        st.write('No Errors in Moving Month')
    else:
        st.write('Moving Month (Positive)')
        st.dataframe(to_df_errors,
                 column_order=['Transaction date', 'Memo/Description', 'Amount'])


# Extract FROM and TO month from description.

# Process Month to Month Batches
# FROM Amount is + and matches transaction 
# TO Amount is - and matches transaction

# Process full file
# Matching descirption amounts net zero  


# Errors if:   

def show_groupNetJEdeposit(df_, df_sales_):
    col1, col2 = st.columns([5,6])
    with col1:
        JENet = df_.groupby('Clean Memo').agg(
            NetJETotal=('Amount', 'sum'),
            NetJECount=('Amount', 'count')
            ).reset_index()
        JENet = JENet[(JENet['NetJETotal'] != 0) & (JENet['NetJECount'] != 1)]
        selection = dataframe_with_selections(JENet)
    with col2:
        st.write("Your selection:")
        union_df = pd.merge(selection, df_, on='Clean Memo', how='inner')
        union_df = union_df.reset_index(inplace=False, drop=False)
        altrows = union_df['index'].iloc[1::2]
        union_df = union_df.drop(columns=['index'])
        union_df = union_df.style.format('${:.2f}', subset=['Amount'])
        union_df = union_df.set_properties(subset = pd.IndexSlice[altrows, :], **{'background-color': '#E3EFF8'})
        st.dataframe(union_df, hide_index=True, column_order=DepositFullColumns(), width=800)
        if df_sales_ is not None:
            st.write('From Sales Data:')
            salesunion_df = pd.merge(selection, df_sales_, on='Clean Memo', how='inner')
            salesunion_df = salesunion_df.reset_index(inplace=False, drop=False)
            altrowssales = salesunion_df['index'].iloc[1::2]
            salesunion_df = salesunion_df.drop(columns=['index'])
            salesunion_df = salesunion_df.style.format('${:.2f}', subset=['Amount'])
            salesunion_df = salesunion_df.set_properties(subset = pd.IndexSlice[altrowssales, :], **{'background-color': '#E3EFF8'})
            st.dataframe(salesunion_df, hide_index=True, column_order=DepositFullColumns(), width=800)


def show_singleJE(df_):
    JESingle = df_.copy()
    JESingle['Inv_Count'] = JESingle.groupby('Extr Num')['Extr Num'].transform('count')
    JESingle = JESingle[(JESingle['Inv_Count'] == 1) & ((JESingle['Amount'].abs() == 500) | (JESingle['Amount'].abs() == 1000))]
    JESingle['Event Date'] = JESingle['Description'].str.extract(r'(\d{2}/\d{2}/\d{4})')
    JESingle['Event Date'] = pd.to_datetime(JESingle['Event Date'], errors='coerce')
    JESingle = JESingle[JESingle['Trans Date'] > JESingle['Event Date']]
    st.dataframe(JESingle, column_order=DepositFullColumns())


def show_singleJE_other(df_):
    JESingle = df_.copy()
    JESingle['Inv_Count'] = JESingle.groupby('Extr Num')['Extr Num'].transform('count')
    
    st.dataframe(JESingle[(JESingle['Inv_Count'] == 1) & ((JESingle['Amount'].abs() != 500) & (JESingle['Amount'].abs() != 1000))], column_order=DepositFullColumns())


def show_firstJEdeposit(df_):
    filtered_df = df_[df_['Extr Num'].notna()]
    filtered_df['matches'] = filtered_df['Clean Memo']+'-'+filtered_df['Trans Date']
    filtered_df = filtered_df.drop_duplicates(subset='matches', keep=False)
    filtered_df = filtered_df.sort_values(by='Transaction date')
    first_rows = filtered_df.drop_duplicates(subset='Clean Memo', keep='first')
    st.dataframe(first_rows[first_rows['Amount'] < 0],
                 column_order=['Transaction date', 'Description', 'Amount'], width=800)


def run():
    # with st.container(height=650):
    if 'tipdata' not in st.session_state:
        st.session_state['tipdata'] = servertipdata()
    col1, col2 = st.columns([8, 2])
    with col1:
        st.header(st.session_state['company'])
    with col2:
        st.caption('')
    salesloadedfile = None
    depositloadedfile = None
    dfsales = None
    salesfiles = st.file_uploader('Upload Sales Audit File', type=['csv', 'xlsx'], accept_multiple_files=False, key='salesfileuploader')
    depositfiles = st.file_uploader('Upload Deposit Audit File', type=['csv', 'xlsx'], accept_multiple_files=False, key='depositfileuploader')
    if salesfiles is not None:
        salesloadedfile = salesloadfile(salesfiles)
    if depositfiles is not None:
        depositloadedfile = depositloadfile(depositfiles)
    with st.expander(label='Sales Data Audit'):
        if salesloadedfile is not None:
            st.markdown('---')
            st.markdown('### Sales Data Audit')
            #df = st.session_state['tipdata']['df_audit_sales'].copy()
            # Original
            # st.dataframe(df)
            dfsales = addMonthName(salesloadedfile)
            dfsales = adjustMemo(dfsales)
            dfsales = addFromTo(dfsales)
            # Modified
            dft = dfsales.reset_index(inplace=False, drop=False)
            altrows = dft['index'].iloc[1::2]
            dft = dft.drop(columns=['index'])
            dft = dft.style.format('${:.2f}', subset=['Amount'])
            dft = dft.set_properties(subset = pd.IndexSlice[altrows, :], **{'background-color': '#E3EFF8'})
            st.dataframe(dft,hide_index=True)
            st.markdown('### Sales Net non Zero')
            show_groupNetJE(dfsales)
            col1, cola, col2 = st.columns([6,0.1,6])
            with col1:
                st.markdown('### Sales JE Correct')
                show_MonthMatchesAmount(dfsales)
            with col2:
                st.markdown('### Sales First Deposits (Negative)')
                show_firstJE(dfsales)
            # Publish needs to be at the end to allow for updates read in-line. st.empty container saves the space
            # if st.session_state['updatedsomething']:
            #     if publishbutton.button('Publish Data', key='fromaudit1'):
            #         publish()
        else:
            st.markdown('---')
            st.markdown('You must first upload Sales Audit data')
            st.markdown('''
                        ### Instructions: 
                        #### Import Files:  
                        **from Quickbooks Online** 
                        1. View the balance sheet > sales liability account > choose date range
                        2. Export as excel (xlsx)
                        3. Clean data to show only headers and transactions
        
                        #### Reminders:
                        - None at the moment
                        ''')
    with st.expander(label='Deposit Data Audit'):
        if depositloadedfile is not None:
            st.markdown('---')
            st.markdown('### Deposit Data Audit')
            #df = st.session_state['tipdata']['df_audit_deposit'].copy()
            # Original
            # st.dataframe(df)
            dfdeposit = addMonthName(depositloadedfile)
            dfdeposit = adjustMemo(dfdeposit)
            # Modified
            st.dataframe(dfdeposit)
            st.markdown('### Deposit Net non Zero')
            st.caption('To research-head to QBO > Liability Account > Customize > Filter by Description > Change filter to look at both liability accounts. Reference Square as needed.')
            show_groupNetJEdeposit(dfdeposit, dfsales)

            col1, col2 = st.columns([1, 1])
            with col1:
                st.markdown('### Single Deposits (\$500/\$1,000)')
                st.caption('Transaction date in description needs to be on or before transaction date in order to be an actual error.')
                # dfdeposit['Event Date'] = pd.to_datetime(dfdeposit['Description'], errors='coerce', infer_datetime_format=True)
                # Extract dates in YYYY-MM-DD format
                show_singleJE(dfdeposit)
            with col2:
                st.markdown('### Single Deposits (other amount)')
                show_singleJE_other(dfdeposit)
            st.markdown('### Deposit First Entry (Negative)')
            show_firstJEdeposit(dfdeposit)
            
            # Publish needs to be at the end to allow for updates read in-line. st.empty container saves the space
            # if st.session_state['updatedsomething']:
            #     if publishbutton.button('Publish Data', key='fromaudit1'):
            #         publish()
        else:
            st.write('You must first upload Deposit Audit data')
            st.markdown('---')
            st.markdown('''
                        ### Instructions: 
                        #### Import Files:  
                        **from Quickbooks Online** 
                        1. View the balance sheet > deposit liability account > choose date range
                        2. Export as excel (xlsx)
                        3. Clean data to show only headers and transactions
        
                        #### Reminders:
                        - Resolve each of the four steps, one at a time
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
        # st.session_state['tipdata'] = {}
        st.session_state['tipdata'] = servertipdata()
    run()
    menu_with_redirect()
