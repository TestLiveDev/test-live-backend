from .database.base import Base

from sqlalchemy import Column, Integer, String, ForeignKey, Text


class TestStep(Base):
    __tablename__ = 't_test_step'
    __table_args__ = (
        {'schema': 'testlive'},
        {'comment': 'Test Step Table'}
    )

    id_test_step = Column(Integer, primary_key=True, autoincrement=True, comment='ID Test Plan')
    id_test_plan = Column(Integer, ForeignKey('testlive.t_test_plan.id_test_plan'),
                          index=True, comment='ID Test Plan')
    name_test_step = Column(String(160), nullable=False, comment='Name Test Step')
    reproduce = Column(Text, comment='Step to Reproduce')
    expected = Column(Text, comment='Expected Result')
