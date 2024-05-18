import streamlit as st
import pandas as pd


def read_csv(file_path: str) -> pd.DataFrame:
    _df = pd.read_csv(file_path)
    return _df


def _clean_import(_df: pd.DataFrame) -> pd.DataFrame:
    df = _df.copy()
    df['Paid Total'] = df['Paid Total'].str.replace('$','',regex=False)
    df['Paid Total'] = df['Paid Total'].astype(float)
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


def _tip_percents():
    col40, col41 = st.columns([1,1])
    tippingPool_Garden = col40.number_input('Garden Pool ($)', value=0.00, format='%f')
    tippingPool_Reg = col41.number_input('Regular Pool ($)', value=0.00, format='%f')
    garden_split = col40.slider(label='Front/Back Split', min_value=0, max_value=100, step=1, value=70, key='garden_split')
    reg_split = col41.slider(label='Front/Back Split', min_value=0, max_value=100, step=1, value=60, key='reg_split')
    return tippingPool_Garden, tippingPool_Reg, garden_split, reg_split

def _hrs_split(_df, _g, _fr, _bk):
    garden = _df[_df['Position'].isin(_g)]
    garden_front = garden[garden['Position'].isin(_fr)]
    garden_back = garden[garden['Position'].isin(_bk)]
    regular = _df[~_df['Position'].isin(_g)]
    regular_front = regular[regular['Position'].isin(_fr)]
    regular_back = regular[regular['Position'].isin(_bk)]
    return garden_front, garden_back, regular_front, regular_back


def _tip_info(house, pool, split, _df_hrs):
    hrs = _df_hrs['Regular'].sum()
    total = pool*(split/100)
    rate = pool*(split/100)/hrs
    if hrs==0 and total != 0:
        st.warning(
            f'''{house} of house:  
            * Percent Split = {split}%  
            * Sub Tip Pool = \${round(total,2)}  
            * Sub Hours Worked = {round(hrs,2)}  
            * Sub Tip Rate = \${round(rate,2)}/hr  
            '''
            )
    else:
        st.info(
            f'''{house} of house:  
            * Percent Split = {split}%  
            * Sub Tip Pool = \${round(total,2)}  
            * Sub Hours Worked = {round(hrs,2)}  
            * Sub Tip Rate = \${round(rate,2)}/hr  
            '''
            )
    _df_hrs['Tip Rate'] = rate
    _df_hrs['Tip Total'] = _df_hrs['Tip Rate'] * _df_hrs['Regular']
    _df_hrs['Total + Tip'] = _df_hrs['Tip Total'] + _df_hrs['Paid Total']  # _df_hrs[['Tip Total','Paid Total']].sum(axis=1)


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
            tippingPool_Garden, tippingPool_Reg, garden_split, reg_split = _tip_percents()
            _hrs_gf, _hrs_gb, _hrs_rf, _hrs_rb = _hrs_split(df_tipElligible, user_garden_input, front_tip_pool, back_tip_pool)
            col40, col41, col42, col43 = st.columns([1,1,1,1])
            with col40: _tip_info('Front', tippingPool_Garden, garden_split, _hrs_gf)
            with col41: _tip_info('Back', tippingPool_Garden, (100-garden_split), _hrs_gb)
            with col42: _tip_info('Front', tippingPool_Reg, reg_split, _hrs_rf)
            with col43: _tip_info('Back', tippingPool_Reg, (100-reg_split), _hrs_rb)
            st.markdown('---')
            col1, col2 = st.columns([1,1])
            _df_tips = pd.concat([_hrs_gf, _hrs_gb, _hrs_rf, _hrs_rb], ignore_index=True)
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
        return _df_tips


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
    df_tipp = _tipping_pools(df_tipElligible, front_tip_pool, back_tip_pool)
    st.write('step4')
    df_aggregate = _aggregate(_df, ['Full Name', 'Position'])
    st.dataframe(df_aggregate)
    return _df
