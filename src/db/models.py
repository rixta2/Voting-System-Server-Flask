from sqlalchemy import String, Column, Integer
from .database import db
class factions(db.Model):
    name = Column(String(80), primary_key=True)
    score = Column(Integer)
    
    def __init__(self, name, score=0):
        self.name = name
        self.score = score