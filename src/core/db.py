from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from urllib.parse import quote_plus

# Escapar posibles caracteres especiales
user = quote_plus("postgres")
password = quote_plus("kikiyale123")
host = "localhost"
port = 5432
db_name = "ciencia_de_datos"

DB_URL = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False)
Base = declarative_base()
