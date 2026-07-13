import os
import sqlalchemy as sa
from sqlalchemy.event import listen

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

DB_PATH = os.path.join(DATA_DIR, "scada.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Using timeout to prevent database locked errors with concurrent access
engine = sa.create_engine(
    DATABASE_URL, 
    connect_args={"timeout": 15, "check_same_thread": False}
)

def _set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()

listen(engine, 'connect', _set_sqlite_pragma)

def get_engine():
    return engine
