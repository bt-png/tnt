import streamlit as st
import pandas as pd
import numpy as np

def read_csv(file_path: str) -> pd.DataFrame:
    _df = pd.read_csv(file_path)
    return _df


def _clean_import(_df: pd.DataFrame) -> pd.DataFrame:
    df = _df.copy()
    df['Paid Total'] = df['Paid Total'].str.replace('$','',regex=False)
    df['Paid Total'] = df['Paid Total'].astype(float)
    df['Paid Total'] = df['Paid Total'].replace(np.nan, 0)
    return df


def _combine_FullName(_df: pd.DataFrame) -> pd.DataFrame:
    df = _df.copy()
    cols = ['First Name', 'Last Name']
    df['Full Name'] = df[cols].apply(lambda row: ' '.join(row.values.astype(str)), axis=1)
    return df


def _aggregate(_df: pd.DataFrame, cols) -> pd.DataFrame:
    df = _df[['Full Name', 'Position', 'Regular', 'Paid Total']].copy()
    ##uniqueNames = df['Full Name'].unique()
    #print(uniqueNames)
    df = df.groupby(['Full Name', 'Position']).agg({
        'Regular': sum,
        'Paid Total': sum,
        })
    return df

def _tipelligibility(df):
    st.write("Employee's")
    col20, col21, col22, col23 = st.columns([1,.1,1,.1])
    user_not_tipped = col20.multiselect(
                "Employee's with job classification not elligible for tips",
                df['Full Name'].unique()  # ,
                # default=('')
            )
    df_tipElligible = df[~df['Full Name'].isin(user_not_tipped)]
    df_tipInElligible = df[df['Full Name'].isin(user_not_tipped)]
    col22.caption('Tip Elligible Employees')
    with col22:
        _str = ' | '
        for names in df_tipElligible['Full Name'].unique():
            _str += names + ' | '
        st.write(_str)
    return df_tipElligible, df_tipInElligible

def _tip_pools(_df):
    df = pd.DataFrame({'Position': _df['Position'].dropna().unique()})
    df.insert(0, 'Tip Pool', '')
    #df['Tip Pool'].apply()
    st.write("Positions")
    col30, col31, col32, col33, col34 = st.columns([1,.1,1,.1,1])
    df_tip = col30.data_editor(
        df,
        hide_index=True,
        column_config={
            'Tip Pool': st.column_config.SelectboxColumn(
                help='The tip category associated with Position',
                width='medium',
                options=['Front of House','Back of House']
                ),
            'Position': st.column_config.TextColumn(
                width='medium'
                )
            },
        )
    front_tip_pool = df_tip[df_tip['Tip Pool'] == 'Front of House']['Position'].values
    back_tip_pool = df_tip[df_tip['Tip Pool'] == 'Back of House']['Position'].values
    with col32:
        st.caption('Front of House Positions')
        _str = ' | '
        for pos in front_tip_pool:
            _str += pos + ' | '
        st.write(_str)
    with col34:
        st.caption('Back of House Positions')
        _str = ' | '
        for pos in back_tip_pool:
            _str += pos + ' | '
        st.write(_str)
    return front_tip_pool, back_tip_pool
    

def _setup_tipping_pools(_df: pd.DataFrame) -> pd.DataFrame:
    st.markdown('---')
    with st.expander('Tipping Rules'):
        col1, col2, col3 = st.columns([.1,.85,.05])
        col1.subheader('Tipping Elligibility')
        with col2:
            df_tipElligible, df_tipInElligible = _tipelligibility(_df)
            st.markdown('---')
            front_tip_pool, back_tip_pool = _tip_pools(df_tipElligible)
    return df_tipElligible, front_tip_pool, back_tip_pool

def _tip_amounts(ukey):
    col40, col41 = st.columns([1,1])
    tippingPool_Garden = col40.number_input('Garden Pool ($)', value=0.00, format='%f', key=ukey+'1')
    tippingPool_Reg = col41.number_input('Regular Pool ($)', value=0.00, format='%f', key=ukey+'2')
    return tippingPool_Garden, tippingPool_Reg

def _tip_percents(ukey):
    col40, col41 = st.columns([1,1])
    garden_split = col40.slider(label='Front/Back Split', min_value=0, max_value=100, step=1, value=70, key=ukey+'garden_split')
    reg_split = col41.slider(label='Front/Back Split', min_value=0, max_value=100, step=1, value=60, key=ukey+'reg_split')
    return garden_split, reg_split

def _hrs_split(_df, _g, _fr, _bk):
    garden = _df[_df['Position'].isin(_g)]
    garden_front = garden[garden['Position'].isin(_fr)]
    garden_back = garden[garden['Position'].isin(_bk)]
    regular = _df[~_df['Position'].isin(_g)]
    regular_front = regular[regular['Position'].isin(_fr)]
    regular_back = regular[regular['Position'].isin(_bk)]
    return garden_front, garden_back, regular_front, regular_back


def _tip_info(house, pool, split, _df_hrs):
    total = pool*(split/100)
    if len(_df_hrs.index) == 0:
        str = 'No Entries'
        hrs=0
        rate=0
    else:
        hrs = _df_hrs['Regular'].sum()
        rate = pool*(split/100)/hrs if hrs != 0 else 0
        str = f'''{house} of house:  
                * Percent Split = {split}%  
                * Sub Tip Pool = \${round(total,2)}  
                * Sub Hours Worked = {round(hrs,2)}  
                * Sub Tip Rate = \${round(rate,2)}/hr  
                '''
    if hrs==0 and total != 0:
        st.warning(str)
    elif hrs!=0 and total ==0:
        st.warning(str)
    else:
        st.info(str)
    _df_hrs['Tip Rate'] = rate
    _df_hrs['Tip Total'] = _df_hrs['Tip Rate'] * _df_hrs['Regular']
    _df_hrs['Total + Tip'] = _df_hrs['Tip Total'] + _df_hrs['Paid Total']  # _df_hrs[['Tip Total','Paid Total']].sum(axis=1)


def _display_tips(_df_tips):
    col1, col2 = st.columns([1,1])
    col1.caption('Grouped by Position')
    _df_tips_pos = _df_tips.groupby(['Full Name', 'Position']).agg({
        'Regular': sum,
        'Tip Total': sum,
        'Paid Total': sum,
        'Total + Tip': sum
        })
    _df_tips_pos['Regular'] = _df_tips_pos['Regular'].apply(lambda x: "{:.2f} hrs".format(x))
    _df_tips_pos['Paid Total'] = _df_tips_pos['Paid Total'].apply(lambda x: "${:.2f}".format(x))
    _df_tips_pos['Tip Total'] = _df_tips_pos['Tip Total'].apply(lambda x: "${:.2f}".format(x))
    _df_tips_pos['Total + Tip'] = _df_tips_pos['Total + Tip'].apply(lambda x: "${:.2f}".format(x))
    col1.dataframe(_df_tips_pos)
    col2.caption('Payroll')
    _df_tips_f = _df_tips.groupby(['Full Name']).agg({
        'Regular': sum,
        'Tip Total': sum,
        'Paid Total': sum,
        'Total + Tip': sum
        })
    _df_tips_f['Regular'] = _df_tips_f['Regular'].apply(lambda x: "{:.2f} hrs".format(x))
    _df_tips_f['Paid Total'] = _df_tips_f['Paid Total'].apply(lambda x: "${:.2f}".format(x))
    _df_tips_f['Tip Total'] = _df_tips_f['Tip Total'].apply(lambda x: "${:.2f}".format(x))
    _df_tips_f['Total + Tip'] = _df_tips_f['Total + Tip'].apply(lambda x: "${:.2f}".format(x))
    col2.dataframe(_df_tips_f)

def _display_changes(_df_tips, _df_tips_adjusted):
    _df_tips_f = _df_tips.groupby(['Full Name']).agg({
        'Regular': sum,
        'Tip Total': sum,
        'Paid Total': sum,
        'Total + Tip': sum
        })
    _df_tips_adjusted_f = _df_tips_adjusted.groupby(['Full Name']).agg({
        'Regular': sum,
        'Tip Total': sum,
        'Paid Total': sum,
        'Total + Tip': sum
        })
    _df_diff = _df_tips_adjusted_f-_df_tips_f
    _df_diff = _df_diff.loc[(_df_diff!=0).any(axis=1)]
    _df_diff['Regular'] = _df_diff['Regular'].apply(lambda x: "{:.2f} hrs".format(x))
    _df_diff['Paid Total'] = _df_diff['Paid Total'].apply(lambda x: "${:.2f}".format(x))
    _df_diff['Tip Total'] = _df_diff['Tip Total'].apply(lambda x: "${:.2f}".format(x))
    _df_diff['Total + Tip'] = _df_diff['Total + Tip'].apply(lambda x: "${:.2f}".format(x))
    st.dataframe(_df_diff)
    

def _tipping_pools(df_tipElligible, front_tip_pool, back_tip_pool) -> pd.DataFrame:
    with st.expander('Tipping Pool', expanded=True):
        col1, col2, col3 = st.columns([.1,.85,.05])
        col1.subheader('Pay Cycle Tipping Pool')
        with col2:
            user_garden_input = st.multiselect(  # Remove this filter from this section. Will choose positions front/back above
                        '"Garden" Positions',  # Update to a date selector to include in the GARDEN EVENTS pool
                        df_tipElligible['Position'].unique(),
                        default=('Host', 'Garden Server')
                    )
            st.markdown('---')
            tippingPool_Garden, tippingPool_Reg = _tip_amounts('first')
            garden_split, reg_split = _tip_percents('first')
            _hrs_gf, _hrs_gb, _hrs_rf, _hrs_rb = _hrs_split(df_tipElligible, user_garden_input, front_tip_pool, back_tip_pool)
            col40, col41, col42, col43 = st.columns([1,1,1,1])
            with col40: _tip_info('Front', tippingPool_Garden, garden_split, _hrs_gf)
            with col41: _tip_info('Back', tippingPool_Garden, (100-garden_split), _hrs_gb)
            with col42: _tip_info('Front', tippingPool_Reg, reg_split, _hrs_rf)
            with col43: _tip_info('Back', tippingPool_Reg, (100-reg_split), _hrs_rb)
            st.markdown('---')
            _df_tips = pd.concat([_hrs_gf, _hrs_gb, _hrs_rf, _hrs_rb], ignore_index=True)
            _display_tips(_df_tips)
        return _df_tips, tippingPool_Garden, tippingPool_Reg, garden_split, reg_split, user_garden_input


def _adjust_work_pos(_df):
    df_revised = _df.copy()
    st.write("Revise Hours worked under Position")
    df = pd.DataFrame(columns=['name', 'hrs', 'from', 'to', 'reason'])
    employees = _df['Full Name'].dropna().unique()
    positions = _df['Position'].dropna().unique()
    config = {
        'name': st.column_config.SelectboxColumn('Full Name', width='medium', required=True, options=employees),
        'hrs': st.column_config.NumberColumn('Take (hrs)', required=True, width='medium'),
        'from': st.column_config.SelectboxColumn('From Old Position', width='medium', options=positions, required=True),
        'to': st.column_config.SelectboxColumn('Move to New Position', width='medium', options=positions, required=True),
        'reason': st.column_config.TextColumn('For the Reason', width='large', required=True),
    }
    result = st.data_editor(df, column_config=config, num_rows='dynamic', hide_index=True)

    df_revised['reason'] = ''
    df_add = pd.DataFrame({'Full Name': result['name'], 'Regular': result['hrs'], 'Position': result['to'], 'reason': result['reason']})
    df_remove = pd.DataFrame({'Full Name': result['name'], 'Regular': -result['hrs'], 'Position': result['from'], 'reason': result['reason']})
    df_revised = pd.concat([df_revised, df_add, df_remove], ignore_index=True)

    st.write('Original')
    st.dataframe(_df)
    st.write('Changes')
    st.dataframe(result)
    st.write('Final')
    st.dataframe(df_revised)
    return df_revised


def _adjust_tipping_pools(_df_tips, tippingPool_Garden, tippingPool_Reg, user_garden_input,
                          df_tipElligible, front_tip_pool, back_tip_pool) -> pd.DataFrame:
    
    with st.expander('Adjust Tipping Pool', expanded=True):
        col1, col2, col3 = st.columns([.1,.85,.05])
        col1.subheader('Work Position Corrections')
        with col2:
            df_tipElligible_adjusted = _adjust_work_pos(df_tipElligible)

            #df_tipElligible_adjusted = df_tipElligible.copy()
            st.markdown('---')
            garden_split, reg_split = _tip_percents('adjust')
            _hrs_gf, _hrs_gb, _hrs_rf, _hrs_rb = _hrs_split(df_tipElligible_adjusted, user_garden_input, front_tip_pool, back_tip_pool)
            col40, col41, col42, col43 = st.columns([1,1,1,1])
            with col40: _tip_info('Front', tippingPool_Garden, garden_split, _hrs_gf)
            with col41: _tip_info('Back', tippingPool_Garden, (100-garden_split), _hrs_gb)
            with col42: _tip_info('Front', tippingPool_Reg, reg_split, _hrs_rf)
            with col43: _tip_info('Back', tippingPool_Reg, (100-reg_split), _hrs_rb)
            st.markdown('---')
            _df_tips_adjusted = pd.concat([_hrs_gf, _hrs_gb, _hrs_rf, _hrs_rb], ignore_index=True)
            _display_changes(_df_tips, _df_tips_adjusted)
            st.markdown('---')
            _display_tips(_df_tips_adjusted)
    return _df_tips_adjusted, df_tipElligible_adjusted


def filter_dataframe(_df: pd.DataFrame) -> pd.DataFrame:
    with st.expander(label='Original Data', expanded=False):
        df = _df.copy()
        with st.container():
            to_filter_columns = ['Full Name']  # st.multiselect("Filter dataframe on", df.columns)  # ('Full Name', 'Position') #   # 
            for column in to_filter_columns:
                user_cat_input = st.multiselect(
                    f"Values for {column}",
                    df[column].unique() #,
                    #default=()# list(df[column].unique())
                )
                if len(user_cat_input) > 0:
                    df = df[df[column].isin(user_cat_input)]
        st.write(df)
    return df


def run(file_path: str) -> pd.DataFrame:
    _df = read_csv(file_path)
    _df = _clean_import(_df)
    _df = _combine_FullName(_df)
    st.write('step1')
    filter_dataframe(_df)
    st.write('step2')
    df_tipElligible, front_tip_pool, back_tip_pool = _setup_tipping_pools(_df)
    st.write('step3')
    _df_tips, tippingPool_Garden, tippingPool_Reg, garden_split, reg_split, user_garden_input = _tipping_pools(df_tipElligible, front_tip_pool, back_tip_pool)
    st.write('step4')
    _df_tips_adjusted, df_tipElligible_adjusted = _adjust_tipping_pools(_df_tips, tippingPool_Garden, tippingPool_Reg, user_garden_input,
                          df_tipElligible, front_tip_pool, back_tip_pool)
    
    return _df_tips
