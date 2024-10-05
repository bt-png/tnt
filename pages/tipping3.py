import streamlit as st
import numpy as np
import pandas as pd
from io import BytesIO
from menu import menu_with_redirect
from style import apply_css
from company import servertipdata
from company import clientGetValue
from sync import syncInput
# from pages.tipping2 import ByPosition
# from pages.tipping2 import TipChangeSummary


def TipChangeSummary():
    # st.caption('Percent Change from House Tip')
    df = st.session_state['tipdata']['df_tipssum'].copy()
    altrows = df['Employee Name'].iloc[1::2]
    df.loc['Employee SubTotal'] = df[[]].sum()
    HoursSum = df['Regular'].sum()
    df.loc[df.index[-1], 'Regular'] = HoursSum
    HouseTipSum = df['House Tip'].sum()
    df.loc[df.index[-1], 'House Tip'] = HouseTipSum
    CalcTipSum = df['Total Tips'].sum()
    df.loc[df.index[-1], 'Total Tips'] = CalcTipSum
    df.loc[df.index[-1], 'CALC Rate/hr'] = CalcTipSum/HoursSum
    df.loc[df.index[-1], '% Change'] = round(100*((CalcTipSum)-HouseTipSum)/HouseTipSum, 2)
    df.loc[df.index[-1], 'Employee Name'] = 'Employee SubTotal'
    
    df['CALC Rate/hr'] = [dollars/hr for dollars, hr in zip(df['Total Tips'], df['Regular'])]
    df['House Tip %'] = [100 * (tip / HouseTipSum) for tip in df['House Tip']]
    df['Total Tips %'] = [100 * (tip / CalcTipSum) for tip in df['Total Tips']]
    df['% Change'] = round(100*((df['Total Tips %'])-df['House Tip %'])/df['House Tip %'], 2)
    
    
    # df.loc['chefs'] = df[[]].sum()
    # df.loc[df.index[-1], 'Employee Name'] = 'Chef Pool'
    # df.loc['chefs', 'Total Tips'] = st.session_state['tipdata']['chefEmployeePool']['Chef Tips'].sum() + st.session_state['tipdata']['chefEmployeePool']['Directed'].sum()

    # df.loc['totals'] = df[[]].sum()
    # df.loc['totals', 'Total Tips'] = df.loc[df.index[-2], 'Total Tips'] + df.loc[df.index[-3], 'Total Tips']
    # df.loc[df.index[-1], 'Employee Name'] = 'Total'
    # column_order=['Employee Name', 'Regular', 'House Tip', 'House Tip %', 'Total Tips', 'Total Tips %', '% Change']
    order = ['Employee Name', 'Regular', 'Total Tips', 'Total Tips %', 'House Tip', 'House Tip %', 'CALC Rate/hr', '% Change']  # df.columns.tolist()
    if df['House Tip'].sum() == 0:
        order.remove('House Tip')
        order.remove('House Tip %')
        order.remove('% Change')
    order.remove('CALC Rate/hr')
    # df['% Change'] = [x if x != np.inf else 0 for x in df['% Change']]
    # df['% Change'] = df['% Change'].fillna(0)
    Height = int(35.2 * (len(df) + 1))
    df.set_index('Employee Name', inplace=True, drop=False)
    df.index.name = None
    df = df.style.format('${:.2f}', subset=['House Tip', 'CALC Rate/hr', 'Total Tips'])
    df = df.format('{:.0f}%', subset=['Total Tips %', 'House Tip %', '% Change'])
    df = df.format('{:.2f}', subset=['Regular'])
    df = df.set_properties(subset = pd.IndexSlice[altrows, :], **{'background-color': '#E3EFF8'})
    df = df.set_properties(subset = pd.IndexSlice[['Employee SubTotal'], :], **{'background-color' : 'lightsteelblue'})
    config = {
        'Employee Name': st.column_config.TextColumn(),
        'Regular': st.column_config.NumberColumn('Total Hours', format='%.2f'),
        # 'House Tip': st.column_config.NumberColumn(format='$%.2f'),
        'Total Tips': st.column_config.NumberColumn('CALC Tips', format='$%.2f'),
        # 'House Tip %': st.column_config.NumberColumn(format='%.2f'),
        'Total Tips %': st.column_config.NumberColumn('CALC Tips %', format='%.2f'),
        }
    # df_tips_agg_p = df_tips_agg_p.format('${:.2f}', subset=['Garden Tips', 'Regular Tips', 'Helper Tips', 'House Tip', 'Total Tip'])
    # df_tips_agg_p = df_tips_agg_p.format('{:.0f}%', subset=['Assigned Tip %', 'House Tip %', '% Change'])
    st.dataframe(df, hide_index=True, column_config=config, column_order=order, height=Height)
    return df


def ByPosition():
    # st.caption('Tips by Position')
    removeNA = False
    df = st.session_state['tipdata']['WorkedHoursDataUsedForTipping'].copy()
    if removeNA:
        df['Tip Pool'] = df['Tip Pool'].replace('Position Not Eligible', None)
    else:
        df['Tip Pool'] = df['Tip Pool'].replace('Position Not Eligible', 'NA')
    df = df.groupby(['Employee Name', 'Position', 'Tip Pool']).agg({
        'Regular': 'sum',
        'Pool Tip': 'sum',
        })
    df.reset_index(inplace=True)
    df.replace(0, np.nan, inplace=True)
    # df.set_index(['Employee Name'], drop=False, inplace=True)
    config = {
        'Employee Name': st.column_config.TextColumn(),
        'Regular': st.column_config.NumberColumn('Total Hours', format='%.2f'),
        'Pool Tip': st.column_config.NumberColumn(format='$%.2f')
        }
    current_list_of_employees = st.session_state['tipdata']['WorkedHoursDataUsedForTipping']['Employee Name'].unique()
    altrows = [i for i in range(0,len(df.index)-1) if i%2!=0]
    Height = int(35.2 * (len(df) + 1))
    df = df.style.format('{:.2f}', subset=['Regular']).format('${:.2f}', subset=['Pool Tip'])
    df = df.set_properties(subset = pd.IndexSlice[altrows, :], **{'background-color': '#E3EFF8'})
    st.dataframe(df, hide_index=True, height=Height,
                 column_order=['Employee Name', 'Position', 'Regular', 'Tip Pool', 'Pool Tip'],
                 column_config=config)
    if removeNA:
        st.caption('Positions where the \'Tip Pool\' is \'Position Not Eligible\' have been removed from this summary.')
    return df


def TipsSum():
    df = st.session_state['tipdata']['WorkedHoursDataUsedForTipping'].copy()
    df = df[df['Tip Pool'] != 'Position Not Eligible']
    df['Pool'] = ['Garden' if ('Garden' in x) else 'Regular' for x in df['Tip Pool']]
    df = df.groupby(['Employee Name', 'Pool']).agg({
        'Regular': 'sum',
        'Garden Tips': 'sum',
        'Regular Tips': 'sum'
        })
    df.reset_index(inplace=True)
    df_reg = df[df['Pool'] == 'Regular']
    df_reg.drop(['Pool', 'Garden Tips'], axis=1, inplace=True)
    df_reg.rename(columns={'Regular': 'Regular Hours'}, inplace=True)
    df_reg['Regular Tip Rate'] = [round(x/y,2) for x, y in zip(df_reg['Regular Tips'], df_reg['Regular Hours'])]
    df_garden = df[df['Pool'] == 'Garden']
    df_garden.drop(['Pool', 'Regular Tips'], axis=1, inplace=True)
    df_garden.rename(columns={'Regular': 'Garden Hours'}, inplace=True)
    df_garden['Garden Tip Rate'] = [round(x/y,2) for x, y in zip(df_garden['Garden Tips'], df_garden['Garden Hours'])]
    # df.set_index(['Employee Name'], inplace=True)
    df = pd.merge(left=df_reg, left_on='Employee Name', right=df_garden, right_on='Employee Name', how='outer')
    # st.dataframe(df)
    # df['Garden Pool Hours'] = [sum(x) for x in ['']]
    # return
    removeNA = False
    # df = st.session_state['tipdata']['WorkedHoursDataUsedForTipping'].copy()
    # df = df.groupby(['Employee Name']).agg({
    #     'Regular': 'sum',
    #     'Garden Tips': 'sum',
    #     'Regular Tips': 'sum'
    #     })
    # # st.dataframe(df)
    # df.reset_index(inplace=True)
    # dfhouse = st.session_state['tipdata']['housetipsforemployees']
    # df = pd.merge(left=df, left_on='Employee Name', right=dfhouse, right_on=['Employee Name'], how='inner')
    dfhelper = st.session_state['tipdata']['Helper Pool Employees']
    HelperPool = st.session_state['tipdata'].get('Helper Pool', 0.0)
    if len(dfhelper) > 0 and HelperPool > 0:
        df['Helper Tips'] = [HelperPool/len(dfhelper) if name in dfhelper['Employee Name'].to_list() else 0 for name in df['Employee Name']]
        # order = ['Employee Name', 'Regular Hours', 'Regular Tips', 'Regular Tips', 'Helper Tips']
    # else:
        # df['Helper Tips'] = 0
        # order = ['Employee Name', 'Regular', 'Garden Tips', 'Regular Tips']
    # df['Total Tips'] = [G + R + H for G, R, H in zip(df['Garden Tips'], df['Regular Tips'], df['Helper Tips'])]
    df.replace(0, np.nan, inplace=True)
    # if removeNA:
    #     df.dropna(subset=['Total Tips'], inplace=True)
    config = {
        'Regular Tips': st.column_config.NumberColumn('Tips'),
        'Regular Tip Rate': st.column_config.NumberColumn('Tip Rate'),
        'Garden Tips': st.column_config.NumberColumn('Tips'),
        'Garden Tip Rate': st.column_config.NumberColumn('Tip Rate'),
        }
    altrows = [i for i in range(0,len(df.index)-1) if i%2!=0]
    df.loc['total'] = df[['Regular Tips', 'Garden Tips']].sum()
    df.loc[df.index[-1], 'Employee Name'] = 'Total'
    # df.set_index(['Employee Name'], drop=True, inplace=True)
    rows = len(df)
    Height = int(35.2 * (rows + 1))
    df = df.style.format('${:.2f}', subset=['Garden Tips', 'Regular Tips', 'Regular Tip Rate', 'Garden Tip Rate'])
    df = df.format('{:.2f}', subset=['Regular Hours', 'Garden Hours'])
    # df = df.set_properties(subset = pd.IndexSlice[['Total'], :], **{'background-color' : 'lightgrey'})
    current_list_of_employees = st.session_state['tipdata']['WorkedHoursDataUsedForTipping']['Employee Name'].unique()
    # Height = int(35.2 * (len(current_list_of_employees) + 1))
    df = df.set_properties(subset = pd.IndexSlice[altrows, :], **{'background-color': '#E3EFF8'})
    df = df.set_properties(subset = pd.IndexSlice[df.index[-1], :], **{'background-color' : 'lightsteelblue'})
    st.dataframe(df, hide_index=True, height=Height, column_config=config)
    if removeNA:
        st.caption('Positions where the \'Tip Pool\' is \'Position Not Eligible\' have been removed from this summary.')


def run():
        # with st.container(height=650):
    if 'tipdata' not in st.session_state:
        st.session_state['tipdata'] = servertipdata()
    col1, col2 = st.columns([8,2])
    col1.header(st.session_state['company'])
    col2.caption('')
    if 'loadedarchive' in st.session_state:
        col2.caption(f'Loaded from Archive: {st.session_state["loadedarchive"]}')
    download = col2.empty()
    
    if 'df_work_hours' in st.session_state['tipdata']:
        if 'WorkedHoursDataUsedForTipping' not in st.session_state['tipdata']:
            st.write('You must first visit the \'Eligibility\' page.')
        else:
            st.markdown('---')
            st.markdown('### Owner Summary')
            col1, col2 = st.columns([5.25, 6])
            with col1:
                st.markdown('#### Staff Summary')
                dfemployeetips = TipChangeSummary()
            with col2:
                col3, col4 = st.columns([4, 3])
                with col3:
                    st.markdown(f"#### Chef Pool - {int(st.session_state['tipdata'].get('Chef Percent', 18))}%")
                    chefpool = st.session_state['tipdata']['Chef Pool']
                    dfchefpool = st.session_state['tipdata']['chefEmployeePool'].copy()
                    dfchefpool['Chef Tips'] = [chefpool * (sh / dfchefpool['Shifts Worked'].sum()) for sh in dfchefpool['Shifts Worked']]
                    dfchefpool['Shifts Worked'] = dfchefpool['Shifts Worked'].fillna(0).astype(int)
                    if dfchefpool['Directed'].sum() > 0:
                        order = ['Employee Name', 'Chef Tips', 'Directed', 'Shifts Worked']
                    else:
                        order = ['Employee Name', 'Chef Tips', 'Shifts Worked']
                    altrows = dfchefpool['Employee Name'].iloc[1::2]
                    dfchefpool.reset_index(inplace=True)
                    dfchefpool.set_index('Employee Name', inplace=True, drop=False)
                    dfchefpool.loc['Total'] = dfchefpool[['Chef Tips', 'Directed', 'Shifts Worked']].sum()
                    dfchefpool.loc[dfchefpool.index[-1], 'Employee Name'] = 'Chef SubTotal'
                    dfchefpool = dfchefpool.style.format('${:.2f}', subset=['Chef Tips', 'Directed'])
                    dfchefpool = dfchefpool.format('{:0.0f}', subset=['Shifts Worked'])
                    dfchefpool = dfchefpool.set_properties(subset = pd.IndexSlice[altrows, :], **{'background-color': '#E3EFF8'})
                    dfchefpool = dfchefpool.set_properties(subset=pd.IndexSlice[['Total'], :], **{'background-color' : 'lightsteelblue'})
                    st.dataframe(dfchefpool, hide_index=True, column_order=order)
                with col4:
                    st.markdown('#### Tip Sources')
                    src = pd.DataFrame({
                        'Name': ['Square Reg', 'Square Garden', 'Venmo/Cash', 'Adjustment (+/-)'],
                        'Total': [
                            st.session_state['tipdata'].get('Raw Pool', 0.0) - st.session_state['tipdata'].get('Base Garden Tip', 0.0),
                            st.session_state['tipdata'].get('Base Garden Tip', 0.0),
                            st.session_state['tipdata'].get('Extra Garden Tip', 0.0),
                            st.session_state['tipdata'].get('Service Charge Adjustment', 0.0)
                            ]
                            })
                    src.loc['total'] = src[['Total']].sum()
                    src.loc[src.index[-1], 'Name'] = 'Total'
                    src.set_index('Name', inplace=True, drop=False)
                    # src.set_index('Name', inplace=True, drop=True)
                    # src.index.name = None
                    src = src.loc[~(src==0).all(axis=1)]
                    altrows = src['Name'].iloc[1::2]
                    src = src.style.format(
                        '${:.2f}', subset=['Total']
                        )
                    src = src.set_properties(subset = pd.IndexSlice[altrows, :], **{'background-color': '#E3EFF8'})
                    src = src.set_properties(subset = pd.IndexSlice[['Total'], :], **{'background-color' : 'lightsteelblue'})
                    st.dataframe(src, hide_index=True)
                col3, col4 = st.columns([4, 3])
                with col3:
                    st.markdown('#### Hourly Rates')
                    breakouts = pd.DataFrame({
                        # 'Total': st.session_state['tipdata']['tippooltotals'],
                        'Rate/hr': st.session_state['tipdata']['tippoolhourlyrates']
                        })
                    # breakouts['% of Total'] = [round(100 * x / breakouts['Total'].sum(),0) for x in breakouts['Total']]
                    breakouts = breakouts.loc[~(breakouts==0).all(axis=1)]
                    breakouts.index.name = 'Pool'
                    breakouts.reset_index('Pool', inplace=True, drop=False)
                    altrows = breakouts.index[1::2]
                    # breakouts.reset_index(inplace=True)
                    # breakouts.loc['Total'] = breakouts[['Total', '% of Total']].sum()
                    # breakouts.loc[breakouts.index[-1], 'Name'] = 'Total'
                    breakouts = breakouts.style.format(
                        '${:.2f}', subset=['Rate/hr']
                        )  # .format('{:.0f}%', subset=['% of Total'])
                    
                    breakouts = breakouts.set_properties(subset = pd.IndexSlice[altrows, :], **{'background-color': '#E3EFF8'})
                    st.dataframe(breakouts, hide_index=True)
                with col4:                
                    st.markdown('#### Pool Split')
                    cuts = pd.DataFrame(st.session_state['tipdata']['tippool'], index=['Total']).transpose()
                    cuts['% of Total'] = [round(100 * x / cuts['Total'].sum(), 0) for x in cuts['Total']]
                    cuts = cuts.loc[~(cuts==0).all(axis=1)]
                    cuts.index.name = 'Pools'
                    cuts.reset_index(drop=False, inplace=True)
                    cuts.set_index('Pools', inplace=True, drop=False)
                    altrows = cuts['Pools'].iloc[1::2]
                    cuts.loc['Total'] = cuts[['Total']].sum()
                    cuts.loc[cuts.index[-1], 'Pools'] = 'Total'
                    # cuts.loc[cuts.index[-1], 'Total'] = 'Total'
                    cuts = cuts.style.format(
                        '${:.2f}', subset=['Total']
                        ).format('{:.0f}%', subset=['% of Total'])
                    
                    cuts = cuts.set_properties(subset = pd.IndexSlice[['Total'], :], **{'background-color' : 'lightsteelblue'})
                    cuts = cuts.set_properties(subset = pd.IndexSlice[altrows, :], **{'background-color': '#E3EFF8'})
                    st.dataframe(cuts, hide_index=True)
            notes = st.text_area(
                'Notes', height=int(35.2 * (5)), 
                value=st.session_state['tipdata'].get('Tipping Notes', ''),
                key='tippingnotes',
                on_change=syncInput, args=('tippingnotes', 'Tipping Notes')
                )
            st.markdown('---')
            # st.markdown('#### Position Tip Pool Eligibility Breakout')
            # dfbyposition = ByPosition()
            st.markdown('#### Position Tip Summary')
            TipsSum()
            st.markdown('---')
            st.markdown('#### Revisions to Work Positions')
            df = pd.DataFrame.empty
            if 'default_possplits_summary' in st.session_state['tipdata']:
                df = st.session_state['tipdata']['default_possplits_summary']
            if 'RevisedWorkPositions' in st.session_state['tipdata']:
                if not df.empty:
                    dfadd = st.session_state['tipdata']['RevisedWorkPositions']
                    df = pd.concat([df, dfadd], ignore_index=True)
                else:
                    df = st.session_state['tipdata']['RevisedWorkPositions']
            config = {
                'name': st.column_config.TextColumn('Employee Name'),
                'hrs': st.column_config.NumberColumn('Move (hrs)'),
                'from': st.column_config.TextColumn('From Old Position'),
                'to': st.column_config.TextColumn('to New Position'),
                'reason': st.column_config.TextColumn('Reason')
                }
            if not df.empty:
                df = df.sort_values(by=['name'])
                altrows = [i for i in range(0,len(df.index)-1) if i%2!=0]
                Height = int(35.2 * (len(df) + 1))
                df = df.style.format('{:.2f}', subset=['hrs'])
                df = df.set_properties(subset = pd.IndexSlice[altrows, :], **{'background-color': '#E3EFF8'})
                st.dataframe(df, column_config=config,
                             hide_index=True, height=Height)
            # DOWNLOAD
            # output = BytesIO()
            # writer = pd.ExcelWriter(output, engine='xlsxwriter')
            # workbook = writer.book
            # worksheet = workbook.add_worksheet('OwnerSummary')
            # writer.sheets['OwnerSummary'] = worksheet
            # runningrow = 0
            # runningcol = 0
            # dfemployeetips.to_excel(writer, sheet_name='OwnerSummary', startrow=runningrow, startcol=runningcol)
            # runningcol += 10
            # dfchefpool.to_excel(writer, sheet_name='OwnerSummary', startrow=runningrow, startcol=runningcol)
            # writer.close()
            # download.download_button(
            #     label='Download', data=output.getvalue(), file_name='tips_OwnerSummary.xlsx')
    else:
        st.write('You must first upload and publish Work Hour Data')


if __name__ == '__main__':
    st.set_page_config(
        page_title='TNT Consulting',
        # page_icon='🚊',
        layout='wide'
    )
    if 'company' not in st.session_state:
        st.switch_page("main.py")
    apply_css()
    run()
    menu_with_redirect()
