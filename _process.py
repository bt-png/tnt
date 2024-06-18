import streamlit as st
import _gitfiles
import pandas as pd
import numpy as np
import json
from datetime import datetime

Deployed = True


def save_data():
    bitfile = json.dumps(st.session_state['newdict'])
    if Deployed:
        _gitfiles.commit(
            filename='current_save.csv',
            message='api commit',
            content=bitfile
        )
    else:
        # Save locally during testing
        try:
            with open('current_save.csv', 'w') as file:
                file.write(bitfile)
            st.success('Save Data Has been Saved')
        except Exception:
            st.warning('Something went wrong')


def read_csv(file_path: str) -> pd.DataFrame:
    _df = pd.read_csv(file_path)
    return _df


def _clean_import(_df: pd.DataFrame) -> pd.DataFrame:
    df = _df.copy()
    try:
        df['Paid Total'] = df['Paid Total'].str.replace('$', '', regex=False)
    except Exception:
        pass
    df['Paid Total'] = df['Paid Total'].astype(float)
    df['Paid Total'] = df['Paid Total'].replace(np.nan, 0)
    return df


def _combine_FullName(_df: pd.DataFrame) -> pd.DataFrame:
    df = _df.copy()
    cols = ['First Name', 'Last Name']
    df['Employee Name'] = df[cols].apply(lambda row: ' '.join(row.values.astype(str)), axis=1)
    return df


def gardenEventsPicker():
    if 'df_sales' in st.session_state:
        #dates = st.date_input('Select Garden Event Dates', )
        dfDates = pd.DataFrame({'Dates': []})
        dfDates['Dates'] = dfDates['Dates'].astype('datetime64[as]')
        dfDates = st.data_editor(dfDates, num_rows='dynamic', key='gardendates', column_config={
            'Dates': st.column_config.DateColumn('Garden Event Days', format='MM/DD/YYYY')
            })
        try:
            dfDates['str'] = ["{:%m/%d/%Y}".format(date) for date in dfDates['Dates']]
        except:
            dfDates['str'] = None
        dfDates['str'] = dfDates['str'].astype(str)
        df = st.session_state['df_sales']
        if df is not None:
            df = df.reset_index()
            df = pd.merge(left=df, left_on='index', right=dfDates, right_on='str', how='inner')
            tip = round(df['Tip'].sum(),2)
            st.write(f'Total tips from selected dates from Square = ${tip}')
            extratip = float(st.text_input('Additional Garden Tips', value=0.0))
            totaltip = round(tip + extratip,2)
            st.write(f'Total Garden Tips = ${totaltip}')
            if st.button('Apply'):
                st.session_state['dict']['Garden Pool'] = totaltip
                st.session_state['newdict']['Garden Pool'] = st.session_state['dict']['Garden Pool']
                st.session_state['dict']['Total Pool'] += extratip
                st.session_state['newdict']['Total Pool'] = st.session_state['dict']['Total Pool']
                st.rerun()
    else:
        st.warning('Please upload the Square tip report to select Garden Event dates.')


def _add_payroll_summary(_df):
    keys = list(_all_positions())
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
        'Hours': 'sum',
        'Wage': 'sum',
        'Tip': 'sum'
        })
    df_agg = df_agg.reset_index()
    return df_agg


def _payroll_group_by_pos(_df):
    df_agg = _df.groupby(['Employee Name', 'Position']).agg({
        'Hours': 'sum',
        'Wage': 'sum',
        'Tip': 'sum',
        'Wage + Tip': 'sum'
        })
    df_agg = df_agg.reset_index()
    return df_agg


def _add_helper_pool(_df, _helper_tips):
    _df = pd.merge(left=_df, left_on=['Employee Name'], right=_helper_tips, right_on=['Employee Name'], how='outer')
    _df['Helper Tips'] = _df['Helper Tips'].fillna(0)
    return _df


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


def df_row_styles(_df):
    row_styles = []
    current_style = None
    _transp = 'background-color: #ffffff'
    _highlight = 'background-color: #f2f7f2'
    for index, row in _df.iterrows():
        if row[0] == 'Total':
            current_style = 'background-color: #CCCCCC'
        elif index % 2 == 0:
            current_style = _transp
        else:
            current_style = _highlight
        row_styles.append(current_style)
    return row_styles


def table_color_rows(_df):
    row_styles = df_row_styles(_df)
    df_p = _df.reset_index(drop=True)
    df_p = df_p.style.apply(lambda x: row_styles, axis=0)
    df_p = df_p.format(precision=2)
    return df_p


def display_position_summary(_df, rev):
    df = _df.copy()
    row_styles = []
    current_style = None
    _transp = 'background-color: #ffffff'
    _highlight = 'background-color: #f2f7f2'
    for index, row in df.iterrows():
        if index % 2 == 0:
            current_style = _transp
        else:
            current_style = _highlight
        row_styles.append(current_style)
    df['Changed'] = [x in list(rev['name']) and y in list(rev['from']) for x, y in zip(df['Employee Name'], df['Position'])]
    df = df.reset_index(drop=True)
    # df = df.style.apply(lambda x: row_styles, axis=0)
    df = df.style.apply(lambda x: [
        "background-color: red" if x['Changed'] and idx == 2
        else ""
        for idx, v in enumerate(x)
        ], axis=1)
    st.dataframe(df, hide_index=True, height=650, column_order=['Employee Name', 'Position', 'Hours', 'Tip'], column_config={
        'Employee Name': st.column_config.TextColumn(width='medium'),
        'Position': st.column_config.TextColumn(width='medium'),
        'Hours': st.column_config.NumberColumn(format='%.2f'),
        'Tip': st.column_config.NumberColumn(format='$ %.2f'),
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


def display_payroll_summary_House_table(_df):
    df = _df.copy()
    row_styles = []
    current_style = None
    _transp = 'background-color: #ffffff'
    _highlight = 'background-color: #f2f7f2'
    for index, row in df.iterrows():
        if index % 2 == 0:
            current_style = _transp
        else:
            current_style = _highlight
        row_styles.append(current_style)
    df = df.reset_index(drop=True)
    df = df.style.apply(lambda x: row_styles, axis=0)
    st.table(df)


def display_payroll_summary_House(_df, _dfchefs, _adj_result):
    col1, col2 = st.columns([1, 1])
    df = _df.copy()
    df['CALC Tips'] = df['Garden Tips'] + df['Regular Tips'] + df['Helper Tips']
    df['Wage + Tip'] = df['CALC Tips'] + df['Wage']
    df.loc['total'] = df[['House Tip', 'CALC Tips', 'Wage', 'Wage + Tip', 'Hours']].sum()
    df.reset_index(drop=True, inplace=True)
    df.loc[df.index[-1], 'Employee Name'] = 'Total'
    df = table_color_rows(df)
    df = df.format('${:.2f}', subset=['CALC Tips', 'House Tip', 'Wage', 'Wage + Tip'])
    col1.subheader('Worker Summary')
    col1.dataframe(df, hide_index=True, height=600, column_order=[
        'Employee Name', 'Hours', 'House Tip', 'CALC Tips', 'Wage + Tip'], column_config={
            'Hours': st.column_config.NumberColumn(label='Total Hours'),
            }
    )
    chefs = _dfchefs.copy()
    chefs = chefs[chefs['Chef Tips'] > 0]
    chefs.reset_index(drop=True, inplace=True)
    chefs.loc['total'] = chefs[['Chef Tips', 'Directed']].sum()
    chefs.reset_index(drop=True, inplace=True)
    chefs.loc[chefs.index[-1], 'Employee Name'] = 'Total'
    chefs = table_color_rows(chefs)
    chefs = chefs.format('${:.2f}', subset=['Chef Tips', 'Directed'])
    col2.subheader('Chef Summary')
    col2.dataframe(chefs, hide_index=True, column_order=[
        'Employee Name', 'Chef Tips', 'Directed'], column_config={
            'Employee Name': st.column_config.TextColumn(label='Chef', width='medium'),
            'Chef Tips': st.column_config.NumberColumn(label='Pool', width='small'),
            'Directed': st.column_config.NumberColumn(width='small')
        }
    )
    col2.header('')
    col2.header('')
    col2.subheader('Tip Summary')
    # Pool Values
    tp = st.session_state['newdict']['Total Pool']
    gp = st.session_state['newdict']['Garden Pool']
    cp = st.session_state['newdict']['Chef Percent']/100
    hp = st.session_state['newdict']['Helper Pool']
    rem = tp-gp-hp
    cc = cp*rem
    rp = rem-cc
    # Garden Splits
    g_foh = st.session_state['newdict']['Garden FOH']/100
    g_h = st.session_state['newdict']['Garden Host']/100
    g_boh = 1-g_foh-g_h
    # Regular Splits
    helper_sum = _df['Helper Tips'].sum()
    helper_percent = helper_sum/rp
    rem_percent = 1-helper_percent
    r_foh = rem_percent*st.session_state['newdict']['Regular FOH']/100
    r_boh = 1-r_foh-helper_percent
    if gp > 0:
        tip_summary = pd.DataFrame({
            'Cuts': ['Garden', 'Regular', 'Chefs'],
            'Total %': [gp/tp, rp/tp, cc/tp],
            'FOH': [g_foh, r_foh, None],
            'BOH': [g_boh, r_boh, None],
            'Other': [g_h, helper_percent, None]
        })
    else:
        tip_summary = pd.DataFrame({
            'Cuts': ['Regular', 'Chefs'],
            'Total %': [rp/tp, cc/tp],
            'FOH': [r_foh, None],
            'BOH': [r_boh, None],
            'Other': [helper_percent, None]
        })
    tip_summary = table_color_rows(tip_summary)
    col2.dataframe(tip_summary.format({
        'Total %': '{:.1%}',
        'FOH': '{:.1%}',
        'BOH': '{:.1%}',
        'Other': '{:.1%}'
        }), hide_index=True)
    if gp > 0:
        col2.caption('Garden Other = Garden Host')
    col2.caption('Regular Other = Helpers')
    st.markdown('---')
    st.subheader('Revised Work Shifts')
    config = {
        'name': st.column_config.TextColumn('Employee Name', width='medium'),
        'hrs': st.column_config.NumberColumn('Move (hrs)', width='medium'),
        'from': st.column_config.TextColumn('From Old Position', width='medium'),
        'to': st.column_config.TextColumn('to New Position', width='medium'),
        'reason': st.column_config.TextColumn('Reason', width='large'),
    }
    st.dataframe(_adj_result, column_config=config, hide_index=True)


def _tipelligibility(df):
    st.write("Employee's")
    with open('Tip_Exempt_Employees.md', 'r') as f:
        default_tip_exempt_employees = f.read().splitlines()
    exempt = st.session_state['dict'].get('Tip Exempt Employees', default_tip_exempt_employees)
    exempt = set(exempt).intersection(df['Employee Name'].unique())
    if len(exempt) == 0: exempt = None
    col20, col21, col22, col23 = st.columns([1, .1, 1, .1])
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
    st.session_state['newdict']['Tip Exempt Employees'] = user_not_tipped
    return df_tipElligible, df_tipInElligible


def _all_positions():
    with open('Tip_Pool_Positions.md', 'r') as f:
        val = f.read()
    dftmp = pd.DataFrame(eval(val))
    dftmp = pd.DataFrame(st.session_state['dict'].get('Tip Pool Positions', dftmp))
    dftmp.reset_index(drop=True, inplace=True)
    dftmp.sort_values('Tip Pool', inplace=True)
    return dftmp['Tip Pool'].dropna().unique()


def positiondefaults(val):
    mydict = _all_positions()
    for type in mydict.keys():
        for pos in mydict.get(type):
            if pos == val:
                return type


def position_pool(val, df):
    try:
        return df[df['Position'] == val]['Tip Pool'].iloc[0]
    except Exception:
        return False


def pool_rate(x, rate):
    keys = list(_all_positions())
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


def _avail_positions(_df):
    with open('Override_Positions.md', 'r') as f:
        override = f.read().splitlines()
    df_override = pd.DataFrame({'Position': override})
    df = pd.DataFrame({'Position': _df['Position'].dropna().unique()})
    df = pd.concat([df, df_override])
    df = pd.DataFrame({'Position': df['Position'].unique()})
    df = df.sort_values(['Position'])
    return df


def _tip_pools(_df):
    df = _avail_positions(_df)
    with open('Tip_Pool_Positions.md', 'r') as f:
        val = f.read()
    dftmp = pd.DataFrame(eval(val))
    dftmp = pd.DataFrame(st.session_state['dict'].get('Tip Pool Positions', dftmp))
    dftmp.reset_index(drop=True, inplace=True)
    df = pd.merge(left=df, left_on='Position', how='outer', right=dftmp, right_on='Position')
    st.write("Positions")
    col30, col31, col32, col33, col34 = st.columns([1, .1, 1, .1, 1])
    df_tip = col30.data_editor(
        df,
        hide_index=True,
        column_order=['Tip Pool', 'Position'],
        column_config={
            'Tip Pool': st.column_config.SelectboxColumn(
                help='The tip category associated with Position',
                width='medium',
                options=_all_positions()
                ),
            'Position': st.column_config.TextColumn(
                width='large'
                )
            },
        )
    st.session_state['newdict']['Tip Pool Positions'] = df_tip.dropna().reset_index(drop=True).to_dict()
    return df_tip


def applysplits_hrs(hrs, pos, _match):
    val = _match[_match['from'] == pos].iloc[0]['perc']
    val = val/100
    return val*hrs


def applysplits_reas(hrs, pos, _match):
    reas = _match[_match['from'] == pos].iloc[0]['reason']
    return reas


def applysplits_pos(hrs, pos, _match):
    pos = _match[_match['from'] == pos].iloc[0]['to']
    return pos


def applysplits(_df, _res):
    df = _df.copy()
    df['Regular'] = [applysplits_hrs(*a, _res) for a in tuple(zip(_df['Regular'], _df['Position']))]
    df['New Position'] = [applysplits_pos(*a, _res) for a in tuple(zip(_df['Regular'], _df['Position']))]
    df['reason'] = [applysplits_reas(*a, _res) for a in tuple(zip(_df['Regular'], _df['Position']))]
    return df


def _position_splits(_df):
    df_revised = _df.copy()
    st.write("Revise Elligible Tip Hours Split by Position")
    with open('Position_Splits.md', 'r') as f:
        val = f.read()
    mydict = eval(val)
    mydict = st.session_state['dict'].get('Position Splits', mydict)
    df = pd.DataFrame(mydict)
    df.reset_index(drop=True, inplace=True)
    positions = _avail_positions(_df)['Position']
    config = {
        'perc': st.column_config.NumberColumn('Take (%) of hrs', required=True, width='medium'),
        'from': st.column_config.SelectboxColumn('From Old Position', width='medium', options=positions, required=True),
        'to': st.column_config.SelectboxColumn('Move to New Position', width='medium', options=positions, required=True),
        'reason': st.column_config.TextColumn('For the Reason', width='large', required=True),
    }
    result = st.data_editor(df, column_config=config, num_rows='dynamic', hide_index=True)
    st.session_state['newdict']['Position Splits'] = result.to_dict()
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
    df_tipElligible, df_tipInElligible = _tipelligibility(_df)
    st.markdown('---')
    tip_pool_pos = _tip_pools(df_tipElligible)
    st.markdown('---')
    df_tipElligible = _position_splits(df_tipElligible)
    return df_tipElligible, tip_pool_pos


def _tip_amounts(ukey):
    col40, col41, col42 = st.columns([1, 1, 1])
    totalPool = float(col40.text_input('Total Pool ($)', value=st.session_state['dict'].get('Total Pool', 0.01), key=ukey+'1'))
    st.session_state['newdict']['Total Pool'] = totalPool
    tippingPool_Garden = float(col41.text_input('Garden Pool ($)', value=st.session_state['dict'].get('Garden Pool', 0.00), key=ukey+'3'))
    st.session_state['newdict']['Garden Pool'] = tippingPool_Garden
    helperPool = float(col42.text_input("Helper Pool ($)", value=st.session_state['dict'].get('Helper Pool', 0.00), key=ukey+'4'))
    remaining = float(col40.text_input('Remaining Pool ($)', value=round(totalPool-tippingPool_Garden-helperPool,2), disabled=True))
    chefPercent = float(col41.number_input('Chef Percentage (%)', value=st.session_state['dict'].get('Chef Percent', 18), key=ukey+'2'))/100
    st.session_state['newdict']['Chef Percent'] = chefPercent*100
    chefCut = float(col41.text_input('Chef Cut ($)', value=round(remaining * chefPercent, 2), disabled=True))
    tippingPool_Reg = float(col42.text_input('Regular Pool ($)', value=round(totalPool - tippingPool_Garden - helperPool - chefCut,2), key=ukey+'5', disabled=True))
    st.session_state['newdict']['Helper Pool'] = helperPool
    col1, col2 = st.columns([5,1])
    col1.caption('''
                $Remaining Pool = Total Pool - (Garden Pool + Helper Pool)$  
                ${Chef Cut} = {Remaining Pool} \cdot {Chef Percentage}$  
                ${Regular Pool} = {Remaining Pool} - {Chef Cut}$  
                ''')
    if col2.button('Save'):
        save_data()
    return tippingPool_Garden, tippingPool_Reg, chefCut, helperPool


def _tip_percents(ukey, split_vals):
    keys = list(_all_positions())
    vals = list()
    col40, col41, col42, colspace, col43, col44 = st.columns([1, 1, 1, .5, 1, 1])
    col40.subheader(keys[0])
    col41.subheader(keys[1])
    col42.subheader(keys[2])
    col43.subheader(keys[3])
    col44.subheader(keys[4])
    vals.append(col40.number_input(label=keys[0], step=1, value=split_vals[0], key=ukey+'g1', label_visibility='collapsed'))
    vals.append(col41.number_input(label=keys[1], step=1, value=split_vals[1], key=ukey+'g2', label_visibility='collapsed'))
    vals.append(float(col42.text_input(label=keys[2], value=str(100-vals[0]-vals[1]), key=ukey+'g3', disabled=True, label_visibility='collapsed')))
    vals.append(col43.number_input(label=keys[3], step=1, value=split_vals[3], key=ukey+'f2', label_visibility='collapsed'))
    vals.append(float(col44.text_input(label=keys[4], value=str(100-vals[3]), key=ukey+'b2', disabled=True, label_visibility='collapsed')))
    return vals


def _hrs_split(_df, _pool):
    df = _df.copy()
    df['Tip Pool'] = [position_pool(x, _pool) for x in df['Position']]
    return df


def _tip_info(idx, pooltotal, split, _df_hrs, rates):
    keys = list(_all_positions())
    poolname = keys[idx]
    total = pooltotal*(split[idx]/100)
    emp_count = _df_hrs[_df_hrs['Tip Pool'] == poolname]['Employee Name'].unique()
    if len(_df_hrs.index) == 0:
        str = 'No Entries'
        hrs = 0
        rate = 0
    else:
        hrs = _df_hrs[_df_hrs['Tip Pool'] == keys[idx]]['Regular'].sum()
        rate = total/hrs if hrs != 0 else 0
        str = f'''Pool Value: \${round(total,2)}  
                hrs in Pool: {round(hrs,2)}  
                # Employees: {len(emp_count)}  

                Tip Rate/hr: ${round(rate,2)}  
                '''
    if hrs == 0 and total != 0:
        st.warning(str)
    elif hrs != 0 and total == 0:
        st.warning(str)
    else:
        st.info(str)
    rates.append(rate)


def _adjust_work_pos(_df):
    df_revised = _df.copy()
    st.write("Revise Hours worked under Position")
    df = pd.DataFrame(st.session_state['dict'].get('Work Position Revisions'))
    if df.empty:
        df = pd.DataFrame(columns=['name', 'hrs', 'from', 'to', 'reason'])
    df.reset_index(drop=True, inplace=True)
    employees = _df['Employee Name'].dropna().unique()
    positions = _avail_positions(_df)['Position']
    config = {
        'name': st.column_config.SelectboxColumn('Employee Name', width='medium', required=True, options=employees),
        'hrs': st.column_config.NumberColumn('Move (hrs)', required=True, width='medium'),
        'from': st.column_config.SelectboxColumn('From Old Position', width='medium', options=positions, required=True),
        'to': st.column_config.SelectboxColumn('to New Position', width='medium', options=positions, required=True),
        'reason': st.column_config.TextColumn('Reason', width='large', required=True, default='split shift'),
    }
    result = st.data_editor(df, column_config=config, num_rows='dynamic', hide_index=True)
    st.session_state['newdict']['Work Position Revisions'] = result.to_dict()
    df_revised['reason'] = ''
    df_add = pd.DataFrame({'Employee Name': result['name'], 'Regular': result['hrs'], 'Position': result['to'], 'reason': result['reason']})
    df_remove = pd.DataFrame({'Employee Name': result['name'], 'Regular': -result['hrs'], 'Position': result['from'], 'reason': result['reason']})
    df_revised = pd.concat([df_revised, df_add, df_remove], ignore_index=True)
    col1, col2 = st.columns([5,1])
    if col2.button('Save', key='positionsave'):
        save_data()
    return df_revised, result


def _tipping_pools(df_tipElligible, tip_pool_pos) -> pd.DataFrame:
    tippingPool_Garden, tippingPool_Reg, chefCut, helperPool = _tip_amounts('first')
    st.markdown('---')
    with st.expander('Chefs and Helpers', expanded=False):
        col0, col10, col01, col11, col02, col12 = st.columns([.1, 1, .1, 1, .1, 1])
        # CHEFS
        with open('Chef_Employees.md', 'r') as f:
            list_chefs = f.read().splitlines()
        if 'work_shifts' in st.session_state:
            df_tmp = st.session_state['work_shifts']
            chefs = pd.DataFrame({
                'Employee Name': list_chefs,
                'Directed': [0.0 for x in list_chefs]
                })
            chefs = pd.merge(left=chefs, left_on='Employee Name', right=df_tmp, right_on='Employee Name', how='left')
            chefs['Shifts Worked'].fillna(0, inplace=True)
        else:
            chefs = pd.DataFrame(st.session_state['dict'].get(
                'Chef Work Shifts',
                {'Employee Name': list_chefs, 'Shifts Worked': [0 for x in list_chefs], 'Directed': [0.0 for x in list_chefs]}
                ))
        chefs = chefs.sort_values(by=['Employee Name'])
        chefs.reset_index(drop=True, inplace=True)
        chefs = table_color_rows(chefs)
        chefs = col10.data_editor(chefs, column_order=['Employee Name', 'Shifts Worked', 'Directed'], column_config={
            'Employee Name': st.column_config.TextColumn('Chefs Name', disabled=True),
            'Directed': st.column_config.NumberColumn(format='$%.2f')
            }, num_rows='fixed', hide_index=True)
        st.session_state['newdict']['Chef Work Shifts'] = chefs.to_dict()
        if chefs['Shifts Worked'].sum() > 0:
            chefs['Chef Tips'] = round(chefCut * chefs['Shifts Worked']/chefs['Shifts Worked'].sum(), 2)
        else:
            if chefCut > 0:
                col10.warning('Please enter number of shifts worked for each chef so funds can be distributed')
            chefs['Chef Tips'] = 0
        # HELPERS
        helpers = col11.multiselect(
                    "Employees eligible for the Helper Pool",
                    df_tipElligible['Employee Name'].unique(),
                    default=st.session_state['dict'].get('Helpers', None),
                    key='15'
                )
        st.session_state['newdict']['Helpers'] = helpers
        helpers = pd.DataFrame({'Employee Name': helpers})
        if len(helpers) > 0:
            helpers['Helper Tips'] = round(helperPool/len(helpers), 2)
        else:
            if helperPool > 0:
                col11.warning('Please select Employee names so funds can be distributed')
            helpers['Helper Tips'] = 0
        chef_helper = pd.merge(left=chefs, left_on='Employee Name', right=helpers, right_on='Employee Name', how='outer')
        chef_helper['Chef Tips'] = chef_helper['Chef Tips'].fillna(0)
        chef_helper['Directed'] = chef_helper['Directed'].fillna(0)
        chef_helper['Helper Tips'] = chef_helper['Helper Tips'].fillna(0)
        chef_helper = chef_helper.sort_values(by=['Employee Name'])
        chef_helper = table_color_rows(chef_helper)
        chef_helper = chef_helper.format('${:.2f}', subset=['Chef Tips', 'Helper Tips', 'Directed'])
        col12.dataframe(chef_helper, column_order=['Employee Name', 'Directed', 'Chef Tips', 'Helper Tips'], hide_index=True)
    st.subheader('Revise Working Positions')
    with st.container():
        col10, col11 = st.columns([1, 1])
        grouped = df_tipElligible.groupby(['Employee Name', 'Position']).agg({
            'Employee Name': 'first',
            'Position': 'first',
            'Regular': 'sum',
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
        df_tipElligible_adjusted, adj_result = _adjust_work_pos(df_tipElligible)
        if len(adj_result) > 0:
            st.session_state['newdict']['Adjusted Hours'] = adj_result.to_dict()
        else:
            st.session_state['newdict']['Adjusted Hours'] = pd.DataFrame().to_dict()
    st.markdown('---')
    def_splitvalues = [
        st.session_state['dict'].get('Garden FOH', 70),
        st.session_state['dict'].get('Garden Host', 15),
        0,
        st.session_state['dict'].get('Regular FOH', 66),
        0
        ]
    splitvals = _tip_percents('first', def_splitvalues)
    df_tipElligible = _hrs_split(df_tipElligible_adjusted, tip_pool_pos)
    rates = list()
    col40, col41, col42, colspace, col43, col44 = st.columns([1, 1, 1, .5, 1, 1])
    with col40: _tip_info(0, tippingPool_Garden, splitvals, df_tipElligible, rates)
    with col41: _tip_info(1, tippingPool_Garden, splitvals, df_tipElligible, rates)
    with col42: _tip_info(2, tippingPool_Garden, splitvals, df_tipElligible, rates)
    with col43: _tip_info(3, tippingPool_Reg, splitvals, df_tipElligible, rates)
    with col44: _tip_info(4, tippingPool_Reg, splitvals, df_tipElligible, rates)
    st.session_state['newdict']['Garden FOH'] = splitvals[0]
    st.session_state['newdict']['Garden Host'] = splitvals[1]
    st.session_state['newdict']['Regular FOH'] = splitvals[3]
    st.markdown('---')
    # House Tip INPUT DATAFRAME
    col1, col2, col3 = st.columns([3, 5, 4])
    with col1:
        df_house_tips = pd.DataFrame(st.session_state['dict'].get('House Tips'))
        if df_house_tips.empty:
            df_house_tips = pd.DataFrame({})
            df_house_tips['Employee Name'] = df_tipElligible['Employee Name'].unique()
            df_house_tips['House Tip'] = 0.0
        else:
            df_house_tips.reset_index(drop=True, inplace=True)
        df_house_tips = table_color_rows(df_house_tips)
        df_house_tips = st.data_editor(data=df_house_tips, hide_index=True, column_config={
            'Employee Name': st.column_config.TextColumn(disabled=True),
            'House Tip': st.column_config.NumberColumn(format='$%.2f', disabled=False),
        })
        st.session_state['newdict']['House Tips'] = df_house_tips.to_dict()
    with col2:
        df_tipElligible['Tip Rate'] = [pool_rate(x, rates) for x in df_tipElligible['Tip Pool']]
        _df_tips = _add_payroll_summary(df_tipElligible)
        df_tips_agg = _payroll_group_by_tips(_df_tips)
        df_tips_agg = _add_helper_pool(df_tips_agg, helpers)
        df_tips_agg = df_tips_agg.reset_index()
        df_tips_agg = df_tips_agg.drop(['index'], axis=1)
        df_tips_agg = pd.merge(left=df_tips_agg, right=df_house_tips, on=['Employee Name'])
        df_tips_agg['Total Tip'] = df_tips_agg['Garden Tips'] + df_tips_agg['Regular Tips'] + df_tips_agg['Helper Tips']
        df_tips_agg['Assigned Tip %'] = [100*tip/df_tips_agg['Total Tip'].sum() for tip in df_tips_agg['Total Tip']]
        df_tips_agg['Assigned Tip %'] = df_tips_agg['Assigned Tip %'].fillna(0)
        df_tips_agg['House Tip %'] = [100*x/df_tips_agg['House Tip'].sum() for x in df_tips_agg['House Tip']]
        df_tips_agg['House Tip %'] = df_tips_agg['House Tip %'].fillna(0)
        df_tips_agg['% Change'] = round(100*((df_tips_agg['Assigned Tip %'])-df_tips_agg['House Tip %'])/df_tips_agg['House Tip %'], 2)
        df_tips_agg['% Change'] = [x if x != np.inf else 0 for x in df_tips_agg['% Change']]
        df_tips_agg['% Change'] = df_tips_agg['% Change'].fillna(0)
        df_tips_agg_p = df_tips_agg.copy()
        df_tips_agg_p.loc['total'] = df_tips_agg_p[['Hours', 'Garden Tips', 'Regular Tips', 'Helper Tips', 'House Tip', 'Total Tip', 'Assigned Tip %', 'House Tip %']].sum()
        df_tips_agg_p.reset_index(drop=True, inplace=True)
        df_tips_agg_p.loc[df_tips_agg_p.index[-1], 'Employee Name'] = 'Total'
        df_tips_agg_p = table_color_rows(df_tips_agg_p)
        df_tips_agg_p = df_tips_agg_p.format('${:.2f}', subset=['Garden Tips', 'Regular Tips', 'Helper Tips', 'House Tip', 'Total Tip'])
        df_tips_agg_p = df_tips_agg_p.format('{:.0f}%', subset=['Assigned Tip %', 'House Tip %', '% Change'])
        st.dataframe(df_tips_agg_p, hide_index=True, column_order=[
            'Employee Name', 'Hours', 'Garden Tips', 'Regular Tips', 'Helper Tips'], column_config={
                'Hours': st.column_config.NumberColumn(label='Total Hours'),
        })
    with col3:
        df_agg = _payroll_group_by_pos(_df_tips)
        #display_position_summary(df_agg, adj_result)
        df_agg = df_agg.reset_index(drop=True)
        df_agg['Changed'] = [x in list(adj_result['name']) and y in list(adj_result['from']) for x, y in zip(df_agg['Employee Name'], df_agg['Position'])]
        #df_agg_p = table_color_rows(df_agg)
        df_agg_p = table_color_rows(df_agg)
        df_agg_p = df_agg_p.apply(lambda x: [
            "background-color: red" if x['Changed'] and idx == 2
            else ''
            for idx, v in enumerate(x)
            ], axis=1)
        df_agg_p = df_agg_p.format('${:.2f}', subset=['Tip'])
        st.dataframe(df_agg_p, hide_index=True, column_order=['Employee Name', 'Position', 'Hours', 'Tip'])
    st.markdown('---')
    st.dataframe(df_tips_agg_p, hide_index=True, column_order=[
        'Employee Name', 'House Tip', 'House Tip %', 'Total Tip', 'Assigned Tip %', '% Change'], column_config={
            'Assigned Tip %': st.column_config.NumberColumn(label='Total Tip %')
    })
    return df_tips_agg, tippingPool_Garden, tippingPool_Reg, splitvals, df_house_tips, chefs, adj_result


def filter_dataframe(_df: pd.DataFrame) -> pd.DataFrame:
    df = _df.copy()
    with st.container():
        to_filter_columns = ['Employee Name']
        for column in to_filter_columns:
            user_cat_input = st.multiselect(
                f"Choose {column} to Apply Filter",
                df[column].unique()
            )
            if len(user_cat_input) > 0:
                df = df[df[column].isin(user_cat_input)]
    st.dataframe(df, hide_index=True)
    st.write(f"Total Hours: {round(df['Regular'].sum(),2)}, Total Cash Wages: ${round(df['Paid Total'].sum(),2):,}")
    return df


def continue_run(_df):
    if 'dict' not in st.session_state:
        try:
            with open('current_save.csv') as user_file:
                file_contents = user_file.read()
            dict = json.loads(file_contents)
        except Exception:
            dict = {
                'Chef Percent': 18.0,
                'Total Pool': 1567.0,
                'Garden Pool': 450.0,
                'Helper Pool': 75,
                'Num Chefs': 3
                }
        st.session_state['dict'] = dict
    if 'newdict' not in st.session_state:
        st.session_state['newdict'] = st.session_state['dict'].copy()
    _df = _clean_import(_df)
    _df = _combine_FullName(_df)
    tab1, tab2, tab3, tab4 = st.tabs(['Garden Events', 'Tipping Rules', 'Tipping Pool', 'Payroll Summary'])
    with tab1:
        #filter_dataframe(_df)
        gardenEventsPicker()
    with tab2:
        df_tipElligible, tip_pool_pos = _setup_tipping_pools(_df)
    with tab3:
        df_tips_agg, tippingPool_Garden, tippingPool_Reg, splitvals, df_house_tips, df_chefs, adj_result = _tipping_pools(df_tipElligible, tip_pool_pos)
    with tab4:
        display_payroll_summary_House(df_tips_agg, df_chefs, adj_result)
    
    st.markdown('---')
    if st.button('Save All Input Data'):
        save_data()
    return df_tips_agg

def run(file_path: str) -> pd.DataFrame:
    _df = read_csv(file_path)
    return continue_run(_df)
