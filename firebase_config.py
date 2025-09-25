import firebase_admin
from firebase_admin import credentials, db
import streamlit as st
import json

# Load Firebase credentials from secrets
firebase_creds = st.secrets["firebase"]
cred = credentials.Certificate(dict(firebase_creds))

# Initialize Firebase app
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://stockleveldetection-default-rtdb.firebaseio.com/"
    })

def get_db():
    return db.reference("stock_logs")
