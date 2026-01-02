import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Fetch credentials
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "jury_db")

# Construct Connection String
# Format: mysql+mysqlconnector://user:password@host:port/dbname
SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create the Engine with Robust Pooling
# pool_recycle=3600: Recycles connections every hour to prevent stale timeouts
# pool_pre_ping=True: The 'Heartbeat'. Checks if DB is alive before every query.
# Critical for AI apps where generation takes time and connections might drop.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    pool_recycle=3600,
    pool_pre_ping=True,
    pool_size=10,           # Baseline number of connections to keep open
    max_overflow=20         # Allow spikes up to 30 total connections
)

# Create SessionLocal class
# This will be instantiated for every API request
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our ORM models
Base = declarative_base()

# Dependency Injection for FastAPI
def get_db():
    """
    Creates a new database session for a request and closes it 
    automatically when the request finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()