#sqlalchemy

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

#sqlite
engine = create_engine('sqlite:///db.sqlite3', echo=True)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

class Token(Base):
    __tablename__ = 'tokens'
    id = Column(Integer, primary_key=True)
    token = Column(String)
    #telegram user id string unique
    user_id = Column(String, unique=True)
    route_id = Column(String)

    def __repr__(self):
        return "<Token(token='%s', user_id='%s')>" % (
            self.token, self.user_id)
    
class Screen(Base):
    __tablename__ = 'screens'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    user_id = Column(String)
    chat_id = Column(String)
    message_id = Column(String)

    def __repr__(self):
        return "<Screen(name='%s', user_id='%s')>" % (
            self.name, self.user_id)

class Thread(Base):
    __tablename__ = 'threads'
    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    thread_id = Column(String)
