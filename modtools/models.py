from sqlalchemy import Column, String, Integer, DateTime, Boolean

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

class DiscordAction(Base):
    __tablename__ = 'discordactions'

    id = Column(String, primary_key=True)
    action = Column(String, primary_key=True)
    date = Column(DateTime, primary_key=True)
    link = Column(String)
    text = Column(String, primary_key=True)
    target_id = Column(String)
    target_type = Column(String)
    completed = Column(Boolean, default=False)
    reactcompleted = Column(Boolean, default=False)
    messageID = Column(String)
    target_user = Column(String)
    target_channel = Column(String)

class Report(Base):
    __tablename__ = 'reports'
    id = Column(String, primary_key=True)
    date = Column(DateTime, primary_key=True)
    count = Column(String, primary_key=True)
    reason = Column(String, nullable=False)
    date = Column(DateTime)

class ModMailConversation(Base):
    __tablename__ = 'modmailconversations'
    id = Column(String, primary_key=True)
    participant = Column(String)
    subject = Column(String)
    lastupdated = Column(DateTime)