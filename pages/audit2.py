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


def FullColumns():
    return ['Transaction date', 'Memo/Description', 'Amount']


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


def loadfile(files):
    try:
        dataframe = pd.read_csv(files)
    except Exception:
        dataframe = pd.read_excel(files)
    if 'Deposits' in dataframe[dataframe.columns[0]][4]:
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
    else:
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
    return df_


def adjustMemo(df_):
    df_['Clean Memo'] = df_['Memo/Description'].astype(str).str.strip()
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
        JENet = JENet[(JENet['NetJETotal'] != 0) & (JENet['NetJECount'] != 1)]
        selection = dataframe_with_selections(JENet)
    with col2:
        st.write("Your selection:")
        union_df = pd.merge(selection, df_, on='Clean Memo', how='inner')
        st.dataframe(union_df, column_order=FullColumns(), width=1200)


def show_singleJE(df_):
    JESingle = df_.copy()
    JESingle['Inv_Count'] = JESingle.groupby('Extr Num')['Extr Num'].transform('count')
    
    st.dataframe(JESingle[(JESingle['Inv_Count'] == 1) & ((JESingle['Amount'].abs() == 500) | (JESingle['Amount'].abs() == 1000))], column_order=FullColumns())


def show_singleJE_other(df_):
    JESingle = df_.copy()
    JESingle['Inv_Count'] = JESingle.groupby('Extr Num')['Extr Num'].transform('count')
    
    st.dataframe(JESingle[(JESingle['Inv_Count'] == 1) & ((JESingle['Amount'].abs() != 500) & (JESingle['Amount'].abs() != 1000))], column_order=FullColumns())


def show_firstJE(df_):
    filtered_df = df_[df_['Extr Num'].notna()]
    first_rows = filtered_df.drop_duplicates(subset='Clean Memo', keep='first')
    
    st.dataframe(first_rows[first_rows['Amount'] < 0],
                 column_order=['Transaction date', 'Memo/Description', 'Amount'], width=800)


# Invoice numbers can be string of 4 consecutive numbers (1806 or #001806 both should resolve to 1806)

# Errors if:
# Invoice # can't be extracted
# Sum of Amount's from Invoice Numbers does not net zero
# Initial transaction date is -$
# Count of invoice #s != 2


# Errors if:   

def run():
    # with st.container(height=650):
    if 'tipdata' not in st.session_state:
        st.session_state['tipdata'] = servertipdata()
    col1, col2 = st.columns([8, 2])
    with col1:
        st.header(st.session_state['company'])
    with col2:
        st.caption('')
    loadedfile = None
    files = st.file_uploader('Upload Deposit Audit File', type=['csv', 'xlsx'], accept_multiple_files=False, key='fileuploader')
    if files is not None:
        loadedfile = loadfile(files)
    if loadedfile is not None:
        st.markdown('---')
        st.markdown('### Deposit Data Audit')
        #df = st.session_state['tipdata']['df_audit_deposit'].copy()
        # Original
        # st.dataframe(df)
        df = addMonthName(loadedfile)
        df = adjustMemo(df)
        # Modified
        st.dataframe(df)
        st.markdown('### Net non Zero')
        show_groupNetJE(df)

        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown('### Single Deposits (\$500/\$1,000)')
            show_singleJE(df)
        with col2:
            st.markdown('### Single Deposits (other amount)')
            show_singleJE_other(df)
        st.markdown('### First Entry (Negative)')
        show_firstJE(df)
        
        # Publish needs to be at the end to allow for updates read in-line. st.empty container saves the space
        # if st.session_state['updatedsomething']:
        #     if publishbutton.button('Publish Data', key='fromaudit1'):
        #         publish()
    else:
        st.write('You must first upload Deposit Audit data')


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
