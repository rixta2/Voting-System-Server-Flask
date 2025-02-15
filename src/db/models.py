from . import db
from sqlalchemy import String, Column, Integer

class factions(db.Model):
    name = Column(String(80), primary_key=True)
    score = Column(Integer)