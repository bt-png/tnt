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
    df['Employee Name'] = df[cols].apply(lambda row: ' '.join(row.values.astype(str)), axis=1)
    return df


def payroll_summary(_df):
    df = _add_payroll_summary(_df)
    df_agg = _payroll_group_by_tips(df)
    display_payroll_summary(df_agg)
    return df


def position_summary(_df):
    df = _add_payroll_summary(_df)
    df_agg = _payroll_group_by_pos(df)
    display_position_summary(df_agg)
    return df


def _add_payroll_summary(_df):
    keys = list(_all_positions().keys())
    df = _df.copy()
    df['Hours'] = df['Regular']
    df['Wage'] = df['Paid Total']
    df['Tip'] = df['Hours'] * df['Tip Rate']
    df['Wage + Tip'] = df['Wage'] + df['Tip']
    df['Garden Tips'] = [df[(df['Employee Name'] == x) & (df['Tip Pool'].isin([keys[0], keys[1], keys[2]]))]['Tip'].sum() for x in df['Employee Name']]
    df['Regular Tips'] = [df[(df['Employee Name'] == x) & (df['Tip Pool'].isin([keys[3], keys[4]]))]['Tip'].sum() for x in df['Employee Name']]
    return df

def _payroll_group_by_tips(_df):
    df_agg = _df.groupby(['Employee Name', 'Garden Tips', 'Regular Tips']).agg({
        'Hours': sum,
        'Wage': sum,
        'Wage + Tip': sum
        })
    df_agg = df_agg.reset_index()
    #df_agg = df_agg.drop(['index'], axis=1)
    return df_agg

def _payroll_group_by_pos(_df):
    df_agg = _df.groupby(['Employee Name', 'Position']).agg({
        'Hours': sum,
        'Wage': sum,
        'Tip': sum,
        'Wage + Tip': sum
        })
    df_agg = df_agg.reset_index()
    #df_agg = df_agg.drop(['index'], axis=1)
    return df_agg


def display_position_summary(_df):
    st.dataframe(_df, hide_index=True, height=650, column_order=['Employee Name', 'Position', 'Hours', 'Tip'],column_config={
        'Employee Name': st.column_config.TextColumn(width='medium'),
        'Position': st.column_config.TextColumn(width='medium'),
        'Hours': st.column_config.NumberColumn(width='small', format='%.2f'),
        'Tip': st.column_config.NumberColumn(width='small', format='$ %.2f'),
    })


def display_payroll_summary(_df):
    st.dataframe(_df, hide_index=True, height=650, column_config={
        'Employee Name': st.column_config.TextColumn(width='medium'),
        'Garden Tips': st.column_config.NumberColumn(format='$ %.2f'),
        'Regular Tips': st.column_config.NumberColumn(format='$ %.2f'),
        'Hours': st.column_config.NumberColumn(width='small', format='%.2f'),
        'Wage': st.column_config.NumberColumn(width='small', format='$ %.2f'),
        'Wage + Tip': st.column_config.NumberColumn(format='$ %.2f')
    })


def display_payroll_summary_House(_df):
    st.dataframe(_df, hide_index=True, height=650, column_order=[
        'Employee Name', 'Hours', 'Wage + Tip', 'Garden Tips', 'Regular Tips', 'House Tip', '% Change'], column_config={
        'Employee Name': st.column_config.TextColumn(width='medium'),
        'Garden Tips': st.column_config.NumberColumn(format='$ %.2f'),
        'Regular Tips': st.column_config.NumberColumn(format='$ %.2f'),
        'Hours': st.column_config.NumberColumn(label='Total Hours', format='%.2f'),
        'Wage + Tip': st.column_config.NumberColumn(format='$ %.2f'),
        'House Tip': st.column_config.NumberColumn(format='$ %.2f'),
        #'% Change': st.column_config.NumberColumn(format=':.2%')
    })


def _aggregate_name(_df: pd.DataFrame) -> pd.DataFrame:
    df = _df.copy()
    df['Tip Elligible Hours'] = df['Regular']
    df['Cash Wage'] = df['Paid Total']
    df = df.groupby(['Employee Name']).agg({
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
    df = df.groupby(['Employee Name', 'Position']).agg({
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
    exempt = set(exempt).intersection(df['Employee Name'].unique())
    if len(exempt)==0: exempt = None
    col20, col21, col22, col23 = st.columns([1,.1,1,.1])
    try:
        user_not_tipped = col20.multiselect(
                    "Employee's with job classification not elligible for tips",
                    df['Employee Name'].unique(),
                    default=exempt,
                    key='1'
                )
    except Exception:
        st.error('All names within "Tip_Exempt_Employees.md" must match')
        user_not_tipped = col20.multiselect(
                    "Employee's with job classification not elligible for tips",
                    df['Employee Name'].unique(),
                    key='2'
                    )
    df_tipElligible = df[~df['Employee Name'].isin(user_not_tipped)]
    df_tipInElligible = df[df['Employee Name'].isin(user_not_tipped)]
    col22.caption('Tip Elligible Employees')
    with col22:
        _str = ' | '
        for names in df_tipElligible['Employee Name'].unique():
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
                width='large'
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
    with open('Position_Splits.md', 'r') as f:
        val = f.read()
    mydict = eval(val)
    #df = pd.DataFrame(columns=['perc', 'from', 'to', 'reason'])
    df = pd.DataFrame(mydict)
    positions = df_revised['Position'].dropna().unique()
    config = {
        'perc': st.column_config.NumberColumn('Take (%) of hrs', required=True, width='medium'),
        'from': st.column_config.SelectboxColumn('From Old Position', width='medium', options=positions, required=True),
        'to': st.column_config.SelectboxColumn('Move to New Position', width='medium', options=positions, required=True),
        'reason': st.column_config.TextColumn('For the Reason', width='large', required=True),
    }
    result = st.data_editor(df, column_config=config, num_rows='dynamic', hide_index=True)
    #r_from=result[['perc', 'from']].copy()
    df_app = df_revised[df_revised['Position'].isin(result['from'])][['Employee Name', 'Regular', 'Position']]
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


def _tip_percents(ukey, split_vals):
    keys = list(_all_positions().keys())
    vals = list()
    col40, col41, col42, colspace, col43, col44 = st.columns([1,1,1,.5, 1,1])
    vals.append(col40.number_input(label=keys[0], step=1, value=split_vals[0], key=ukey+'g1'))
    vals.append(col41.number_input(label=keys[1], step=1, value=split_vals[1], key=ukey+'g2'))
    vals.append(float(col42.text_input(label=keys[2], value=str(100-vals[0]-vals[1]), key=ukey+'g3', disabled=True)))
    vals.append(col43.number_input(label=keys[3], step=1, value=split_vals[3], key=ukey+'f2'))
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
        'Employee Name': st.column_config.TextColumn(width='medium'),
        'Position': st.column_config.TextColumn(width='medium')
    })
    #st.caption('Payroll')
    #_df_tips_f = _format_aggregate(_aggregate_name(_df_tips))
    #col2.dataframe(_df_tips_f, column_config={
    #    'Employee Name': st.column_config.TextColumn(width='medium')
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
    st.dataframe(_df_diff, column_order=['Employee Name', 'Tip Elligible Hours', 'Tip Total'])
    

def _tipping_pools(df_tipElligible, tip_pool_pos) -> pd.DataFrame:
    with st.expander('Tipping Pool', expanded=True):
        col1, col2, col3 = st.columns([.1,.85,.05])
        col1.subheader('Pay Cycle Tipping Pool')
        with col2:
            tippingPool_Garden, tippingPool_Reg = _tip_amounts('first')
            st.markdown('---')
            def_splitvalues = [70, 15, 15, 66, 34]
            splitvals = _tip_percents('first',def_splitvalues)
            df_tipElligible = _hrs_split(df_tipElligible, tip_pool_pos)
            rates=list()
            col40, col41, col42, colspace, col43, col44 = st.columns([1,1,1,.5,1,1])
            with col40: _tip_info(0, tippingPool_Garden, splitvals, df_tipElligible, rates)
            with col41: _tip_info(1, tippingPool_Garden, splitvals, df_tipElligible, rates)
            with col42: _tip_info(2, tippingPool_Garden, splitvals, df_tipElligible, rates)
            with col43: _tip_info(3, tippingPool_Reg, splitvals, df_tipElligible, rates)
            with col44: _tip_info(4, tippingPool_Reg, splitvals, df_tipElligible, rates)
            st.markdown('---')
            df_tipElligible['Tip Rate'] = [pool_rate(x, rates) for x in df_tipElligible['Tip Pool']]
            #_df_tips = payroll_summary(df_tipElligible)
            _df_tips = _add_payroll_summary(df_tipElligible)
            df_tips_agg = _payroll_group_by_tips(_df_tips)
            df_tips_agg = df_tips_agg.reset_index()
            df_tips_agg = df_tips_agg.drop(['index'], axis=1)
            df_tips_agg['House Tip'] = 0
            df_tips_agg =st.data_editor(df_tips_agg, num_rows='fixed', height=650, hide_index=True, column_order=[
                'Employee Name', 'Hours', 'Wage + Tip', 'Garden Tips', 'Regular Tips', 'House Tip'], column_config={
                    'Employee Name': st.column_config.TextColumn(width='medium', disabled=True),
                    'Garden Tips': st.column_config.NumberColumn(format='$ %.2f', disabled=True),
                    'Regular Tips': st.column_config.NumberColumn(format='$ %.2f', disabled=True),
                    'Hours': st.column_config.NumberColumn(label='Total Hours', format='%.2f', disabled=True),
                    'Wage + Tip': st.column_config.NumberColumn(format='$ %.2f', disabled=True),
                    'House Tip': st.column_config.NumberColumn(format='$ %.2f', disabled=False)
            })
        return df_tips_agg, tippingPool_Garden, tippingPool_Reg, splitvals


def _adjust_work_pos(_df):
    df_revised = _df.copy()
    st.write("Revise Hours worked under Position")
    df = pd.DataFrame(columns=['name', 'hrs', 'from', 'to', 'reason'])
    employees = _df['Employee Name'].dropna().unique()
    positions = _df['Position'].dropna().unique()
    config = {
        'name': st.column_config.SelectboxColumn('Employee Name', width='medium', required=True, options=employees),
        'hrs': st.column_config.NumberColumn('Move (hrs)', required=True, width='medium'),
        'from': st.column_config.SelectboxColumn('From Old Position', width='medium', options=positions, required=True),
        'to': st.column_config.SelectboxColumn('to New Position', width='medium', options=positions, required=True),
        'reason': st.column_config.TextColumn('Reason', width='large', required=True, default='split shift'),
    }
    result = st.data_editor(df, column_config=config, num_rows='dynamic', hide_index=True)
    df_revised['reason'] = ''
    df_add = pd.DataFrame({'Employee Name': result['name'], 'Regular': result['hrs'], 'Position': result['to'], 'reason': result['reason']})
    df_remove = pd.DataFrame({'Employee Name': result['name'], 'Regular': -result['hrs'], 'Position': result['from'], 'reason': result['reason']})
    df_revised = pd.concat([df_revised, df_add, df_remove], ignore_index=True)
    return df_revised


def _adjust_tipping_pools(df_tipElligible, tip_pool_pos, tippingPool_Garden, tippingPool_Reg, adjsplitvals) -> pd.DataFrame:
    with st.expander('Adjust Tip Pools', expanded=False):
        col1, col2, col3 = st.columns([.1,.85,.05])
        col1.subheader('Work Position Corrections')
        with col2:
            col10, col11 = st.columns([1,1])
            grouped = df_tipElligible.groupby(['Employee Name', 'Position']).agg({
                'Employee Name': 'first',
                'Position': 'first',
                'Regular': sum,
                })
            user_cat_input = col10.multiselect(
                f"Choose 'Employee Name' to Apply Filter",
                grouped['Employee Name'].unique(),

            )
            if len(user_cat_input) > 0:
                grouped = grouped[grouped['Employee Name'].isin(user_cat_input)]
            col11.dataframe(grouped, hide_index=True, height=150, column_config={
                'Employee Name': st.column_config.TextColumn(width='medium'),
                'Position': st.column_config.TextColumn(width='medium'),
                'Regular': st.column_config.NumberColumn(label='Hours', width='small'),
                })

            df_tipElligible_adjusted = _adjust_work_pos(df_tipElligible)
            st.markdown('---')
            splitvals = _tip_percents('second', adjsplitvals)
            df_tipElligible_adjusted = _hrs_split(df_tipElligible_adjusted, tip_pool_pos)
            rates=list()
            col40, col41, col42, colspace, col43, col44 = st.columns([1,1,1,.5,1,1])
            with col40: _tip_info(0, tippingPool_Garden, splitvals, df_tipElligible_adjusted, rates)
            with col41: _tip_info(1, tippingPool_Garden, splitvals, df_tipElligible_adjusted, rates)
            with col42: _tip_info(2, tippingPool_Garden, splitvals, df_tipElligible_adjusted, rates)
            with col43: _tip_info(3, tippingPool_Reg, splitvals, df_tipElligible_adjusted, rates)
            with col44: _tip_info(4, tippingPool_Reg, splitvals, df_tipElligible_adjusted, rates)
            st.markdown('---')
            df_tipElligible_adjusted['Tip Rate'] = [pool_rate(x, rates) for x in df_tipElligible_adjusted['Tip Pool']]
            _df_tips_adjusted = position_summary(df_tipElligible_adjusted)
            df_tips_adjusted_agg = _payroll_group_by_tips(_df_tips_adjusted)
            df_tips_adjusted_agg = df_tips_adjusted_agg.reset_index()
        return df_tips_adjusted_agg


def filter_dataframe(_df: pd.DataFrame) -> pd.DataFrame:
    df = _df.copy()
    with st.container():
        to_filter_columns = ['Employee Name']  # st.multiselect("Filter dataframe on", df.columns)  # ('Employee Name', 'Position') #   # 
        for column in to_filter_columns:
            user_cat_input = st.multiselect(
                f"Choose {column} to Apply Filter",
                df[column].unique() #,
                #default=()# list(df[column].unique())
            )
            if len(user_cat_input) > 0:
                df = df[df[column].isin(user_cat_input)]
    st.dataframe(df, hide_index=True, height=150)
    st.write(f"Total Hours: {round(df['Regular'].sum(),2)}, Total Cash Wages: ${round(df['Paid Total'].sum(),2):,}")
    return df


def run(file_path: str) -> pd.DataFrame:
    _df = read_csv(file_path)
    _df = _clean_import(_df)
    _df = _combine_FullName(_df)
    with st.expander(label='Original Data', expanded=False):
        filter_dataframe(_df)
    df_tipElligible, tip_pool_pos = _setup_tipping_pools(_df)
    df_tips_agg, tippingPool_Garden, tippingPool_Reg, splitvals = _tipping_pools(df_tipElligible, tip_pool_pos)
    _df_tips_adjusted = _adjust_tipping_pools(df_tipElligible, tip_pool_pos, tippingPool_Garden, tippingPool_Reg, splitvals)
    with st.expander(label='Payroll Summary', expanded=False):
        col1, col2 = st.columns([1,1])
        with col1:
            st.caption('Default Positions')
            df_tips_agg['% Change'] = round(100*((df_tips_agg['Garden Tips']+df_tips_agg['Regular Tips'])-df_tips_agg['House Tip'])/df_tips_agg['House Tip'],2)
            df_tips_agg['% Change'] = [str(x)+'%' if abs(x)!=np.inf else '' for x in df_tips_agg['% Change']]
            display_payroll_summary_House(df_tips_agg)
        #st.markdown('---')
        with col2:
            st.caption('Revised Positions')
            _df_tips_adjusted['House Tip'] = df_tips_agg['House Tip']
            #st.dataframe(_df_tips_adjusted)
            #st.stop()
            _df_tips_adjusted['% Change'] = round(100*((_df_tips_adjusted['Garden Tips']+_df_tips_adjusted['Regular Tips'])-df_tips_agg['House Tip'])/_df_tips_adjusted['House Tip'],2)
            _df_tips_adjusted['% Change'] = [str(x)+'%' if abs(x)!=np.inf else '' for x in _df_tips_adjusted['% Change']]
            _df_tips_adjusted = _df_tips_adjusted.drop(['index'], axis=1)
            display_payroll_summary_House(_df_tips_adjusted)
    return df_tips_agg, _df_tips_adjusted
