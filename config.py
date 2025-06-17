import os

TOKEN = os.getenv('TOKEN', '')
OWNER_ID = int(os.getenv('OWNER_ID', ''))
MONGO_URI = os.getenv('MONGO_URI', '')
DB_NAME = os.getenv('DB_NAME', '')
FORCE_SUB_CHANNEL = os.getenv('FORCE_SUB_CHANNEL', '')