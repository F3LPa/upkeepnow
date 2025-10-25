import firebase_admin
from firebase_admin import credentials, firestore, storage
from app.env_settings import settings

cred = credentials.Certificate(settings("GOOGLE_APPLICATION_CREDENTIALS"))
FIREBASE_STORAGE_BUCKET = settings("BUCKET")

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {"storageBucket": FIREBASE_STORAGE_BUCKET})

# Pega o projeto do Firebase
project_id = cred.project_id

# Cria o cliente Firestore usando as credenciais
firestore_db = firestore.client()  # Use o cliente do firebase_admin


def get_bucket():
    return storage.bucket()
