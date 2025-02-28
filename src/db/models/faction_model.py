from sqlalchemy import String, Column, Integer
from .. import Base, SessionLocal
import logging
from src.utils.constants import FACTIONS

class Faction(Base):
    __tablename__ = "factions"
    name = Column(String(80), primary_key=True)
    score = Column(Integer)
    
    def __init__(self, name, score=0):
        self.name = name
        self.score = score


    

