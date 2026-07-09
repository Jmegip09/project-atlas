import os
from dotenv import load_dotenv

# Loads variables from the .env file at the project root into the environment
load_dotenv()

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")

# SQLAlchemy connection string
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# File paths used across the pipeline
RAW_DATA_DIR = "data/raw"
SAMPLE_DATA_DIR = "data/sample"
PROCESSED_DATA_DIR = "data/processed"
DATA_QUALITY_LOG_PATH = "data/processed/data_quality_log.csv"