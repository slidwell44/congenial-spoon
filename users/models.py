from sqlalchemy import Column, Integer, String

from db.core import Base


class User(Base):
    __tablename__ = "users"
    uid = Column(Integer, primary_key=True)
    oid = Column(Integer, primary_key=True)
    id = Column(String(255), nullable=False)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
