from .database.base import Base

from sqlalchemy import Column, Integer, ForeignKey


class ResultTestCase(Base):
    __tablename__ = 't_result_test_case'
    __table_args__ = ({'schema': 'testlive', 'comment': 'Result Test Case Table'})

    id_result_test_case = Column(Integer, primary_key=True, autoincrement=True, comment='ID Result Test Case')
    id_release = Column(Integer, ForeignKey('testlive.t_release.id_release'), index=True, comment='ID Relese')
    id_test_case = Column(Integer, ForeignKey('testlive.t_test_case.id_test_case'), index=True, comment='ID Test Case')
