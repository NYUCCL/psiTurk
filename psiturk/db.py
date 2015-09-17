
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

from psiturk_config import PsiturkConfig

config = PsiturkConfig()
config.load_config()

DATABASE = config.get('Database Parameters', 'database_url')

config_pool_recycle = config.getint('Database Parameters', 'pool_recycle')

engine = create_engine(DATABASE, echo=False, pool_recycle=config_pool_recycle)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    #print "Initalizing db if necessary."
    Base.metadata.create_all(bind=engine)
