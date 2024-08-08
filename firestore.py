import streamlit as st
import json
# import firebase_admin
# from firebase_admin import credentials
# cred = credentials.Certificate(key_dict)
# firebase_admin.initialize_app(cred)
from google.cloud import firestore
from google.oauth2 import service_account


key_dict = json.loads(st.secrets['Firestorekey'])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds)


# ---------login----------------
def createnewconfig():
    conf = {
        'credentials': {
            'usernames': {
                'jsmith': {
                    'email': 'jsmith@gmail.com',
                    'failed_login_attempts': 0,  # Will be managed automatically
                    'logged_in': False,  # Will be managed automatically
                    'name': 'John Smith',
                    'password': 'abc',  # Will be hashed automatically
                },
                'rbriggs': {
                    'email': 'rbriggs@gmail.com',
                    'failed_login_attempts': 0,  # Will be managed automatically
                    'logged_in': False,  # Will be managed automatically
                    'name': 'Rebecca Briggs',
                    'password': 'def'  # Will be hashed automatically
                }
            }
        },
        'cookie': {
            'expiry_days': 30,
            'key': 'some_signature_key',  # Must be string
            'name': 'some_cookie_name'
        },
        'pre-authorized': {
            'emails': []
        }
    }
    saveconfig(conf)


def openconfig():
    doc_ref = db.collection('users').document('login')
    doc = doc_ref.get()
    conf = doc.to_dict()
    return conf


def saveconfig(conf):
    try:
        doc_ref = db.collection('users').document('login')
        doc_ref.set(conf)
    except Exception:
        st.session_state.auth_warning = 'Error: Please try again later'


def addPreAuthorizedEmails(emails):
    conf = openconfig()
    existingemails = conf['pre-authorized']['emails']
    for email in emails:
        if email not in existingemails:
            existingemails.append(email)
    saveconfig(conf)


# ---------clients----------------
@st.cache_data
def readclients():
    clients = dict()
    try:
        doc_ref = db.collection('clients')
        for doc in doc_ref.stream():
            val = doc.to_dict()
            clients[doc.id] = val
        return clients
    except Exception:
        st.session_state.auth_warning = 'Error: Please try again later'


def saveclients(client_dict):
    try:
        doc_ref = db.collection('clients').document('companies')
        doc_ref.set(client_dict)
    except Exception:
        st.session_state.auth_warning = 'Error: Please try again later'


def addclient(client, emails):
    doc_ref = db.collection('clients').document(client)
    if not doc_ref.get().exists:
        doc_ref.set({
            'emails': emails
        })


# def clientUpdateUsers(client: str, username: list):
#     try:
#         doc_ref = db.collection('clients').document(client)
#         doc = doc_ref.get()
#         if doc.exists:
#             val = doc.to_dict()
#             val['username'] = username
#         else:
#             val = {'username': username}
#         doc_ref.set(val)
#     except Exception:
#         st.session_state.auth_warning = 'Error: Please try again later'

def listclientArchive(client):
    archives = []
    try:
        doc_ref = db.collection('archives').document(client)
        for doc in doc_ref.stream():
            st.write(doc.data.id)
            archives.append(doc.id)
        return archives
    # try:
    #     if 'tipdata' in val:
    #         pickled_bit = val['tipdata']
    #         return pickle.loads(pickled_bit)
    except Exception:
        return {}


def clientArchiveDict(str, client, field, update):
    try:
        doc_ref = db.collection('archives').document(client)
        doc = doc_ref.get()
        if doc.exists:
            val = doc.to_dict()
            val[str] = update
        else:
            val = {str: update}
        doc_ref.set(val)
    except Exception:
        st.session_state.auth_warning = 'Error: Please try again later'


def clientUpdateDict(client, field, update):
    try:
        doc_ref = db.collection('clients').document(client)
        doc = doc_ref.get()
        if doc.exists:
            val = doc.to_dict()
            val[field] = update
        else:
            val = {field: update}
        doc_ref.set(val)
    except Exception:
        st.session_state.auth_warning = 'Error: Please try again later'


# def clientUpdateTipPositions(client, update):
#     try:
#         doc_ref = db.collection('clients').document(client)
#         doc = doc_ref.get()
#         if doc.exists:
#             val = doc.to_dict()
#             val['tipposition'] = update
#         else:
#             val = {'tipposition': update}
#         doc_ref.set(val)
#     except Exception:
#         st.session_state.auth_warning = 'Error: Please try again later'


# def clientUpdateTipPoolNames(client, update):
#     try:
#         doc_ref = db.collection('clients').document(client)
#         doc = doc_ref.get()
#         if doc.exists:
#             val = doc.to_dict()
#             val['tippools'] = update
#         else:
#             val = {'tippools': update}
#         doc_ref.set(val)
#     except Exception:
#         st.session_state.auth_warning = 'Error: Please try again later'


# def clientUpdateOverridePositions(client, update):
#     try:
#         doc_ref = db.collection('clients').document(client)
#         doc = doc_ref.get()
#         if doc.exists:
#             val = doc.to_dict()
#             val['overridepositions'] = update
#         else:
#             val = {'overridepositions': update}
#         doc_ref.set(val)
#     except Exception:
#         st.session_state.auth_warning = 'Error: Please try again later'


# def clientUpdateChefEmployees(client, update):
#     try:
#         doc_ref = db.collection('clients').document(client)
#         doc = doc_ref.get()
#         if doc.exists:
#             val = doc.to_dict()
#             val['chefs'] = update
#         else:
#             val = {'chefs': update}
#         doc_ref.set(val)
#     except Exception:
#         st.session_state.auth_warning = 'Error: Please try again later'


# def clientUpdateTipExemptEmployees(client, update):
#     try:
#         doc_ref = db.collection('clients').document(client)
#         doc = doc_ref.get()
#         if doc.exists:
#             val = doc.to_dict()
#             val['tipexempt'] = update
#         else:
#             val = {'tipexempt': update}
#         doc_ref.set(val)
#     except Exception:
#         st.session_state.auth_warning = 'Error: Please try again later'


# def clientUpdateEmails(client, emails: list):
#     try:
#         doc_ref = db.collection('clients').document(client)
#         doc = doc_ref.get()
#         if doc.exists:
#             val = doc.to_dict()
#             val['emails'] = emails
#         else:
#             val = {'emails': emails}
#         doc_ref.set(val)
#     except Exception:
#         st.session_state.auth_warning = 'Error: Please try again later'


def addUsernametoClient(client, username):
    try:
        doc_ref = db.collection('clients').document(client)
        doc = doc_ref.get()
        if doc.exists:
            val = doc.to_dict()
            if 'username' in val:
                users = val['username']
                if username not in users:
                    users.append(username)
            else:
                val['username'] = [username]
        else:
            val = {'username': username}
        doc_ref.set(val)
    except Exception:
        st.session_state.auth_warning = 'Error: Please try again later'


def associateEmail(email, username):
    try:
        doc_ref = db.collection('clients')
        for doc in doc_ref.stream():
            dict = doc.to_dict()
            if email in dict['emails']:
                st.write(f'Email associated to {doc.id}')
                addUsernametoClient(doc.id, username)
    except Exception:
        st.session_state.auth_warning = 'Error: Please try again later'


def userAssociatedCompanies(username):
    companies = readclients()
    companylist = []  # companies.keys()
    for company in companies:
        if 'username' in companies[company]:
            if username in companies[company]['username']:
                companylist.append(company)
    return companylist
