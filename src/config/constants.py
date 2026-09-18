import os

from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv('API_KEY')
EXTERNAL_URL = os.getenv('EXTERNAL_URL')
VIDEO_DIR = os.getenv('VIDEO_DIR')
COMFY_URL = os.getenv('COMFY_URL')
DB_PATH = "data/requests.db"