from src.core.db import engine
from src.data.models.booking_model import Base

if __name__ == "__main__":
    print("🛠️  Creando las tablas en la base de datos...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas correctamente.")
