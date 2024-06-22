import streamlit as st
import pandas as pd
import numpy as np
from menu import menu_with_redirect
from style import apply_css
from company import publish
from company import servertipdata
from company import clientGetValue
from sync import updated
from sync import syncInput
from sync import syncDataEditor


@st.cache_data
def tippools():
    data = clientGetValue(st.session_state['company'], 'tippools')
    return data


def tipAmounts():
    ukey = 'tipamounts'
    col40, col41, col42 = st.columns([1, 1, 1])
    totalPool = float(
        col40.text_input('#### Total Pool ($)',
                         value=st.session_state['tipdata'].get('Total Pool', 0.01),
                         key=ukey+'1', on_change=syncInput, args=(ukey+'1', 'Total Pool',)))
    # st.session_state['tipdata']['updated_Total Pool'] = totalPool
    tippingPool_Garden = float(
        col41.text_input('#### Base Garden Pool ($)',
                         value=st.session_state['tipdata'].get('Base Garden Tip', 0.00),
                         key=ukey+'3', on_change=syncInput, args=(ukey+'3', 'Base Garden Tip')))
    # st.session_state['tipdata']['updated_Base Garden Tip'] = tippingPool_Garden
    extraGardenTip = st.session_state['tipdata'].get('Extra Garden Tip', 0.00)
    if extraGardenTip > 0:
        col40.caption('Total Pool does not include the additional Garden Tips')
        col41.caption(f"an additional ${format(extraGardenTip,',')} will be distributed with the Base Garden Pool")
    helperPool = float(
        col42.text_input('#### Helper Pool ($)',
                         value=st.session_state['tipdata'].get('Helper Pool', 0.00),
                         key=ukey+'4', on_change=syncInput, args=(ukey+'4', 'Helper Pool')))
    # st.session_state['tipdata']['updated_Helper Pool'] = helperPool
    col40, col41, col42 = st.columns([1, 1, 1])
    remaining = float(col40.text_input('#### Remaining Pool ($)', value=round(totalPool-tippingPool_Garden-helperPool, 2), disabled=True))
    chefPercent = int(
        col41.number_input('#### Chef Percentage (%)',
                           value=st.session_state['tipdata'].get('Chef Percent', 18),
                           key=ukey+'2', on_change=syncInput, args=(ukey+'2', 'Chef Percent')))/100
    # st.session_state['tipdata']['updated_Chef Percent'] = chefPercent*100
    chefPool = float(col41.text_input('#### Total Chef Pool ($)', value=round(remaining * chefPercent, 2), disabled=True))
    st.session_state['tipdata']['Chef Pool'] = chefPool
    tippingPool_Reg = float(col42.text_input('#### Regular Pool ($)', value=round(totalPool - tippingPool_Garden - helperPool - chefPool, 2), key=ukey+'5', disabled=True))
    st.session_state['tipdata']['Regular Pool'] = tippingPool_Reg
    col1, col2 = st.columns([5, 1])
    col1.caption('''
                $Remaining Pool = Total Pool - (Garden Pool + Helper Pool)$  
                ${Chef Cut} = {Remaining Pool} \cdot {Chef Percentage}$  
                ${Regular Pool} = {Remaining Pool} - {Chef Cut}$  
                ''')
    dictionary = {}
    dictionary['Garden'] = tippingPool_Garden+extraGardenTip
    dictionary['Regular'] = remaining
    dictionary['Helper'] = helperPool
    dictionary['Chefs'] = chefPool
    st.session_state['tipdata']['tippool'] = dictionary
    st.session_state['tipdata']['tiptotals'] = totalPool + extraGardenTip


def tipPercents():
    ukey = 'tippools'
    # if 'tippoolpercents' not in st.session_state['tipdata']:
    split_vals = [70, 15, None, 66, None]  # Update to read from Company Defaults
    #     dictionary = dict(zip(tippools(), split_vals))
    st.session_state['tipdata']['tippool_g1'] = split_vals[0]
    st.session_state['tipdata']['tippool_g2'] = split_vals[1]
    st.session_state['tipdata']['tippool_f1'] = split_vals[3]
    vals = list()
    col40, col41, col42, colspace, col43, col44 = st.columns([1, 1, 1, .5, 1, 1])
    col40.markdown('#### ' + tippools()[0])
    col41.markdown('#### ' + tippools()[1])
    col42.markdown('#### ' + tippools()[2])
    col43.markdown('#### ' + tippools()[3])
    col44.markdown('#### ' + tippools()[4])
    vals.append(col40.number_input(
        label=tippools()[0], step=1, value=int(st.session_state['tipdata']['tippool_g1']),
        key=ukey+'g1', label_visibility='collapsed', on_change=syncInput, args=(ukey+'g1', 'tippool_g1'))
        )
    vals.append(col41.number_input(
        label=tippools()[1], step=1, value=int(st.session_state['tipdata']['tippool_g2']),
        key=ukey+'g2', label_visibility='collapsed', on_change=syncInput, args=(ukey+'g2', 'tippool_g2'))
        )
    vals.append(float(col42.text_input(
        label=tippools()[2], value=str(100-vals[0]-vals[1]), key=ukey+'g3',
        disabled=True, label_visibility='collapsed'))
        )
    vals.append(col43.number_input(
        label=tippools()[3], step=1, value=int(st.session_state['tipdata']['tippool_f1']),
        key=ukey+'f1', label_visibility='collapsed', on_change=syncInput, args=(ukey+'f1', 'tippool_f1'))
        )
    vals.append(float(col44.text_input(
        label=tippools()[4], value=str(100-vals[3]), key=ukey+'b2',
        disabled=True, label_visibility='collapsed'))
        )
    # dictionary = dict(zip(tippools(), vals))
    # if dictionary != st.session_state['tipdata']['tippoolpercents']:
    #     updated()
    # st.session_state['tipdata']['tippoolpercents'] = dictionary
    gardenpool = st.session_state['tipdata']['tippool']['Garden']
    regularpool = st.session_state['tipdata']['tippool']['Regular']
    gardensplit = [
        round(gardenpool * vals[0]/100, 2),
        round(gardenpool * vals[1]/100, 2)
                ]
    gardensplit.append(round(gardenpool-sum(gardensplit), 2))
    regularsplit = [round(regularpool * vals[3]/100, 2)]
    regularsplit.append(round(regularpool-sum(regularsplit), 2))
    result = gardensplit + regularsplit
    dictionary = dict(zip(tippools(), result))
    st.session_state['tipdata']['tippooltotals'] = dictionary


def tipPoolSumHRS():
    df = st.session_state['tipdata']['WorkedHoursDataUsedForTipping']
    dictionary = {}
    for pool in tippools():
        dictionary[pool] = df[df['Tip Pool'] == pool]['Regular'].sum()
    st.session_state['tipdata']['tippoolsumhrs'] = dictionary


def position_to_pool(position: str):
    # if 'Available Work Positions' in st.session_state['tipdata']:
    #     data = st.session_state['tipdata']['Available Work Positions']
    if 'position_pool' in st.session_state['tipdata']:
        data = st.session_state['tipdata']['position_pool']
    else:
        data = clientGetValue(st.session_state['company'], 'tipposition')
    if position in data['Position']:
        idx = data['Position'].index(position)
        pospool = data['Tip Pool'][idx]
        pool = tippools()[pospool]
    else:
        pool = 'Position Not Elligible'
    return pool


def tipHrsSplit(_df: pd.DataFrame):
    # No need to return a df as the actions are done inplace
    # df = st.session_state['tipdata']['WorkedHoursDataUsedForTipping']
    if 'Tip Pool' in _df:
        _df.drop('Tip Pool', axis=1, inplace=True)
    _df.insert(0, 'Tip Pool', [position_to_pool(x) for x in _df['Position']])


def tipPoolPositions():
    df = pd.DataFrame({'Position': st.session_state['tipdata']['Available Work Positions']})
    tipHrsSplit(df)
    st.markdown('#### Tipping Positions')
    edited_data = st.data_editor(df, num_rows='fixed', hide_index=True, column_config={
        'Tip Pool': st.column_config.SelectboxColumn(options=tippools()),
        'Position': st.column_config.TextColumn(disabled=True)
    })
    # syncDataEditor(edited_data, 'position_pool')
    pospool = edited_data[edited_data['Tip Pool'] != 'Position Not Elligible']
    pospool.reset_index(drop=True, inplace=True)
    pool = [tippools().index(x) for x in pospool['Tip Pool']]
    pos = pospool['Position'].to_list()
    dictionary = {'Tip Pool': pool, 'Position': pos}
    # default = clientGetValue(st.session_state['company'], 'tipposition')
    # st.write(default)
    # dictionary = dict(zip(dictionary, clientGetValue(st.session_state['company'], 'tipposition')))
    if not edited_data.equals(df):
        updated()
        st.session_state['tipdata']['position_pool'] = dictionary
    # st.write(pool + default['Tip Pool'])


def helperPool():
    # st.markdown('#### Helper Pool Employees')
    if 'helperEmployeeNamepool' not in st.session_state['tipdata']:
        st.session_state['tipdata']['helperEmployeeNamepool'] = []
    pool = st.multiselect(
                    "#### Helper Pool Employees",
                    st.session_state['tipdata']['Tip Elligible Employees'],
                    default=st.session_state['tipdata']['helperEmployeeNamepool'], placeholder='Select Employees to add to the Helper Pool',
                    key='helperpoolemployees', on_change=syncInput, args=('helperpoolemployees', 'helperEmployeeNamepool')
                )
    if 'Helper Pool Employees' in st.session_state['tipdata']:
        df = st.session_state['tipdata']['Helper Pool Employees']
        for idx, row in df.iterrows():
            if row['Employee Name'] not in pool:
                df.drop(idx, inplace=True)
        for name in pool:
            if name not in df['Employee Name'].to_list():
                df.loc[len(df.index)] = [name, True]
    else:
        df = pd.DataFrame({
            'Employee Name': pool,
            'Remain in Tip Pool': [True for x in pool]
            })
    st.session_state['tipdata']['Helper Pool Employees'] = df.copy()
    if len(st.session_state['tipdata']['Helper Pool Employees']) > 0:
        st.write('')
        edited_data = st.data_editor(st.session_state['tipdata']['Helper Pool Employees'], hide_index=True, num_rows='fixed', column_config={
                'Employee Name': st.column_config.TextColumn(disabled=True),
                'Remain in Tip Pool': st.column_config.CheckboxColumn()
                }
            )
        syncDataEditor(edited_data, 'Helper Pool Employees')


def removeHelperPools():
    df_hrs = st.session_state['tipdata']['WorkedHoursDataUsedForTipping']
    if 'updated_Helper Pool Employees' in st.session_state['tipdata']:
        removeHelpers = st.session_state['tipdata']['updated_Helper Pool Employees']
    else:
        removeHelpers = st.session_state['tipdata']['Helper Pool Employees']
    if len(removeHelpers) > 0:
        removeHelpers = removeHelpers[~removeHelpers['Remain in Tip Pool']]['Employee Name'].to_list()
        if len(removeHelpers) > 0:
            # for idx, row in df_hrs.iterrows():
            #     if row['Employee Name'] in removeHelpers:
            #         df_hrs.drop(idx, inplace=True)
            for name in removeHelpers:
                df_hrs.drop(df_hrs.index[df_hrs['Employee Name'] == name], inplace=True)
            # st.session_state['tipdata']['WorkedHoursDataUsedForTipping'] = df_hrs
            syncDataEditor(df_hrs, 'WorkedHoursDataUsedForTipping')


def applyColumnSort(_df: pd.DataFrame, sort: list) -> pd.DataFrame:
    new_columns = sort + (_df.columns.drop(sort).tolist())
    _df = _df[new_columns]
    return _df


def tipDisplayInfo(idx, rates):
    df_hrs = st.session_state['tipdata']['WorkedHoursDataUsedForTipping']
    poolname = tippools()[idx]
    total = st.session_state['tipdata']['tippooltotals'][poolname]
    emp_count = df_hrs[df_hrs['Tip Pool'] == poolname]['Employee Name'].unique()
    if len(df_hrs.index) == 0:
        str = 'No Entries'
        hrs = 0
        rate = 0
    else:
        hrs = df_hrs[df_hrs['Tip Pool'] == poolname]['Regular'].sum()
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


def tipDisplaySummary():
    rates = []
    col40, col41, col42, colspace, col43, col44 = st.columns([1, 1, 1, .5, 1, 1])
    with col40: tipDisplayInfo(0, rates)
    with col41: tipDisplayInfo(1, rates)
    with col42: tipDisplayInfo(2, rates)
    with col43: tipDisplayInfo(3, rates)
    with col44: tipDisplayInfo(4, rates)
    dictionary = dict(zip(tippools(), rates))
    st.session_state['tipdata']['tippoolhourlyrates'] = dictionary


def tipPercentsSummary():
    rerun = True if 'tippoolhourlyrates' not in st.session_state['tipdata'] else False
    tipPercents()
    tipPoolSumHRS()
    tipDisplaySummary()
    if rerun:
        st.rerun()
    if st.session_state['updatedsomething']:
        st.caption('You may need to \'Publish\' for updates to reflect in the splits.')


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


def applyDefaultSplits():
    if 'updated_RevisedDefaultWorkPositions' in st.session_state['tipdata']:
        data = st.session_state['tipdata']['updated_RevisedDefaultWorkPositions']
    elif 'RevisedDefaultWorkPositions' in st.session_state['tipdata']:
        data = st.session_state['tipdata']['RevisedDefaultWorkPositions']
    else:
        data = pd.DataFrame.from_dict(clientGetValue(st.session_state['company'], 'positionsplits'))
    df_revised = st.session_state['tipdata']['ORIGINAL_WorkedHoursDataUsedForTipping'].copy()
    if len(data) > 0:
        df_app = df_revised[df_revised['Position'].isin(data['from'])][['Employee Name', 'Regular', 'Position']]
        df_revised['reason'] = ''
        df_add = applysplits(df_app, data)
        archive = df_add.copy()
        archive = archive.rename(columns={'Employee Name': 'name', 'Regular': 'hrs', 'Position': 'from', 'New Position': 'to'})
        archive.reset_index(drop=True, inplace=True)
        st.session_state['tipdata']['default_possplits_summary'] = archive
        df_remove = df_add.copy()
        df_add['Position'] = df_add['New Position']
        df_add = df_add.drop(columns=['New Position'])
        df_remove['Regular'] = -df_remove['Regular']
        df_remove = df_remove.drop(columns=['New Position'])
        df_revised = pd.concat([df_revised, df_add, df_remove], ignore_index=True)
    tipHrsSplit(df_revised)
    st.session_state['tipdata']['DEFAULT_WorkedHoursDataUsedForTipping'] = df_revised.copy()
    return


def reviseDefaultSplits():
    st.caption('Default Splits for Working Shifts')
    positions = st.session_state['tipdata']['Available Work Positions']
    if 'RevisedDefaultWorkPositions' not in st.session_state['tipdata']:
        data = pd.DataFrame.from_dict(clientGetValue(st.session_state['company'], 'positionsplits'))
        st.session_state['tipdata']['RevisedDefaultWorkPositions'] = data
    config = {
        'from': st.column_config.SelectboxColumn('From Old Position', width='medium', options=positions, required=True),
        'to': st.column_config.SelectboxColumn('to New Position', width='medium', options=positions, required=True),
        'perc': st.column_config.NumberColumn('Apply Percentage to Worked hrs (%)', required=True),
        'reason': st.column_config.TextColumn('Reason', width='large', required=True, default='Assigned Split Shifts')
    }
    edited_data = st.data_editor(
        st.session_state['tipdata']['RevisedDefaultWorkPositions'],
        column_config=config, num_rows='dynamic', hide_index=True)
    # edited_data = edited_data.dropna()
    edited_data.reset_index(drop=True, inplace=True)
    syncDataEditor(edited_data, 'RevisedDefaultWorkPositions')
    # if not edited_data.equals(st.session_state['tipdata']['RevisedDefaultWorkPositions']):
    #     updated()
    #     st.session_state['tipdata']['updated_RevisedDefaultWorkPositions'] = edited_data


def revisePositionsWorked():
    st.caption('Revise Individual Working Shift Positions')
    df = st.session_state['tipdata']['DEFAULT_WorkedHoursDataUsedForTipping'].copy()
    if 'RevisedWorkPositions' not in st.session_state['tipdata']:
        tmpdf = pd.DataFrame(columns=['name', 'hrs', 'from', 'to', 'reason'])
        tmpdf.reset_index(drop=True, inplace=True)
        st.session_state['tipdata']['RevisedWorkPositions'] = tmpdf.copy()
    employees = df['Employee Name'].unique().tolist()
    positions = st.session_state['tipdata']['Available Work Positions']
    # st.write(employees)
    # st.write(positions)
    # employees = df['Employee Name'].unique().tolist()
    # positions = st.session_state['tipdata']['Available Work Positions']
    # st.dataframe(st.session_state['tipdata']['RevisedWorkPositions'])
    config = {
        'name': st.column_config.SelectboxColumn('Employee Name', width='medium', required=True, options=employees),
        'hrs': st.column_config.NumberColumn('Move (hrs)', required=True, width='medium'),
        'from': st.column_config.SelectboxColumn('From Old Position', width='medium', options=positions, required=True),
        'to': st.column_config.SelectboxColumn('to New Position', width='medium', options=positions, required=True),
        'reason': st.column_config.TextColumn('Reason', width='large', required=True, default='split shift'),
    }
    edited_data = st.data_editor(
        st.session_state['tipdata']['RevisedWorkPositions'],
        column_config=config, num_rows='dynamic', hide_index=True)
    edited_data.reset_index(drop=True, inplace=True)
    # if not edited_data.equals(st.session_state['tipdata']['RevisedWorkPositions']):
    #     updated()
    #     st.session_state['tipdata']['updated_RevisedWorkPositions'] = edited_data
    syncDataEditor(edited_data, 'RevisedWorkPositions')
    # # st.session_state['newdict']['Work Position Revisions'] = result.to_dict()
    df_add = pd.DataFrame({'Employee Name': edited_data['name'], 'Regular': edited_data['hrs'], 'Position': edited_data['to'], 'reason': edited_data['reason']})
    df_remove = pd.DataFrame({'Employee Name': edited_data['name'], 'Regular': -edited_data['hrs'], 'Position': edited_data['from'], 'reason': edited_data['reason']})
    df_revised = pd.concat([df_add, df_remove], ignore_index=True).copy()
    # st.session_state['tipdata']['ALL_RevisedWorkPositions'] = df_revised
    syncDataEditor(df_revised, 'ALL_RevisedWorkPositions')
    df_combined = pd.concat([df, df_revised], ignore_index=True).copy()
    tipHrsSplit(df_combined)
    df_combined = applyColumnSort(df_combined, ['Tip Pool', 'Employee Name', 'Regular', 'Position'])
    st.session_state['tipdata']['WorkedHoursDataUsedForTipping'] = df_combined
    # st.dataframe(st.session_state['tipdata']['WorkedHoursDataUsedForTipping'])


def filter_WorkdedHoursDataUsedForTipping():
    ogrouped = st.session_state['tipdata']['DEFAULT_WorkedHoursDataUsedForTipping'].groupby(['Employee Name', 'Position']).agg({
        'Employee Name': 'first',
        'Position': 'first',
        'Tip Pool': 'first',
        'Regular': 'sum',
        })
    grouped = st.session_state['tipdata']['WorkedHoursDataUsedForTipping'].groupby(['Employee Name', 'Position']).agg({
        'Employee Name': 'first',
        'Position': 'first',
        'Tip Pool': 'first',
        'Regular': 'sum',
        })
    col1, col2, col3 = st.columns([1, 2, 2])
    col2.caption('Default Splits Applied')
    if not ogrouped.equals(grouped):
        col3.caption('Revised Worked Shifts (includes default splits)')
    col1, col2, col3 = st.columns([2, 5, 5])
    user_cat_input = col1.multiselect(
        f"Choose 'Employee Name' to Apply Filter",
        ogrouped['Employee Name'].unique()
        )
    if len(user_cat_input) > 0:
        ogrouped = ogrouped[ogrouped['Employee Name'].isin(user_cat_input)]
        grouped = grouped[grouped['Employee Name'].isin(user_cat_input)]
    col2.dataframe(ogrouped, hide_index=True, height=250, column_config={
        'Employee Name': st.column_config.TextColumn(),
        'Position': st.column_config.TextColumn(),
        'Tip Pool': st.column_config.TextColumn(),
        'Regular': st.column_config.NumberColumn(label='Hours'),
        })
    if not ogrouped.equals(grouped):
        col3.dataframe(grouped, hide_index=True, height=250, column_config={
            'Employee Name': st.column_config.TextColumn(),
            'Position': st.column_config.TextColumn(),
            'Tip Pool': st.column_config.TextColumn(),
            'Regular': st.column_config.NumberColumn(label='Hours'),
            })
        col3.caption('The Revised table is utilized for tipping Pools')


def HouseTip():
    st.caption('House Tip')
    if 'housetipsforemployees' not in st.session_state['tipdata']:
        df = pd.DataFrame({'Employee Name': st.session_state['tipdata']['Employees Worked']})
        df['House Tip'] = 0.0
        st.session_state['tipdata']['housetipsforemployees'] = df.copy()
    df = st.session_state['tipdata']['housetipsforemployees'].copy()
    current_list_of_employees = st.session_state['tipdata']['WorkedHoursDataUsedForTipping']['Employee Name'].unique()
    edited_data = st.data_editor(
        st.session_state['tipdata']['housetipsforemployees'][st.session_state['tipdata']['housetipsforemployees']['Employee Name'].isin(current_list_of_employees)],
        hide_index=True, num_rows='fixed',
        column_config={
            'Employee Name': st.column_config.TextColumn(disabled=True),
            'House Tip': st.column_config.NumberColumn(format='$%.2f')
        }
        )
    df.update(edited_data)
    syncDataEditor(df, 'housetipsforemployees')


def TipsSum():
    # st.caption('Employee Tips Summary')
    removeNA = False
    df = st.session_state['tipdata']['WorkedHoursDataUsedForTipping'].copy()
    df = df.groupby(['Employee Name']).agg({
        'Regular': 'sum',
        'Garden Tips': 'sum',
        'Regular Tips': 'sum'
        })
    df.reset_index(inplace=True)
    dfhouse = st.session_state['tipdata']['housetipsforemployees']
    df = pd.merge(left=df, left_on='Employee Name', right=dfhouse, right_on=['Employee Name'], how='inner')
    dfhelper = st.session_state['tipdata']['Helper Pool Employees']
    HelperPool = st.session_state['tipdata']['tippool']['Helper']
    if len(dfhelper) > 0 and HelperPool > 0:
        df['Helper Tips'] = [HelperPool/len(dfhelper) if name in dfhelper['Employee Name'].to_list() else 0 for name in df['Employee Name']]
    else:
        df['Helper Tips'] = 0
    df['Total Tips'] = [G + R + H for G, R, H in zip(df['Garden Tips'], df['Regular Tips'], df['Helper Tips'])]
    df.replace(0, np.nan, inplace=True)
    if removeNA:
        df.dropna(subset=['Total Tips'], inplace=True)
    config = {
        'Employee Name': st.column_config.TextColumn(),
        'Regular': st.column_config.NumberColumn('Total Hours', format='%.2f'),
        'Garden Tips': st.column_config.NumberColumn(format='$%.2f'),
        'Regular Tips': st.column_config.NumberColumn(format='$%.2f'),
        'House Tip': st.column_config.NumberColumn(format='$%.2f'),
        'Helper Tips': st.column_config.NumberColumn(format='$%.2f'),
        }
    df.loc['total'] = df[['Regular', 'Garden Tips', 'Regular Tips', 'Helper Tips']].sum()
    df.loc[df.index[-1], 'Employee Name'] = 'Total'
    st.session_state['tipdata']['df_tipssum'] = df.copy()
    df.set_index(['Employee Name'], drop=True, inplace=True)
    st.dataframe(df, hide_index=True,
                 column_order=['Employee Name', 'Regular', 'Garden Tips', 'Regular Tips', 'Helper Tips'],
                 column_config=config)
    if removeNA:
        st.caption('Positions where the \'Tip Pool\' is \'Position Not Elligible\' have been removed from this summary.')


def ByPosition():
    # st.caption('Tips by Position')
    removeNA = False
    df = st.session_state['tipdata']['WorkedHoursDataUsedForTipping'].copy()
    if removeNA:
        df['Tip Pool'] = df['Tip Pool'].replace('Position Not Elligible', None)
    else:
        df['Tip Pool'] = df['Tip Pool'].replace('Position Not Elligible', 'NA')
    df = df.groupby(['Employee Name', 'Position', 'Tip Pool']).agg({
        'Regular': 'sum',
        'Pool Tip': 'sum',
        })
    df.reset_index(inplace=True)
    df.replace(0, np.nan, inplace=True)
    df.set_index(['Employee Name'], drop=True, inplace=True)
    config = {
        'Employee Name': st.column_config.TextColumn(),
        'Regular': st.column_config.NumberColumn('Total Hours', format='%.2f'),
        'Pool Tip': st.column_config.NumberColumn(format='$%.2f')
        }
    st.dataframe(df, hide_index=True,
                 column_order=['Employee Name', 'Position', 'Regular', 'Tip Pool', 'Pool Tip'],
                 column_config=config)
    if removeNA:
        st.caption('Positions where the \'Tip Pool\' is \'Position Not Elligible\' have been removed from this summary.')


def TipChangeSummary():
    # st.caption('Percent Change from House Tip')
    df = st.session_state['tipdata']['df_tipssum'].copy()
    HouseTipSum = df['House Tip'].sum()
    df.loc[df.index[-1], 'House Tip'] = HouseTipSum
    CalcTipSum = df['Total Tips'].sum()
    df.loc[df.index[-1], 'Total Tips'] = CalcTipSum
    df['House Tip %'] = [100 * (tip / HouseTipSum) for tip in df['House Tip']]
    df['Total Tips %'] = [100 * (tip / CalcTipSum) for tip in df['Total Tips']]
    df['% Change'] = round(100*((df['Total Tips %'])-df['House Tip %'])/df['House Tip %'], 2)
    df.loc[df.index[-1], '% Change'] = round(100*((CalcTipSum)-HouseTipSum)/HouseTipSum, 2)
    # df['% Change'] = [x if x != np.inf else 0 for x in df['% Change']]
    # df['% Change'] = df['% Change'].fillna(0)
    df = df.style.format('${:.2f}', subset=['Garden Tips', 'Regular Tips', 'Helper Tips', 'House Tip', 'Total Tips'])
    df = df.format('{:.0f}%', subset=['Total Tips %', 'House Tip %', '% Change'])
    df = df.format('{:.2f}', subset=['Regular'])
    config = {
        'Employee Name': st.column_config.TextColumn(),
        'Regular': st.column_config.NumberColumn('Total Hours', format='%.2f'),
        # 'House Tip': st.column_config.NumberColumn(format='$%.2f'),
        # 'Total Tips': st.column_config.NumberColumn(format='$%.2f'),
        # 'House Tip %': st.column_config.NumberColumn(format='%.2f'),
        # 'Total Tips %': st.column_config.NumberColumn(format='%.2f'),
        }
    # df_tips_agg_p = df_tips_agg_p.format('${:.2f}', subset=['Garden Tips', 'Regular Tips', 'Helper Tips', 'House Tip', 'Total Tip'])
    # df_tips_agg_p = df_tips_agg_p.format('{:.0f}%', subset=['Assigned Tip %', 'House Tip %', '% Change'])
    st.dataframe(df, hide_index=True, column_config=config,
                 column_order=['Employee Name', 'Regular', 'House Tip', 'House Tip %', 'Total Tips', 'Total Tips %', '% Change']
                )


def applyTipRatestoHoursWorked():
    if 'tippoolhourlyrates' in st.session_state['tipdata']:
        tiprates = st.session_state['tipdata']['tippoolhourlyrates']
    else:
        tiprates = dict(zip(tippools(), [0, 0, 0, 0, 0]))  # {"Garden FOH": 0, "Garden Host": 0, "Garden BOH": 0, "FOH": 11.765217391304349, "BOH": 0}
    if 'updated_WorkedHoursDataUsedForTipping' in st.session_state:
        st.warning('Table is being udpated elsewhere')
    df = st.session_state['tipdata']['WorkedHoursDataUsedForTipping']
    if 'Tip Pool Rate' in df:
        df.drop('Tip Pool Rate', axis=1, inplace=True)
        df.drop('Pool Tip', axis=1, inplace=True)
        df.drop('Regular Tips', axis=1, inplace=True)
        df.drop('Garden Tips', axis=1, inplace=True)
    df.insert(4, 'Tip Pool Rate', [tiprates[pool] if pool != 'Position Not Elligible' else 0 for pool in df['Tip Pool']])
    df.insert(4, 'Pool Tip', [rate * hrs for rate, hrs in zip(df['Tip Pool Rate'], df['Regular'])])
    df.insert(4, 'Regular Tips', [tip if (pool in tippools()[3:5]) else 0 for tip, pool in zip(df['Pool Tip'], df['Tip Pool'])])
    df.insert(4, 'Garden Tips', [tip if (pool in tippools()[0:3]) else 0 for tip, pool in zip(df['Pool Tip'], df['Tip Pool'])])
    # df.insert(4, 'Regular Tips', [df[(df['Employee Name'] == x) & (df['Tip Pool'].isin(tippools()[3:5]))]['Pool Tip'].sum() for x in df['Employee Name']])
    # df.insert(4, 'Garden Tips', [df[(df['Employee Name'] == x) & (df['Tip Pool'].isin(tippools()[0:3]))]['Pool Tip'].sum() for x in df['Employee Name']])
    st.session_state['tipdata']['WorkedHoursDataUsedForTipping'] = df.copy()


def run():
    # with st.container(height=650):
    if 'tipdata' not in st.session_state:
        st.session_state['tipdata'] = servertipdata()
    col1, col2 = st.columns([8, 2])
    with col1:
        st.header(st.session_state['company'])
    with col2:
        st.caption('')
        publishbutton = st.empty()
    if 'df_work_hours' in st.session_state['tipdata']:
        if 'ORIGINAL_WorkedHoursDataUsedForTipping' not in st.session_state['tipdata']:
            st.write('You must first visit the \'Eligibility\' page.')
        else:
            st.markdown('---')
            st.markdown('### Tip Pools & Distribution Percentages')
            tipAmounts()
            st.markdown('---')
            col1, col2 = st.columns([1, 1])
            with col1:
                tipPoolPositions()
            with col2:
                helperPool()
            st.markdown('---')
            tipsummary_container = st.container()
            st.markdown('---')
            st.markdown('### Revise Working')
            reviseDefaultSplits()
            applyDefaultSplits()
            revisePositionsWorked()
            removeHelperPools()
            # applyDefaultSplits()
            filter_WorkdedHoursDataUsedForTipping()
            st.markdown('---')
            st.markdown('### Tip Pool Distribution')
            applyTipRatestoHoursWorked()
            col1, col2, col3 = st.columns([2, 4, 5])
            with col1:
                HouseTip()
            with col2:
                st.caption('Employee Tips Summary')
                TipsSum()
            with col3:
                st.caption('Tips by Position')
                ByPosition()
            st.caption('Percent Change from House Tip')
            TipChangeSummary()
            st.markdown('---')
            with tipsummary_container:
                # this needs to be last item so it can sum up all the changes from above
                tipPercentsSummary()
            if st.session_state['updatedsomething']:
                if publishbutton.button('Publish Data', key='fromtipping0'):
                    publish()
    else:
        st.write('You must first upload and publish Work Hour Data')


if __name__ == '__main__':
    st.set_page_config(
        page_title='TNT Consulting',
        # page_icon='🚊',
        layout='wide'
    )
    if 'company' not in st.session_state:
        st.switch_page("app.py")
    apply_css()
    run()
    menu_with_redirect()
