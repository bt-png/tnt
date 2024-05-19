import streamlit as st

import _process

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
            with st.expander(label='Final Data', expanded=False):
                st.caption('Default Positions')
                st.dataframe(df_tips)
                st.markdown('---')
                st.caption('Revised Positions')
                st.dataframe(df_tips_adjusted)

if __name__ == '__main__':
    run()