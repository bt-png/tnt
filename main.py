import streamlit as st
import json
import _process
import _gitfiles
import pandas as pd
import numpy as np
from io import StringIO


dfs = ['df_sales', 'df_schedule', 'df_work_hours']


def loadFilestoSessionState(files):
    for df in dfs:
        if df not in st.session_state:
            st.session_state[df] = None
    
    for file in files:
        try:
            dataframe = pd.read_csv(file)
        except:
            dataframe = pd.read_excel(file)
        if 'Sales' == dataframe.columns[0]:
            dataframe = dataframe.set_index('Sales').transpose()
            for col in dataframe.columns:
                dataframe[col] = dataframe[col].str.replace('$', '', regex=False)
                dataframe[col] = dataframe[col].str.replace(',', '', regex=False)
                dataframe[col] = dataframe[col].astype(float)
                dataframe[col] = dataframe[col].replace(np.nan, 0)
            #st.dataframe(dataframe)
            st.session_state['df_sales'] = dataframe.copy()
        elif 'Schedule' == dataframe.columns[0]:
            st.session_state['df_schedule'] = dataframe.copy()
        elif 'First Name' == dataframe.columns[0]:
            st.session_state['df_work_hours'] = dataframe.copy()


def writeSessionStateDataFrames():
    for df in dfs:
        st.write(f'Loaded data for {df}')
        st.write(st.session_state[df])


def allDataFramesLoaded():
    checkSum=0
    for df in dfs:
        if st.session_state[df] is not None:
            #if len(st.session_state[df]) > 0:
            checkSum += 1
        else:
            st.write(f'Data has not been loaded for {df}')
    if checkSum == len(dfs):
        return True
    return False


def loadTotalTips():
    df = st.session_state[dfs[0]]
    st.session_state['dict']['Total Pool'] = round(df['Tip'].sum(),2)
                                 

def run():
    st.set_page_config(
        page_title='TNT Consulting',
        layout='wide'
    )
    st.write('Hello')
    with st.container():
        choice = st.selectbox(label='Upload new files, or continue from a save?', options=['Upload', 'Continue'], placeholder='Select...', index=0)
        col1, col2 = st.columns([9,1])
        if choice == 'Upload':
            val = None #col1.file_uploader('Upload CSV', type={'csv'}, accept_multiple_files=False)
            files = col1.file_uploader('Upload Files', type=['csv', 'xlsx'], accept_multiple_files=True)
            if files is not None:
                loadFilestoSessionState(files)
                if allDataFramesLoaded():
                    loadTotalTips()
                    #st.success('All Files Received')
                    #writeSessionStateDataFrames()
                    _process.continue_run(st.session_state['df_work_hours'])
            if val is not None:
                # Delete existing save data
                newdict = {}
                bitfile = json.dumps(newdict)
                _gitfiles.commit(
                    filename='current_save.csv',
                    message='reset new csv',
                    content=bitfile
                )
                col2.header('')
                col2.header('')
                if col2.button('Save CSV'):
                    bitfile = val.getvalue()
                    _gitfiles.commit(
                        filename='current_input.csv',
                        message='api commit',
                        content=bitfile
                    )                       
        elif choice == 'Continue':
            val = 'current_input.csv'
        else:
            st.warning('Please make a choice')
        if val is not None:
            st.markdown('---')
            df_tips = _process.run(val)

if __name__ == '__main__':
    run()
