import firebase_admin
from firebase_admin.firestore import firestore
from firebase_admin import credentials
from app.env_settings import settings

cred = credentials.Certificate("app/db/upkeepnow-6ec42-firebase-adminsdk-fbsvc-3cd8c824e3.json")
firebase_app = firebase_admin.initialize_app(cred)
firestore_db = firestore.Client()
