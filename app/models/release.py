from .database.base import Base

from sqlalchemy import Column, Integer, String, ForeignKey


class Release(Base):
    __tablename__ = 't_release'
    __table_args__ = (
        {'schema': 'testlive'},
        {'comment': 'Release Table'}
    )
  
    id_release = Column(Integer, primary_key=True, autoincrement=True, comment='ID Organization')
    id_organization = Column(Integer, ForeignKey('testlive.t_organization.id_organization'), nullable=False, comment='ID Organization')
    name_release = Column(String(160), nullable=False, comment='Name Release')
