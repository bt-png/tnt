import streamlit as st

import _process
import _pickle


def run():
    st.set_page_config(
        page_title='TNT Consulting',
        layout='wide'
    )
    st.write('Hello')
    with st.container():
        val = st.file_uploader('Upload CSV', type={'csv'}, accept_multiple_files=False)
        if val is not None:
            st.markdown('---')
            df_tips, df_tips_adjusted = _process.run(val)

if __name__ == '__main__':
    run()