
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from psiturk_config import PsiturkConfig

config = PsiturkConfig()
config.load_config()

DATABASE = config.get('Database Parameters', 'database_url')

if 'mysql' in config.get('Database Parameters', 'database_url').lower():
	try:
		 __import__('imp').find_module('MySQLdb')
	except ImportError:
		print("Sorry, to use a MySQL database you need to install "
			  "the `mysql-python` python package.  Try `pip mysql-python`. "
			  "Hopefully it goes smoothly for you.  Installation can "
			  "be tricky on some systems.")
		exit()

engine = create_engine(DATABASE, echo=False) 
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    #print "Initalizing db if necessary."
    Base.metadata.create_all(bind=engine)
