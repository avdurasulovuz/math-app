from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
from config import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)
    name = Column(String, default="O'quvchi")
    grade = Column(Integer, default=7) # 1 - 11 sinflar
    coins = Column(Integer, default=100)
    streak = Column(Integer, default=1)
    xp = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Resource(Base):
    __tablename__ = "resources"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    category = Column(String, nullable=False) # 'textbook', 'formula', 'dtm', 'audio'
    grade = Column(Integer, default=7)
    subject = Column(String, default="Algebra") # Algebra, Geometriya, Matematika
    file_url = Column(String, nullable=True)
    content = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Problem(Base):
    __tablename__ = "problems"
    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(Text, nullable=False)
    image_url = Column(String, nullable=True)
    solution_steps_json = Column(Text, nullable=False) # JSON array of step titles & explanations
    audio_script = Column(Text, nullable=True) # Text for TTS voice
    grade = Column(Integer, default=7)
    subject = Column(String, default="Algebra")
    topic = Column(String, default="Tenglamalar")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Duel(Base):
    __tablename__ = "duels"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    creator_id = Column(Integer)
    opponent_id = Column(Integer, nullable=True)
    creator_score = Column(Integer, default=0)
    opponent_score = Column(Integer, default=0)
    status = Column(String, default="pending") # pending, active, completed
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)
