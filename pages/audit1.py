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
    if 'Sales' in dataframe[dataframe.columns[0]][4]:
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


def addFromTo(df_):
    df_['FROM'] = \
        df_['Memo/Description'].astype(str).str.split('for', n=1, expand=True)[0].str.strip()
    df_['FROM'] = \
        df_['FROM'].astype(str).str.split(' ', n=1, expand=True)[0].str.strip()
    df_['TO'] = \
            df_['Memo/Description'].astype(str).str.split('for', n=1, expand=True)[1].str.strip()
    df_['TO'] = \
        df_['TO'].astype(str).str.split(' ', n=1, expand=True)[0].str.strip()
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
        JENet = JENet[JENet['NetJETotal'] != 0]
        selection = dataframe_with_selections(JENet)
    with col2:
        st.write("Your selection:")
        union_df = pd.merge(selection, df_, on='Clean Memo', how='inner')
        st.dataframe(union_df, column_order=FullColumns(), width=1200)


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
    files = st.file_uploader('Upload Sales Audit File', type=['csv', 'xlsx'], accept_multiple_files=False, key='fileuploader')
    if files is not None:
        loadedfile = loadfile(files)
    if loadedfile is not None:
        st.markdown('---')
        st.markdown('### Sales Data Audit')
        df = st.session_state['tipdata']['df_audit_sales'].copy()
        # Original
        # st.dataframe(df)
        df = addMonthName(loadedfile)
        df = adjustMemo(df)
        df = addFromTo(df)
        # Modified
        st.dataframe(df)
        st.markdown('### Net non Zero')
        show_groupNetJE(df)
        col1, cola, col2 = st.columns([6,0.1,6])
        with col1:
            st.markdown('### JE Correct')
            show_MonthMatchesAmount(df)
        with col2:
            st.markdown('### First Deposits (Negative)')
            show_firstJE(df)
        # Publish needs to be at the end to allow for updates read in-line. st.empty container saves the space
        # if st.session_state['updatedsomething']:
        #     if publishbutton.button('Publish Data', key='fromaudit1'):
        #         publish()
    else:
        st.write('You must first upload and publish Sales Audit data')


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
