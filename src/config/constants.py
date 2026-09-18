import os

from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv('API_KEY')
COMFY_URL = "http://localhost:8188"
DB_PATH = "data/requests.db"