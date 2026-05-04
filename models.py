from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from database import engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ChatLog(Base):
    __tablename__ = "chat_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50))
    user_message = Column(Text)
    bot_response = Column(Text)
    sentiment = Column(String(20))
    created_at = Column(TIMESTAMP)

Base.metadata.create_all(bind=engine)