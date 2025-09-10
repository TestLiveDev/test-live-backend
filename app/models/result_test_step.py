from .database.base import Base

from sqlalchemy import Column, Integer, ForeignKey, Text


class ResultTestStep(Base):
    __tablename__ = 't_result_test_step'
    __table_args__ = ({'schema': 'testlive', 'comment': 'Result Test Step'})

    id_result_test_step = Column(Integer, primary_key=True, autoincrement=True, comment='ID Result Test Step')
    id_result_test_case = Column(Integer, ForeignKey('testlive.t_result_test_case.id_result_test_case'),
                                 nullable=False, index=True, comment='ID Result Test Case')
    id_test_step = Column(Integer, ForeignKey('testlive.t_test_case.id_test_case'),
                          nullable=False, index=True, comment='ID Test Case')
    id_status = Column(Integer, ForeignKey('testlive.t_status.id_status'), index=True, comment='ID Status')
    result = Column(Text, comment='Fact Result')
