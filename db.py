
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

from config import config

DATABASE = config.get('Database Parameters', 'database_url')

engine = create_engine(DATABASE, echo=False) 
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    print "Setting up database connection, initalizing if necessary."
    Base.metadata.create_all(bind=engine)
