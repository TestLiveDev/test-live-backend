from .database.base import Base

from sqlalchemy import Column, Integer, String


class Oraganization(Base):
    __tablename__ = 't_organization'
    __table_args__ = (
        {'schema': 'testlive'},
        {'comment': 'Organization Table'}
    )
  
    id_organization = Column(Integer, primary_key=True, autoincrement=True, comment='ID Organization')
    name_organization = Column(String(160), nullable=False, comment='Name Oranization')
