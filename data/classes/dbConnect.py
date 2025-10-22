from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base 

Base = declarative_base()

DB_PATH = "test.db"

engine = create_engine(f"sqlite:///{DB_PATH}", echo=True)
Session = sessionmaker(bind=engine)

def get_session():
    session = Session()

    return session