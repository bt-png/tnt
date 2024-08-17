import streamlit as st
import pandas as pd
from menu import menu_with_redirect
from style import apply_css
from company import servertipdata
from pages.tipping2 import ByPosition
from sync import syncInput
# from pages.tipping2 import TipChangeSummary


def TipChangeSummary():
    # st.caption('Percent Change from House Tip')
    df = st.session_state['tipdata']['df_tipssum'].copy()
    HouseTipSum = df['House Tip'].sum()
    df.loc[df.index[-1], 'House Tip'] = HouseTipSum
    CalcTipSum = df['Total Tips'].sum()
    df.loc[df.index[-1], 'Total Tips'] = CalcTipSum
    df['CALC Rate/hr'] = [dollars/hr for dollars, hr in zip(df['Total Tips'], df['Regular'])]
    df['House Tip %'] = [100 * (tip / HouseTipSum) for tip in df['House Tip']]
    df['Total Tips %'] = [100 * (tip / CalcTipSum) for tip in df['Total Tips']]
    df['% Change'] = round(100*((df['Total Tips %'])-df['House Tip %'])/df['House Tip %'], 2)
    df.loc[df.index[-1], '% Change'] = round(100*((CalcTipSum)-HouseTipSum)/HouseTipSum, 2)
    df.loc[df.index[-1], 'CALC Rate/hr'] = None
    df.loc[df.index[-1], 'Employee Name'] = 'Employee SubTotal'
    
    # df.loc['chefs'] = df[[]].sum()
    # df.loc[df.index[-1], 'Employee Name'] = 'Chef Pool'
    # df.loc['chefs', 'Total Tips'] = st.session_state['tipdata']['chefEmployeePool']['Chef Tips'].sum() + st.session_state['tipdata']['chefEmployeePool']['Directed'].sum()

    # df.loc['totals'] = df[[]].sum()
    # df.loc['totals', 'Total Tips'] = df.loc[df.index[-2], 'Total Tips'] + df.loc[df.index[-3], 'Total Tips']
    # df.loc[df.index[-1], 'Employee Name'] = 'Total'
    # column_order=['Employee Name', 'Regular', 'House Tip', 'House Tip %', 'Total Tips', 'Total Tips %', '% Change']
    order = ['Employee Name', 'Regular', 'House Tip', 'House Tip %', 'CALC Rate/hr', 'Total Tips', 'Total Tips %', '% Change']  # df.columns.tolist()
    if df['House Tip'].sum() == 0:
        order.remove('House Tip')
        order.remove('House Tip %')
        order.remove('% Change')
    # df['% Change'] = [x if x != np.inf else 0 for x in df['% Change']]
    # df['% Change'] = df['% Change'].fillna(0)
    Height = int(35.2 * (len(df) + 1))
    df.set_index('Employee Name', inplace=True, drop=False)
    df.index.name = None
    df = df.style.format('${:.2f}', subset=['House Tip', 'CALC Rate/hr', 'Total Tips'])
    df = df.format('{:.0f}%', subset=['Total Tips %', 'House Tip %', '% Change'])
    df = df.format('{:.2f}', subset=['Regular'])
    df = df.set_properties(subset = pd.IndexSlice[['Employee SubTotal'], :], **{'background-color' : 'lightgrey'})
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


def run():
        # with st.container(height=650):
    if 'tipdata' not in st.session_state:
        st.session_state['tipdata'] = servertipdata()
    st.header(st.session_state['company'])
    if 'df_work_hours' in st.session_state['tipdata']:
        if 'WorkedHoursDataUsedForTipping' not in st.session_state['tipdata']:
            st.write('You must first visit the \'Eligibility\' page.')
        else:
            st.markdown('---')
            st.markdown('### Owner Summary')
            col1, col2 = st.columns([5.25, 6])
            with col1:
                st.markdown('#### Staff Summary')
                TipChangeSummary()
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
                    dfchefpool.loc['Total'] = dfchefpool[['Chef Tips', 'Directed', 'Shifts Worked']].sum()
                    dfchefpool.loc[dfchefpool.index[-1], 'Employee Name'] = 'Chef SubTotal'
                    dfchefpool = dfchefpool.style.format('${:.2f}', subset=['Chef Tips', 'Directed'])
                    dfchefpool = dfchefpool.format('{:0.0f}', subset=['Shifts Worked'])
                    dfchefpool = dfchefpool.set_properties(subset=pd.IndexSlice[['Total'], :], **{'background-color' : 'lightgrey'})
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
                    # src.set_index('Name', inplace=True, drop=True)
                    # src.index.name = None
                    src = src.loc[~(src==0).all(axis=1)]
                    src = src.style.format(
                        '${:.2f}', subset=['Total']
                        )
                    src = src.set_properties(subset = pd.IndexSlice[['total'], :], **{'background-color' : 'lightgrey'})
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
                    # breakouts.loc['Total'] = breakouts[['Total', '% of Total']].sum()
                    # breakouts.loc[breakouts.index[-1], 'Name'] = 'Total'
                    breakouts = breakouts.style.format(
                        '${:.2f}', subset=['Rate/hr']
                        )  # .format('{:.0f}%', subset=['% of Total'])
                    st.dataframe(breakouts)
                with col4:                
                    st.markdown('#### Pool Split')
                    cuts = pd.DataFrame(st.session_state['tipdata']['tippool'], index=['Total']).transpose()
                    cuts['% of Total'] = [round(100 * x / cuts['Total'].sum(), 0) for x in cuts['Total']]
                    cuts = cuts.loc[~(cuts==0).all(axis=1)]
                    cuts.index.name = 'Pools'
                    cuts.reset_index(drop=False, inplace=True)
                    cuts.loc['Total'] = cuts[['Total']].sum()
                    cuts.loc[cuts.index[-1], 'Pools'] = 'Total'
                    # cuts.loc[cuts.index[-1], 'Total'] = 'Total'
                    cuts = cuts.style.format(
                        '${:.2f}', subset=['Total']
                        ).format('{:.0f}%', subset=['% of Total'])
                    cuts = cuts.set_properties(subset = pd.IndexSlice[['Total'], :], **{'background-color' : 'lightgrey'})
                    st.dataframe(cuts, hide_index=True)
            notes = st.text_area(
                'Notes', height=int(35.2 * (2)), 
                value=st.session_state['tipdata'].get('Tipping Notes', ''),
                key='tippingnotes',
                on_change=syncInput, args=('tippingnotes', 'Tipping Notes')
                )
            st.markdown('#### Position Tip Pool Eligibility Breakout')
            ByPosition()
            st.markdown('---')
            st.markdown('### Revisions to Work Positions')
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
                st.dataframe(df.sort_values(by=['name']), column_config=config, hide_index=True)
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
