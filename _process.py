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


def payroll_summary(_df):
    keys = list(_all_positions().keys())
    df = _df.copy()
    df['Hours'] = df['Regular']
    df['Wage'] = df['Paid Total']
    df['Tip'] = df['Hours'] * df['Tip Rate']
    df['Wage + Tip'] = df['Wage'] + df['Tip']
    df['Garden Tips'] = [df[(df['Full Name'] == x) & (df['Tip Pool'].isin([keys[0], keys[1], keys[2]]))]['Tip'].sum() for x in df['Full Name']]
    df['Regular Tips'] = [df[(df['Full Name'] == x) & (df['Tip Pool'].isin([keys[3], keys[4]]))]['Tip'].sum() for x in df['Full Name']]
    df_agg = df.groupby(['Full Name', 'Garden Tips', 'Regular Tips']).agg({
        'Hours': sum,
        'Wage': sum,
        'Wage + Tip': sum
        })
    st.write(df_agg)
    return df


def _aggregate_name(_df: pd.DataFrame) -> pd.DataFrame:
    df = _df.copy()
    df['Tip Elligible Hours'] = df['Regular']
    df['Cash Wage'] = df['Paid Total']
    df = df.groupby(['Full Name']).agg({
        'Tip Elligible Hours': sum,
        'Tip Total': sum,
        'Cash Wage': sum,
        'Cash Wage plus Tip': sum
        })
    return df


def _aggregate_name_position(_df: pd.DataFrame) -> pd.DataFrame:
    df = _df.copy()
    df['Tip Elligible Hours'] = df['Regular']
    df['Cash Wage'] = df['Paid Total']
    df = df.groupby(['Full Name', 'Position']).agg({
        'Tip Elligible Hours': sum,
        'Tip Total': sum,
        'Cash Wage': sum,
        'Cash Wage plus Tip': sum
        })
    return df


def _format_aggregate(_df):
    _df['Tip Elligible Hours'] = _df['Tip Elligible Hours'].apply(lambda x: "{:.2f} hrs".format(x))
    _df['Cash Wage'] = _df['Cash Wage'].apply(lambda x: "${:.2f}".format(x))
    _df['Tip Total'] = _df['Tip Total'].apply(lambda x: "${:.2f}".format(x))
    _df['Cash Wage plus Tip'] = _df['Cash Wage plus Tip'].apply(lambda x: "${:.2f}".format(x))
    return _df


def _tipelligibility(df):
    st.write("Employee's")
    with open('Tip_Exempt_Employees.md', 'r') as f:
        exempt = f.read().splitlines()
    exempt = set(exempt).intersection(df['Full Name'].unique())
    if len(exempt)==0: exempt = None
    col20, col21, col22, col23 = st.columns([1,.1,1,.1])
    try:
        user_not_tipped = col20.multiselect(
                    "Employee's with job classification not elligible for tips",
                    df['Full Name'].unique(),
                    default=exempt,
                    key='1'
                )
    except Exception:
        st.error('All names within "Tip_Exempt_Employees.md" must match')
        user_not_tipped = col20.multiselect(
                    "Employee's with job classification not elligible for tips",
                    df['Full Name'].unique(),
                    key='2'
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

#@st.cache_data
def _all_positions():
    with open('Tip_Pool_Positions.md', 'r') as f:
        val = f.read()
    return eval(val)


def positiondefaults(val):
    mydict = _all_positions()
    for type in mydict.keys():
        for pos in mydict.get(type):
            if pos == val: 
                return type


def position_pool(val, df):
    return df[df['Position']==val]['Tip Pool'].iloc[0]


def pool_rate(x, rate):
    keys = list(_all_positions().keys())
    if x == keys[0]:
        return rate[0]
    elif x == keys[1]:
        return rate[1]
    elif x == keys[2]:
        return rate[2]
    elif x == keys[3]:
        return rate[3]
    elif x == keys[4]:
        return rate[4]


def _tip_pools(_df):
    df = pd.DataFrame({'Position': _df['Position'].dropna().unique()})
    df.insert(0, 'Tip Pool', '')
    df['Tip Pool'] = [positiondefaults(a) for a in df['Position']]
    st.write("Positions")
    col30, col31, col32, col33, col34 = st.columns([1,.1,1,.1,1])
    df_tip = col30.data_editor(
        df,
        hide_index=True,
        column_config={
            'Tip Pool': st.column_config.SelectboxColumn(
                help='The tip category associated with Position',
                width='medium',
                options=_all_positions().keys()
                ),
            'Position': st.column_config.TextColumn(
                width='medium'
                )
            },
        )
    #front_tip_pool = df_tip[df_tip['Tip Pool'] == 'Front of House']['Position'].values
    #back_tip_pool = df_tip[df_tip['Tip Pool'] == 'Back of House']['Position'].values
    return df_tip


def applysplits_hrs(hrs, pos, _match):
    val = _match[_match['from']==pos].iloc[0]['perc']
    val = val/100
    #st.write(val)
    #if pos == 'Host':
    return val*hrs
    #return hrs


def applysplits_reas(hrs, pos, _match):
    reas = _match[_match['from']==pos].iloc[0]['reason']
    return reas


def applysplits_pos(hrs, pos, _match):
    pos = _match[_match['from']==pos].iloc[0]['to']
    return pos


def applysplits(_df, _res):
    df = _df.copy()
    df['Regular'] = [applysplits_hrs(*a,_res) for a in tuple(zip(_df['Regular'], _df['Position']))]
    df['New Position'] = [applysplits_pos(*a,_res) for a in tuple(zip(_df['Regular'], _df['Position']))]
    df['reason'] = [applysplits_reas(*a,_res) for a in tuple(zip(_df['Regular'], _df['Position']))]
    return df


def _position_splits(_df):
    df_revised = _df.copy()
    st.write("Revise Elligible Tip Hours Split by Position")
    df = pd.DataFrame(columns=['perc', 'from', 'to', 'reason'])
    positions = df_revised['Position'].dropna().unique()
    config = {
        'perc': st.column_config.NumberColumn('Take (%) of hrs', required=True, width='medium'),
        'from': st.column_config.SelectboxColumn('From Old Position', width='medium', options=positions, required=True),
        'to': st.column_config.SelectboxColumn('Move to New Position', width='medium', options=positions, required=True),
        'reason': st.column_config.TextColumn('For the Reason', width='large', required=True),
    }
    result = st.data_editor(df, column_config=config, num_rows='dynamic', hide_index=True)
    #r_from=result[['perc', 'from']].copy()
    df_app = df_revised[df_revised['Position'].isin(result['from'])][['Full Name', 'Regular', 'Position']]
    df_revised['reason'] = ''
    df_add = applysplits(df_app, result)
    df_remove = df_add.copy()
    df_add['Position'] = df_add['New Position']
    df_add = df_add.drop(columns=['New Position'])
    df_remove['Regular'] = -df_remove['Regular']
    df_remove = df_remove.drop(columns=['New Position'])
    df_revised = pd.concat([df_revised, df_add, df_remove], ignore_index=True)
    return df_revised


def _setup_tipping_pools(_df: pd.DataFrame) -> pd.DataFrame:
    st.markdown('---')
    with st.expander('Tipping Rules'):
        col1, col2, col3 = st.columns([.1,.85,.05])
        col1.subheader('Tipping Elligibility')
        with col2:
            df_tipElligible, df_tipInElligible = _tipelligibility(_df)
            st.markdown('---')
            tip_pool_pos = _tip_pools(df_tipElligible)
            st.markdown('---')
            df_tipElligible = _position_splits(df_tipElligible)
    return df_tipElligible, tip_pool_pos


def _tip_amounts(ukey):
    col40, col41, col42, col43 = st.columns([1,1,1,1])
    totalPool = float(col40.text_input('Total Pool ($)', value='0.00', key=ukey+'1'))
    chefPercent = float(col41.number_input('Chef Percentage (%)', value=18, key=ukey+'2'))/100
    chefCut = round(totalPool*chefPercent,2)
    tippingPool_Garden = float(col42.text_input('Garden Pool ($)', value='0.00', key=ukey+'3'))
    tippingPool_Reg = float(col43.text_input('Regular Pool ($)', value=str(totalPool-chefCut-tippingPool_Garden), key=ukey+'4', disabled=True))

    chefCount = col40.number_input('# Chefs', value=4, key=ukey+'5')
    chefCut_ind = col41.text_input('Each Chefs tip total ($)', value=str(chefCut/chefCount), key=ukey+'6', disabled=True)  
    return tippingPool_Garden, tippingPool_Reg


def _tip_percents(ukey):
    keys = list(_all_positions().keys())
    vals = list()
    col40, col41, col42, col43, col44 = st.columns([1,1,1,1,1])
    vals.append(col40.number_input(label=keys[0], step=1, value=40, key=ukey+'g1'))
    vals.append(col41.number_input(label=keys[1], step=1, value=20, key=ukey+'g2'))
    vals.append(float(col42.text_input(label=keys[2], value=str(100-vals[0]-vals[1]), key=ukey+'g3', disabled=True)))
    vals.append(col43.number_input(label=keys[3], step=1, value=60, key=ukey+'f2'))
    vals.append(float(col44.text_input(label=keys[4], value=str(100-vals[3]), key=ukey+'b2', disabled=True)))
    return vals


def _hrs_split(_df, _pool):
    df = _df.copy()
    df['Tip Pool'] = [position_pool(x, _pool) for x in df['Position']]
    keys = list(_all_positions().keys())
    return df


def _tip_info(idx, pooltotal, split, _df_hrs, rates):
    keys = list(_all_positions().keys())
    poolname = keys[idx]
    total = pooltotal*(split[idx]/100)
    if len(_df_hrs.index) == 0:
        str = 'No Entries'
        hrs=0
        rate=0
    else:
        hrs = _df_hrs[_df_hrs['Tip Pool'] == keys[idx]]['Regular'].sum()
        rate = total/hrs if hrs != 0 else 0
        str = f'''{poolname}:  
                * Percent Split = {split[idx]}%  
                * Tip Pool = \${round(total,2)}  
                * Hours Worked = {round(hrs,2)}  
                * Tip Rate = \${round(rate,2)}/hr  
                '''
    if hrs==0 and total != 0:
        st.warning(str)
    elif hrs!=0 and total ==0:
        st.warning(str)
    else:
        st.info(str)
    rates.append(rate)


def _display_tips(_df_tips):
    #col1, col2 = st.columns([3,2])
    st.caption('Grouped by Position')
    _df_tips_pos = _format_aggregate(_aggregate_name_position(_df_tips))
    st.dataframe(_df_tips_pos, column_config={
        'Full Name': st.column_config.TextColumn(width='medium'),
        'Position': st.column_config.TextColumn(width='medium')
    })
    #st.caption('Payroll')
    #_df_tips_f = _format_aggregate(_aggregate_name(_df_tips))
    #col2.dataframe(_df_tips_f, column_config={
    #    'Full Name': st.column_config.TextColumn(width='medium')
    #})


def _confirm_tip_total(_df_tips, tippingPool_Garden, tippingPool_Reg):
    col1, col2 = st.columns([1,1])
    totalpool = tippingPool_Garden+tippingPool_Reg
    dispersed = _df_tips[['Tip Total']].to_numpy().sum()
    col1.caption(f'Total of Tipping Pool = ${round(totalpool,2)}')
    col2.caption(f'Total Tips Dispersed = ${round(dispersed,2)}')
    if ~np.isclose(totalpool, dispersed, atol=0.001):
        st.warning('Not all tips have been allocated')


def _display_changes(_df_tips, _df_tips_adjusted):
    _df_tips_f = _aggregate_name(_df_tips)
    _df_tips_adjusted_f = _aggregate_name(_df_tips_adjusted)
    _df_diff = _df_tips_adjusted_f-_df_tips_f
    _df_diff = _df_diff.loc[(_df_diff!=0).any(axis=1)]
    _df_diff = _format_aggregate(_df_diff)
    st.caption('Changes in Tips')
    st.dataframe(_df_diff, column_order=['Full Name', 'Tip Elligible Hours', 'Tip Total'])
    

def _tipping_pools(df_tipElligible, tip_pool_pos) -> pd.DataFrame:
    with st.expander('Tipping Pool', expanded=True):
        col1, col2, col3 = st.columns([.1,.85,.05])
        col1.subheader('Pay Cycle Tipping Pool')
        with col2:
            tippingPool_Garden, tippingPool_Reg = _tip_amounts('first')
            splitvals = _tip_percents('first')
            df_tipElligible = _hrs_split(df_tipElligible, tip_pool_pos)
            rates=list()
            col40, col41, col42, col43, col44 = st.columns([1,1,1,1,1])
            with col40: _tip_info(0, tippingPool_Garden, splitvals, df_tipElligible, rates)
            with col41: _tip_info(1, tippingPool_Garden, splitvals, df_tipElligible, rates)
            with col42: _tip_info(2, tippingPool_Garden, splitvals, df_tipElligible, rates)
            with col43: _tip_info(3, tippingPool_Reg, splitvals, df_tipElligible, rates)
            with col44: _tip_info(4, tippingPool_Reg, splitvals, df_tipElligible, rates)
            df_tipElligible['Tip Rate'] = [pool_rate(x, rates) for x in df_tipElligible['Tip Pool']]
            #_df_hrs['Tip Total'] = _df_hrs['Tip Rate'] * _df_hrs['Regular']
            #_df_hrs['Cash Wage plus Tip'] = _df_hrs['Tip Total'] + _df_hrs['Paid Total']  # _df_hrs[['Tip Total','Paid Total']].sum(axis=1)
            _df_tips = payroll_summary(df_tipElligible)
            #st.markdown('---')
            #_confirm_tip_total(_df_tips, tippingPool_Garden, tippingPool_Reg)
        return _df_tips, tippingPool_Garden, tippingPool_Reg, splitvals


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
    return df_revised


def _adjust_tipping_pools(_df_tips, tippingPool_Garden, tippingPool_Reg, user_garden_input,
                          df_tipElligible, front_tip_pool, back_tip_pool) -> pd.DataFrame:
    
    with st.expander('Adjust Tipping Pool', expanded=False):
        col1, col2, col3 = st.columns([.1,.85,.05])
        col1.subheader('Work Position Corrections')
        with col2:
            df_tipElligible_adjusted = _adjust_work_pos(df_tipElligible)
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
            st.markdown('---')
            _confirm_tip_total(_df_tips_adjusted, tippingPool_Garden, tippingPool_Reg)
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
        st.write(f"Total Hours: {round(df['Regular'].sum(),2)}, Total Cash Wages: ${round(df['Paid Total'].sum(),2):,}")
    return df


def run(file_path: str) -> pd.DataFrame:
    _df = read_csv(file_path)
    _df = _clean_import(_df)
    _df = _combine_FullName(_df)
    filter_dataframe(_df)
    df_tipElligible, tip_pool_pos = _setup_tipping_pools(_df)
    _df_tips, tippingPool_Garden, tippingPool_Reg, splitvals = _tipping_pools(df_tipElligible, tip_pool_pos)
    st.stop()
    _df_tips_adjusted, df_tipElligible_adjusted = _adjust_tipping_pools(_df_tips, tippingPool_Garden, tippingPool_Reg, user_garden_input,
                          df_tipElligible, front_tip_pool, back_tip_pool)
    return _df_tips, _df_tips_adjusted
