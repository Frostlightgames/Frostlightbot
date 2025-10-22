from sqlalchemy import Column, Integer, String
from Frostlightbot.data.classes.dbConnect import Base, engine

class Config(Base):
    __tablename__ = "config"

    id      = Column(Integer, primary_key=True, autoincrement=False)
    name    = Column(String, nullable=False, unique=True)

    def __repr__(self):
        return f"<Config(id={self.id}, name='{self.name}')>"
    
    def __init__(self,id,name):
        self.id     = id
        self.name   = name

class Member(Base):
    __tablename__ = "member"

    id      = Column(Integer, primary_key=True, autoincrement=False)
    name    = Column(String , nullable=False)
    coins   = Column(Integer)
    candy   = Column(Integer)
    level   = Column(Integer)
    xp      = Column(Integer)

    def __repr__(self):
        return f"<Member(id={self.id}, name='{self.name}', coins={self.coins}, candy={self.candy}, level={self.level}, xp={self.xp})>"

    def __init__(self,id,name,coins=0,candy=0,level=1,xp=0):
        self.id     = id
        self.name   = name
        self.coins  = coins
        self.candy  = candy
        self.level  = level
        self.xp     = xp

Base.metadata.create_all(engine)