import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate("/Users/keerthanaulaganathan/Desktop/python/ML/OpenCV/stock_env/firebase.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://stockleveldetection-default-rtdb.firebaseio.com/"
})

def get_db():
    return db.reference("stock_logs")
