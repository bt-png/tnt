import json
import streamlit as st
import numpy as np
import pandas as pd
from google.cloud import firestore
from google.oauth2 import service_account


key_dict = json.loads(st.secrets['Firestorekey'])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds)


def get_locker_data(locker_num: int):
    try:
        doc_ref = db.collection('locker_data_KOGA').document(str(locker_num))
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return {}
    except Exception as error:
        st.session_state.auth_warning = 'Error: Please try again later'
        return {}


def post_locker_data(locker_num: int, updates: dict):
    try:
        doc_ref = db.collection('locker_data_KOGA').document(str(locker_num))
        doc = doc_ref.get()
        if doc.exists:
            val = doc.to_dict()
            for k, v in updates.items():
                if k != 'Assigned':
                    val[k] = v  
        else:
            val = updates
            val.pop('Assigned')
        doc_ref.set(val)
        return True
    except Exception as error:
        st.session_state.auth_warning = 'Error: Please try again later'
        return False


def post_locker_combo(locker_num: int, updates: dict):
    try:
        doc_ref = db.collection('locker_data_KOGA').document(str(locker_num))
        doc = doc_ref.get()
        if doc.exists:
            val = doc.to_dict()
            for k, v in updates.items():
                if k == 'Combinations':
                    val[k] = v  
        else:
            val = updates
            val.pop('Assigned')
        doc_ref.set(val)
        return True
    except Exception as error:
        st.session_state.auth_warning = 'Error: Please try again later'
        return False


def reset_locker_data(locker_num: int):
    try:
        doc_ref = db.collection('locker_data_KOGA').document(str(locker_num))
        doc = doc_ref.get()
        if doc.exists:
            val = doc.to_dict()
            val['Comments'] = np.nan
            if 'Verified' in val:
                val.pop('Verified')
            doc_ref.set(val)
            return True
        else:
            return False
    except Exception as error:
        st.session_state.auth_warning = 'Error: Please try again later'
        return False


def post_locker_assignments(updates: dict):
    try:
        doc_ref = db.collection('locker_data_KOGA').document('Assignments')
        doc = doc_ref.get()
        if doc.exists:
            val = doc.to_dict()
        else:
            val = dict()
        for k, v in updates.items():
            val[str(k)] = v['Assigned']
        doc_ref.set(val)
        return True
    except Exception as error:
        st.session_state.auth_warning = 'Error: Please try again later'
        return False


def revoke_locker_assignment(locker_num: int):
    try:
        doc_ref = db.collection('locker_data_KOGA').document('Assignments')
        doc = doc_ref.get()
        if doc.exists:
            val = doc.to_dict()
            if str(locker_num) in val.keys():
                val.pop(str(locker_num))
                doc_ref.set(val)
                return True
            else:
                return False
        else:
            return False
    except Exception as error:
        st.session_state.auth_warning = 'Error: Please try again later'
        return False


# def stream_locker_data():
#     updatemade = False
#     batch = db.batch()
#     doc_ref = db.collection('locker_data_KOGA')
#     for doc in doc_ref.stream():
#         if doc.id == strname:
#             updatemade = True
#             dict_doc = doc.to_dict()
#             dict_doc.update({'Attendee': strnewname})
#             doc_newref = db.collection('futureattendance').document(strnewname)
#             doc_newref.set(dict_doc)
#             batch.delete(doc.reference)
#     if updatemade:
#         batch.commit()


def get_locker_assignments():
    try:
        doc_ref = db.collection('locker_data_KOGA').document('Assignments')
        doc = doc_ref.get()
        if doc.exists:
            val = doc.to_dict()
            return val
        return {}
    except Exception as error:
        st.session_state.auth_warning = 'Error: Please try again later'
        return {}

# def stream_locker_data():
#     df = pd.DataFrame({
#         'Name': [],
#         'Status': [],
#         'Attendance Poll': [],
#     })
#     doc_ref = db.collection('futureattendance')
#     for doc in doc_ref.stream():
#         new_entry = pd.DataFrame([{
#             'Name': doc.id,
#             'Status': roster.member_status(doc.id),
#             'Attendance Poll': doc.to_dict()['plan']
#             }])
#         df = pd.concat([df,new_entry], ignore_index=True)
#     return df

#     updatemade = False
#     batch = db.batch()
#     doc_ref = db.collection('futureattendance')
#     for doc in doc_ref.stream():
#         if doc.id == strname:
#             updatemade = True
#             dict_doc = doc.to_dict()
#             dict_doc.update({'Attendee': strnewname})
#             doc_newref = db.collection('futureattendance').document(strnewname)
#             doc_newref.set(dict_doc)
#             batch.delete(doc.reference)
#     if updatemade:
#         batch.commit()