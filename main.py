import streamlit as st
import json
import _process
import _gitfiles
import pandas as pd
import numpy as np
from io import StringIO
Deployed = False

dfs = ['df_sales', 'df_schedule', 'df_work_hours']


def clear_save_data():
    st.session_state['newdict'] = {}
    bitfile = json.dumps(st.session_state['newdict'])
    if Deployed:
        # Delete existing save data
        _gitfiles.commit(
            filename='current_save.csv',
            message='reset new csv',
            content=bitfile
        )
    else:
        # Save locally during testing
        try:
            with open('current_save.csv', 'w') as file:
                file.write(bitfile)
            st.success('Save Data Has been Saved')
        except Exception:
            st.warning('Something went wrong')


def save_csv():
    df = st.session_state['df_work_hours']
    bitfile = df.to_csv()
    #st.write(bitfile)
    if Deployed:
        _gitfiles.commit(
            filename='current_input.csv',
            message='api commit',
            content=bitfile
        )
    else:
        # Save locally during testing
        try:
            with open('current_input.csv', 'w') as file:
                file.write(bitfile)
            st.success('Work Hours CSV has been Saved')
        except Exception:
            st.warning('Something went wrong')


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
            st.session_state['df_sales'] = dataframe.copy()
        elif 'Schedule' == dataframe.columns[0]:
            #dataframe = dataframe.set_index('First Name').transpose()
            st.session_state['df_schedule'] = dataframe.copy()
        elif 'First Name' == dataframe.columns[0]:
            #st.session_state['val'] = file
            st.session_state['df_work_hours'] = dataframe.copy()
            

def writeSessionStateDataFrames():
    for df in dfs:
        st.write(f'Loaded data for {df}')
        st.write(st.session_state[df])


def allDataFramesLoaded():
    col1, col2 = st.columns([9,1])
    checkSum=0
    for df in dfs:
        if st.session_state[df] is not None:
            if df == 'df_sales':
                loadTotalTips()
            if df == 'df_work_hours':
                save_csv()
                #col1.write(f'Data has been loaded for {df}. You may continue to upload more so the' \
                #    'Garden pool and chef work shifts can be read in, or you may continue and enter manually.')
                #if col1.button('Continue without loading more documents.'):
                #    st.session_state['Continue'] = True
                    #_process.continue_run(st.session_state['df_work_hours'])
            if df == 'df_schedule':
                st.dataframe(st.session_state[df])
            checkSum += 1
        else:
            col1.warning(f'Data has not been loaded for {df}')
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
    if 'Continue' not in st.session_state:
        st.session_state['Continue'] = False
    choice = st.selectbox(label='Upload new files, or continue from a save?', options=['Upload', 'Continue'], placeholder='Select...', index=1)
    st.write('Hello')
    with st.container():
        col1, col2 = st.columns([9,1])
        if choice == 'Upload':
            if col2.button('Clear Save Data'):
                clear_save_data()
            st.session_state['Continue'] = False
            val = None #col1.file_uploader('Upload CSV', type={'csv'}, accept_multiple_files=False)
            files = col1.file_uploader('Upload Files', type=['csv', 'xlsx'], accept_multiple_files=True)
            if files is not None:
                loadFilestoSessionState(files)
                if allDataFramesLoaded():
                    st.session_state['Continue'] = True
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
            if st.session_state['Continue']:
                pass
            else:
                st.session_state['Continue'] = True
                st.rerun()
        else:
            st.warning('Please make a choice')
    if st.session_state['Continue']:
        val = 'current_input.csv'
        st.markdown('---')
        df_tips = _process.run(val)

if __name__ == '__main__':
    run()
