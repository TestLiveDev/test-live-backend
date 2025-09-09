"""Main Tables

Revision ID: 96adfb895be5
Revises: 20e74310343a
Create Date: 2025-09-09 17:02:36.565055

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '96adfb895be5'
down_revision: Union[str, Sequence[str], None] = '20e74310343a'


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('t_organization',
        sa.Column('id_organization', sa.Integer(), autoincrement=True, nullable=False, comment='ID Organization'),
        sa.Column('name_organization', sa.String(length=160), nullable=False, comment='Name Oranization'),
        sa.PrimaryKeyConstraint('id_organization'),
        schema='testlive',
        comment='Organization Table'
    )

    op.create_table('t_status',
        sa.Column('id_status', sa.Integer(), autoincrement=True, nullable=False, comment='ID Status'),
        sa.Column('name_status', sa.String(length=60), nullable=False, comment='Name Status'),
        sa.Column('code_status', sa.String(length=60), nullable=False, comment='Code Status'),
        sa.PrimaryKeyConstraint('id_status'),
        sa.UniqueConstraint('code_status'),
        sa.UniqueConstraint('name_status'),
        schema='testlive',
        comment='Status Table'
    )

    op.create_table('t_release',
        sa.Column('id_release', sa.Integer(), autoincrement=True, nullable=False, comment='ID Release'),
        sa.Column('id_organization', sa.Integer(), nullable=False, comment='ID Organization'),
        sa.Column('name_release', sa.String(length=160), nullable=False, comment='Name Release'),
        sa.ForeignKeyConstraint(['id_organization'], ['testlive.t_organization.id_organization'], ),
        sa.PrimaryKeyConstraint('id_release'),
        schema='testlive',
        comment='Release Table'
    )
    op.create_index(op.f('ix_testlive_t_release_id_organization'), 't_release', ['id_organization'], unique=False, schema='testlive')

    op.create_table('t_test_plan',
        sa.Column('id_test_plan', sa.Integer(), autoincrement=True, nullable=False, comment='ID Test Plan'),
        sa.Column('id_organization', sa.Integer(), nullable=True, comment='ID Organization'),
        sa.Column('id_parent', sa.Integer(), nullable=True, comment='ID Parent Test Plan'),
        sa.Column('name_test_plan', sa.String(length=160), nullable=False, comment='Name Test Plan'),
        sa.ForeignKeyConstraint(['id_organization'], ['testlive.t_organization.id_organization'], ),
        sa.ForeignKeyConstraint(['id_parent'], ['testlive.t_test_plan.id_test_plan'], ),
        sa.PrimaryKeyConstraint('id_test_plan'),
        schema='testlive',
        comment='Test Plan Table'
    )
    op.create_index(op.f('ix_testlive_t_test_plan_id_organization'), 't_test_plan', ['id_organization'], unique=False, schema='testlive')
    op.create_index(op.f('ix_testlive_t_test_plan_id_parent'), 't_test_plan', ['id_parent'], unique=False, schema='testlive')

    op.create_table('t_test_case',
        sa.Column('id_test_case', sa.Integer(), autoincrement=True, nullable=False, comment='ID Test Case'),
        sa.Column('id_test_plan', sa.Integer(), nullable=False, comment='ID Test Plan'),
        sa.Column('name_test_case', sa.String(length=160), nullable=False, comment='Name Test Case'),
        sa.ForeignKeyConstraint(['id_test_plan'], ['testlive.t_test_plan.id_test_plan'], ),
        sa.PrimaryKeyConstraint('id_test_case'),
        schema='testlive',
        comment='Test Case Table'
    )
    op.create_index(op.f('ix_testlive_t_test_case_id_test_plan'), 't_test_case', ['id_test_plan'], unique=False, schema='testlive')

    op.create_table('t_test_step',
        sa.Column('id_test_step', sa.Integer(), autoincrement=True, nullable=False, comment='ID Test Plan'),
        sa.Column('id_test_plan', sa.Integer(), nullable=True, comment='ID Test Plan'),
        sa.Column('name_test_step', sa.String(length=160), nullable=False, comment='Name Test Step'),
        sa.Column('reproduce', sa.Text(), nullable=True, comment='Step to Reproduce'),
        sa.Column('expected', sa.Text(), nullable=True, comment='Expected Result'),
        sa.ForeignKeyConstraint(['id_test_plan'], ['testlive.t_test_plan.id_test_plan'], ),
        sa.PrimaryKeyConstraint('id_test_step'),
        schema='testlive',
        comment='Test Step Table'
    )
    op.create_index(op.f('ix_testlive_t_test_step_id_test_plan'), 't_test_step', ['id_test_plan'], unique=False, schema='testlive')

    op.create_table('t_result_test_case',
        sa.Column('id_result_test_case', sa.Integer(), autoincrement=True, nullable=False, comment='ID Result Test Case'),
        sa.Column('id_release', sa.Integer(), nullable=True, comment='ID Relese'),
        sa.Column('id_test_case', sa.Integer(), nullable=True, comment='ID Test Case'),
        sa.ForeignKeyConstraint(['id_release'], ['testlive.t_release.id_release'], ),
        sa.ForeignKeyConstraint(['id_test_case'], ['testlive.t_test_case.id_test_case'], ),
        sa.PrimaryKeyConstraint('id_result_test_case'),
        schema='testlive',
        comment='Result Test Case Table'
    )
    op.create_index(op.f('ix_testlive_t_result_test_case_id_release'), 't_result_test_case', ['id_release'], unique=False, schema='testlive')
    op.create_index(op.f('ix_testlive_t_result_test_case_id_test_case'), 't_result_test_case', ['id_test_case'], unique=False, schema='testlive')

    op.create_table('t_result_test_step',
        sa.Column('id_result_test_step', sa.Integer(), autoincrement=True, nullable=False, comment='ID Result Test Step'),
        sa.Column('id_result_test_case', sa.Integer(), nullable=False, comment='ID Result Test Case'),
        sa.Column('id_test_step', sa.Integer(), nullable=False, comment='ID Test Case'),
        sa.Column('id_status', sa.Integer(), nullable=True, comment='ID Status'),
        sa.Column('result', sa.Text(), nullable=True, comment='Fact Result'),
        sa.ForeignKeyConstraint(['id_result_test_case'], ['testlive.t_result_test_case.id_result_test_case'], ),
        sa.ForeignKeyConstraint(['id_status'], ['testlive.t_status.id_status'], ),
        sa.ForeignKeyConstraint(['id_test_step'], ['testlive.t_test_case.id_test_case'], ),
        sa.PrimaryKeyConstraint('id_result_test_step'),
        schema='testlive',
        comment='Result Test Step'
    )
    op.create_index(op.f('ix_testlive_t_result_test_step_id_result_test_case'), 't_result_test_step', ['id_result_test_case'], unique=False, schema='testlive')
    op.create_index(op.f('ix_testlive_t_result_test_step_id_status'), 't_result_test_step', ['id_status'], unique=False, schema='testlive')
    op.create_index(op.f('ix_testlive_t_result_test_step_id_test_step'), 't_result_test_step', ['id_test_step'], unique=False, schema='testlive')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_testlive_t_result_test_step_id_test_step'), table_name='t_result_test_step', schema='testlive')
    op.drop_index(op.f('ix_testlive_t_result_test_step_id_status'), table_name='t_result_test_step', schema='testlive')
    op.drop_index(op.f('ix_testlive_t_result_test_step_id_result_test_case'), table_name='t_result_test_step', schema='testlive')
    op.drop_table('t_result_test_step', schema='testlive')
    op.drop_index(op.f('ix_testlive_t_result_test_case_id_test_case'), table_name='t_result_test_case', schema='testlive')
    op.drop_index(op.f('ix_testlive_t_result_test_case_id_release'), table_name='t_result_test_case', schema='testlive')
    op.drop_table('t_result_test_case', schema='testlive')
    op.drop_index(op.f('ix_testlive_t_test_step_id_test_plan'), table_name='t_test_step', schema='testlive')
    op.drop_table('t_test_step', schema='testlive')
    op.drop_index(op.f('ix_testlive_t_test_case_id_test_plan'), table_name='t_test_case', schema='testlive')
    op.drop_table('t_test_case', schema='testlive')
    op.drop_index(op.f('ix_testlive_t_test_plan_id_parent'), table_name='t_test_plan', schema='testlive')
    op.drop_index(op.f('ix_testlive_t_test_plan_id_organization'), table_name='t_test_plan', schema='testlive')
    op.drop_table('t_test_plan', schema='testlive')
    op.drop_index(op.f('ix_testlive_t_release_id_organization'), table_name='t_release', schema='testlive')
    op.drop_table('t_release', schema='testlive')
    op.drop_table('t_status', schema='testlive')
    op.drop_table('t_organization', schema='testlive')
