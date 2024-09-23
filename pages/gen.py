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
    _df.loc[_df[_df['Locker'] == locker_num].index, 'Current'] += 1


def input_locker():
    return st.text_input('Locker Number')


def load_df():
    df = pd.DataFrame({
        'Locker': [12, 13, 14, 15],
        'Current': [1, 2, 1, 3],
        'Combinations': [[0,1,2,3,4], [0,1,2,3,4], [0,1,2,3,4], [0,1,2,3,4]],
        'Assigned': ['', '', '', ''],
        'Comments': ['', '', '', '']
    })
    return df


if __name__ == '__main__':
    df = load_df()
    locker = input_locker()
    if locker != '' and locker.isnumeric:
        locker = int(locker)
        if locker in df['Locker'].to_list():
            show_combination(locker, df)
            if st.button("That didn't work"):
                next_combination(locker, df)
        else:
            st.write('Locker number is not assigned')
        st.dataframe(df)

