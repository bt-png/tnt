import streamlit as st
import pandas as pd


def active_combination(locker_num, _df):
    return _df.loc[_df['Locker'] == locker_num]['Current'].values[0]


def show_combination(locker_num, _df):
    combinations = _df.loc[_df['Locker'] == locker_num]['Combinations'].values[0]
    active = active_combination(locker_num, _df)
    st.write('Your locker combo may be:')
    st.text(combinations[active])


def next_combination(locker_num, _df):
    # st.text(_df.loc[_df[_df['Locker'] == locker_num].index, 'Current'][0])
    if _df.loc[_df[_df['Locker'] == locker_num].index, 'Current'][0] == 4:
        _df.loc[_df[_df['Locker'] == locker_num].index, 'Current'] = 0
    else:
        _df.loc[_df[_df['Locker'] == locker_num].index, 'Current'] += 1


def input_locker():
    return st.text_input('Locker Number')


def load_df():
    df = pd.DataFrame({
        'Locker': [12, 13, 14, 15],
        'Current': [1, 2, 1, 3],
        'Combinations': [['0-15-36','1-12-34','2-32-31','3-5-12','4-2-12'], [0,1,2,3,4], [0,1,2,3,4], [0,1,2,3,4]],
        'Assigned': ['Tharp', '', '', ''],
        'Comments': ['', '', '', '']
    })
    return df


if __name__ == '__main__':
    if 'df' not in st.session_state:
        st.session_state.df = load_df()
    df = st.session_state.df
    family = st.text_input('Family Name')
    locker = st.text_input('Locker Number')
    if locker != '' and locker.isnumeric:
        locker = int(locker)
        if locker in df['Locker'].to_list():
            row = df[df['Locker'] == locker]
            # st.write(row)
            if (row['Assigned'] == family).all():
                show_combination(locker, df)
                if st.button("That didn't work"):
                    next_combination(locker, df)
                    
        else:
            st.write('Locker number is not assigned')
        #st.dataframe(df)

