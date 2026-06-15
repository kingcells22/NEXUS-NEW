from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# URL de conexión a tu PostgreSQL 16 local
# Formato: postgresql://usuario:password@localhost:5432/nombre_bd
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:123456@localhost:5432/nexus_db"

# Creación del motor que se comunica con la base de datos
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"client_encoding": "utf8"}
)

# Fábrica de sesiones para interactuar con la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base de la cual heredarán todos nuestros modelos
Base = declarative_base()

# Dependencia para inyectar la sesión en las rutas de FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()