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
            data = _process.run(val)
            with st.expander(label='Final Data', expanded=False):
                st.write(data)

if __name__ == '__main__':
    run()