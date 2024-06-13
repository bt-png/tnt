import streamlit as st

import _process
import _gitfiles


def run():
    st.set_page_config(
        page_title='TNT Consulting',
        layout='wide'
    )
    st.write('Hello')
    with st.container():
        choice = st.selectbox(label='Upload a new file, or continue from a save?', options=['Upload', 'Continue'], placeholder='Select...', index=1)
        col1, col2 = st.columns([9,1])
        if choice == 'Upload':
            val = col1.file_uploader('Upload CSV', type={'csv'}, accept_multiple_files=False)
            if val is not None:
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
