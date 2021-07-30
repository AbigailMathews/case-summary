import databases
import os
import urllib
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

host_server = os.environ.get('host_server', 'localhost')
db_server_port = os.environ.get('db_server_port', '5432')
database_name = os.environ.get('database_name', 'openpoliceai')
db_username = os.environ.get('db_username', 'openpoliceai')
db_password = os.environ.get('db_password', 'openpoliceai')
SQLALCHEMY_DATABASE_URL = 'postgresql://{}:{}@{}:{}/{}'.format(
    db_username, db_password, host_server, db_server_port, database_name)

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
