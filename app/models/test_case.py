from .database.base import Base

from sqlalchemy import Column, Integer, String, ForeignKey


class TestCase(Base):
    __tablename__ = 't_test_case'
    __table_args__ = ({'schema': 'testlive', 'comment': 'Test Case Table'})

    id_test_case = Column(Integer, primary_key=True, autoincrement=True, comment='ID Test Case')
    id_test_plan = Column(Integer, ForeignKey('testlive.t_test_plan.id_test_plan'),
                          nullable=False, index=True, comment='ID Test Plan')
    name_test_case = Column(String(160), nullable=False, comment='Name Test Case')
