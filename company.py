import streamlit as st
import pandas as pd
import firestore
import pickle
from firestore import clientUpdateDict
from firestore import clientArchiveDict
from firestore import getclientArchive
from firestore import clientArchiveDelete
from firestore import readclients
from sync import syncdataframes


def refresh():
    firestore.readclients.clear()
    st.rerun()


def readClients():
    return firestore.readclients()


def servertipdata():
    try:
        val = readClients()[st.session_state['company']].copy()
        if 'tipdata' in val:
            pickled_bit = val['tipdata']
            return pickle.loads(pickled_bit)
    except Exception:
        return {}


def publisharchive(str):
    if 'updatedsomething' in st.session_state:
        if st.session_state['updatedsomething']:
            st.session_state['updatedsomething'] = False
            # Updating handled throu sync.synctipdata as callback function
            if 'tipdata' not in st.session_state:
                st.session_state['tipdata'] = {}
            else:
                syncdataframes()
    pickled_bit = pickle.dumps(st.session_state['tipdata'])
    clientArchiveDict(str, st.session_state['company'], 'tipdata', pickled_bit)
    readclients.clear()
    st.session_state['tipdata'] = servertipdata()
    st.rerun()


def loadarchive(str):
    pickled_bit = getclientArchive(str, st.session_state['company'])
    st.session_state['tipdata'] = pickle.loads(pickled_bit)
    # st.rerun()


def deletearchive(str):
    clientArchiveDelete(str, st.session_state['company'])
    st.rerun()


def publish():
    if 'updatedsomething' in st.session_state:
        if st.session_state['updatedsomething']:
            st.session_state['updatedsomething'] = False
            # Updating handled throu sync.synctipdata as callback function
            if 'tipdata' not in st.session_state:
                st.session_state['tipdata'] = {}
            else:
                syncdataframes()
            pickled_bit = pickle.dumps(st.session_state['tipdata'])
            clientUpdateDict(st.session_state['company'], 'tipdata', pickled_bit)
            readclients.clear()
            st.session_state['tipdata'] = servertipdata()
            st.rerun()


def saveNewClient(company, authorized_emails):
    firestore.addclient(company, authorized_emails)
    firestore.addPreAuthorizedEmails(authorized_emails)
    refresh()
    st.success('Client information has been saved.')


def associateEmail(email, username):
    return firestore.associateEmail(email, username)


def clientGetValue(client, field):
    clients = readClients()
    if field in clients[client]:
        return clients[client][field]
    else:
        return []


def updatePositionSplits(client):
    st.write('Default Position Splits')
    st.caption('Position splits performed automatically. User may revise.')
    clients = readClients()
    positionSplits = {
        'perc': [50],
        'from': ['Farm & Kitchen Assistant'],
        'to': ['Back of House'],
        'reason': ['Default_Assigned Split Shifts']
        }
    if 'positionsplits' in clients[client]:
        positionSplits = clients[client]['positionsplits']
    data_edited = st.data_editor(
        pd.DataFrame.from_dict(positionSplits),
        num_rows='dynamic',
        hide_index=True,
        key='positionsplits'
        ).dropna()
    update = {
        'perc': data_edited['perc'].to_list(),
        'from': data_edited['from'].to_list(),
        'to': data_edited['to'].to_list(),
        'reason': data_edited['reason'].to_list(),
        }
    if positionSplits != update:
        if st.button('Update Position Splits'):
            firestore.clientUpdateDict(client, 'positionsplits', update)
            refresh()


def updateTipPositions(client):
    st.write('Default Tipping Positions')
    st.caption('Position assignments loaded automatically. User may revise.')
    clients = readClients()
    tipPool = ['Garden FOH', 'Garden Host', 'Garden BOH', 'FOH', 'BOH']
    if 'tippools' in clients[client]:
        tipPool = clients[client]['tippools']
    tipPositions = {
        'Tip Pool': [0, 1, 2, 3, 3, 4, 4, 4],
        'Position': [
            'Garden Server',
            'Garden Host',
            'Garden & Kitchen Assistant',
            'Host',
            'Server',
            'Dishwasher',
            'Kitchen Assistant',
            'Back of House'
            ],
        }
    if 'tipposition' in clients[client]:
        tipPositions = clients[client]['tipposition']
    data = tipPositions.copy()
    data['Pool'] = [tipPool[idx] for idx in data['Tip Pool']]
    data = pd.DataFrame.from_dict(data)
    data.drop('Tip Pool', axis=1, inplace=True)
    data_edited = st.data_editor(
        pd.DataFrame(data),
        num_rows='dynamic',
        column_order=['Pool', 'Position'],
        column_config={
            'Position': st.column_config.TextColumn(width='large'),
            'Pool': st.column_config.SelectboxColumn(options=tipPool)
            },
        hide_index=True,
        key='tipposition'
        ).dropna()
    data_edited['Tip Pool'] = [tipPool.index(name) for name in data_edited['Pool']]
    update = {'Tip Pool': data_edited['Tip Pool'].to_list(), 'Position': data_edited['Position'].to_list()}
    if tipPositions != update:
        if st.button('Update Tip Positions'):
            firestore.clientUpdateDict(client, 'tipposition', update)  # clientUpdateTipPositions(client, update)
            refresh()


def updateTipPoolNames(client):
    st.write('Available Tipping Pools')
    st.caption('Pool splits, order is maintained.')
    clients = readClients()
    tipPool = ['Garden FOH', 'Garden Host', 'Garden BOH', 'Lead', 'FOH', 'BOH']
    if 'tippools' in clients[client]:
        tipPool = clients[client]['tippools']
    update = st.data_editor(
        pd.DataFrame({'Pool': tipPool}),
        num_rows='fixed',
        column_config={
            'Pool': st.column_config.TextColumn(width='medium')
            },
        hide_index=False,
        key='tippools'
        ).dropna()
    update = update['Pool'].to_list()
    if tipPool != update:
        if st.button('Update Tip Pool'):
            firestore.clientUpdateDict(client, 'tippools', update)  # clientUpdateTipPoolNames(client, update)
            refresh()


def updateTipExemptEmployees(client):
    st.write('Tip Exempt Employees')
    st.caption('Hours will not be attributed to the tipping pools. User may add/remove more.')
    clients = readClients()
    tipExempt = []
    if 'tipexempt' in clients[client]:
        tipExempt = clients[client]['tipexempt']
    update = st.data_editor(
        pd.DataFrame({'Employee Name': tipExempt}, dtype=str),
        num_rows='dynamic',
        column_config={'Employee Name': st.column_config.TextColumn(width='large')},
        hide_index=True,
        key='tipexempt'
        ).dropna()
    update = update['Employee Name'].to_list()
    if tipExempt != update:
        if st.button('Update Tip Exempt List'):
            firestore.clientUpdateDict(client, 'tipexempt', update)  # clientUpdateTipExemptEmployees(client, update)
            refresh()


def updateOverridePositions(client):
    st.write('Override Positions')
    st.caption('Entered positions will always be available, regardless if shifts were worked.')
    clients = readClients()
    positions = []
    if 'overridepositions' in clients[client]:
        positions = clients[client]['overridepositions']
    update = st.data_editor(
        pd.DataFrame({'Position': positions}, dtype=str),
        num_rows='dynamic',
        column_config={'Position': st.column_config.TextColumn(width='medium')},
        hide_index=True,
        key='positions'
        ).dropna()
    update = update['Position'].to_list()
    if positions != update:
        if st.button('Update Override Positions'):
            firestore.clientUpdateDict(client, 'overridepositions', update)
            refresh()


def updateChefEmployees(client):
    st.write('List of Chef\'s')
    st.caption('Default list for chef pool. User may add more.')
    clients = readClients()
    chefs = []
    if 'chefs' in clients[client]:
        chefs = clients[client]['chefs']
    update = st.data_editor(
        pd.DataFrame({'Employee Name': chefs}, dtype=str),
        num_rows='dynamic',
        column_config={'Employee Name': st.column_config.TextColumn(width='large')},
        hide_index=True,
        key='chef'
        ).dropna()
    update = update['Employee Name'].to_list()
    if chefs != update:
        if st.button('Update List of Chef\'s'):
            firestore.clientUpdateDict(client, 'chefs', update)
            refresh()


def updateEmailsUsers(client):
    clients = readClients()
    emails = []
    users = []
    if 'emails' in clients[client]:
        emails = clients[client]['emails']
    if 'username' in clients[client]:
        users = clients[client]['username']
    col1, col2 = st.columns([1, 1])
    with col1:
        st.write('Associated Emails')
        authorized_emails = st.data_editor(
            pd.DataFrame({'Authorized Emails': emails}, dtype=str),
            num_rows='dynamic',
            column_config={'Authorized Emails': st.column_config.TextColumn(width='large')},
            hide_index=True,
            key='emails'
            ).dropna()
    with col2:
        st.write('Associated Users')
        authorized_users = st.data_editor(
            pd.DataFrame({'UserNames': users}, dtype=str),
            num_rows='dynamic',
            column_config={'UserNames': st.column_config.TextColumn(width='medium')},
            hide_index=True,
            key='users'
            ).dropna()
    authorized_emails = authorized_emails['Authorized Emails'].to_list()
    authorized_users = authorized_users['UserNames'].to_list()
    if emails != authorized_emails and users != authorized_users:
        if st.button('Update Emails and Users'):
            firestore.clientUpdateDict(client, 'emails', authorized_emails)
            firestore.clientUpdateDict(client, 'username', authorized_users)
            refresh()
    elif emails != authorized_emails:
        if st.button('Update Emails'):
            firestore.clientUpdateDict(client, 'emails', authorized_emails)
            refresh()
    elif users != authorized_users:
        if st.button('Update Users'):
            firestore.clientUpdateDict(client, 'username', authorized_users)
            refresh()


def newClient():
    company = st.text_input('Company Name')
    emails = st.data_editor(pd.DataFrame({'Authorized Emails': []}, dtype=str),
                            num_rows='dynamic',
                            hide_index=True,
                            column_config={
                                'Authorized Emails': st.column_config.TextColumn(width='large')
                                }
                            )
    if st.form_submit_button('Save'):
        saveNewClient(company, emails['Authorized Emails'].to_list())


def cpmain(company):
    st.session_state['company'] = company
    st.markdown('---')
    col1, col2 = st.columns([1.25, 8.75])
    col1.write('')
    col1.caption('Associated Company:')
    col2.header(company)
    st.caption('Use the navigation menu on the left to get started!')
