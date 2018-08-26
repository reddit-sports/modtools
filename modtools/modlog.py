from sqlalchemy import Column, String, Integer, DateTime

from b import Base


class ModLog(Base):
    __tablename__ = 'modlogs'

    id = Column(String, primary_key=True)
    target_body = Column(String)
    mod_id36 = Column(String)
    date = Column(DateTime)
    created_utc = Column(Integer)
    subreddit = Column(String)
    target_title = Column(String)
    target_permalink = Column(String)
    details = Column(String)
    action = Column(String)
    target_author = Column(String)
    target_fullname = Column(String)
    sr_id36 = Column(String)
    mod = Column(String)
