from .database.base import Base

from sqlalchemy import Column, Integer, String


class Status(Base):
    __tablename__ = 't_status'
    __table_args__ = (
        {'schema': 'testlive'},
        {'comment': 'Status Table'}
    )

    id_status = Column(Integer, primary_key=True, autoincrement=True, comment='ID Status')
    name_status = Column(String(60), nullable=False, unique=True, comment='Name Status')
    code_status = Column(String(60), nullable=False, unique=True, comment='Code Status')
