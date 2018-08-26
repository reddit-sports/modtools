from sqlalchemy import Column, String, Integer, DateTime, ARRAY
from b import Base


class ModQueueItem(Base):
    __tablename__ = 'modqueue'

    id = Column(String, primary_key=True)
    posttype = Column(String)
    date = Column(DateTime)
    link_title = Column(String)
    link_id = Column(String)
    author = Column(String)
    edited = Column(String)
    body = Column(String)
    permalink = Column(String)