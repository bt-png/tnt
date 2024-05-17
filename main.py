import streamlit as st

def run():
    st.write('Hello')
    with st.container():
        val = st.file_uploader('Upload CSV', type='csv', accept_multiple_files=False)
        if val is not None:
            st.write(val)

if __name__ == '__main__':
    run()