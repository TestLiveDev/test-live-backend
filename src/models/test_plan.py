from .database.base import Base

from sqlalchemy import Column, Integer, String, ForeignKey


class TestPlan(Base):
    __tablename__ = 't_test_plan'
    __table_args__ = (
        {'schema': 'testlive'},
        {'comment': 'Test Plan Table'}
    )

    id_test_plan = Column(Integer, primary_key=True, autoincrement=True, comment='ID Test Plan')
    id_organization = Column(Integer, ForeignKey('testlive.t_organization.id_organization'),
                             index=True, comment='ID Organization')
    id_parent = Column(Integer, ForeignKey('testlive.t_test_plan.id_test_plan'),
                       index=True, comment='ID Parent Test Plan')
    name_test_plan = Column(String(160), nullable=False, comment='Name Test Plan')
