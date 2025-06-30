from sqlmodel import Session, SQLModel, create_engine

from backend.settings.app_config import settings

sqlite_file_name = settings.ConnectionStrings.db_connections
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
