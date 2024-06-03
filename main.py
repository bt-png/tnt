import streamlit as st

import _process
import _gitfiles
import _pickle


def run():
    st.set_page_config(
        page_title='TNT Consulting',
        layout='wide'
    )
    st.write('Hello')
    with st.container():
        col1, col2 = st.columns([9,1])
        val = col1.file_uploader('Upload CSV', type={'csv'}, accept_multiple_files=False)
        if val is not None:
            col2.header('')
            col2.header('')
            if col2.button('Save'):
                bitfile = val.getvalue()
                _gitfiles.commit(
                    filename='current_input.csv',
                    message='api commit',
                    content=bitfile
                )
            st.markdown('---')
            df_tips, df_tips_adjusted = _process.run(val)

if __name__ == '__main__':
    run()
