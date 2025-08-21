# db.py
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(dotenv_path=ROOT_DIR / ".env")

mongo_url = os.environ["MONGO_URL"]
client = AsyncIOMotorClient(mongo_url)

# Múltiplos bancos
db_gpac = client["gpac"]
db_bkautocenter = client["bkautocenter"]
db_agua_na_boca = client["aguanaboca"]
db_equora = client["equora"]
