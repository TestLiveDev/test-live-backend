"""initial schema

Revision ID: 9f3a2b6c1d4e
Revises:
Create Date: 2026-03-24 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "9f3a2b6c1d4e"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


STATUS_TABLE = sa.table(
    "statuses",
    sa.column("name", sa.String(length=100)),
    sa.column("code", sa.String(length=50)),
    sa.column("category", sa.String(length=50)),
)


def upgrade() -> None:
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "statuses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_statuses_code"), "statuses", ["code"], unique=True)
    op.bulk_insert(
        STATUS_TABLE,
        [
            {
                "name": "Планируется",
                "code": "planning",
                "category": "release_priority",
            },
            {
                "name": "В работе",
                "code": "in_progress",
                "category": "release_priority",
            },
            {
                "name": "Релизнут",
                "code": "released",
                "category": "release_priority",
            },
            {"name": "Низкий", "code": "low", "category": "priority"},
            {"name": "Средний", "code": "medium", "category": "priority"},
            {"name": "Высокий", "code": "high", "category": "priority"},
            {
                "name": "Критический",
                "code": "critical",
                "category": "priority",
            },
            {"name": "Не запущен", "code": "not_run", "category": "result"},
            {"name": "Пройден", "code": "passed", "category": "result"},
            {"name": "Провален", "code": "failed", "category": "result"},
            {"name": "Заблокирован", "code": "blocked", "category": "result"},
            {"name": "Пропущен", "code": "skipped", "category": "result"},
        ],
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_table(
        "project_members",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("id_project", sa.Integer(), nullable=False),
        sa.Column("id_user", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["id_project"], ["projects.id"]),
        sa.ForeignKeyConstraint(["id_user"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "id_project", "id_user", name="uq_project_members_project_user"
        ),
    )
    op.create_table(
        "releases",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("id_project", sa.Integer(), nullable=False),
        sa.Column("id_status", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["id_project"], ["projects.id"]),
        sa.ForeignKeyConstraint(["id_status"], ["statuses.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "test_plans",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("id_project", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["id_project"], ["projects.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "test_cases",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("id_test_plan", sa.Integer(), nullable=False),
        sa.Column("id_priority", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("preconditions", sa.Text(), nullable=True),
        sa.Column("postconditions", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["id_priority"], ["statuses.id"]),
        sa.ForeignKeyConstraint(["id_test_plan"], ["test_plans.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "release_test_plans",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("id_release", sa.Integer(), nullable=False),
        sa.Column("id_test_plan", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["id_release"], ["releases.id"]),
        sa.ForeignKeyConstraint(["id_test_plan"], ["test_plans.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "id_release", "id_test_plan", name="uq_release_test_plans_release_plan"
        ),
    )
    op.create_table(
        "release_test_cases",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("id_release", sa.Integer(), nullable=False),
        sa.Column("id_test_case", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["id_release"], ["releases.id"]),
        sa.ForeignKeyConstraint(["id_test_case"], ["test_cases.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "id_release", "id_test_case", name="uq_release_test_cases_release_case"
        ),
    )
    op.create_table(
        "test_results",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("id_test_case", sa.Integer(), nullable=False),
        sa.Column("id_release", sa.Integer(), nullable=False),
        sa.Column("id_status", sa.Integer(), nullable=False),
        sa.Column("executed_at", sa.DateTime(), nullable=False),
        sa.Column("executed_by", sa.String(length=255), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["id_release"], ["releases.id"]),
        sa.ForeignKeyConstraint(["id_status"], ["statuses.id"]),
        sa.ForeignKeyConstraint(["id_test_case"], ["test_cases.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "test_steps",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("id_test_case", sa.Integer(), nullable=False),
        sa.Column("order_num", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=500), nullable=False),
        sa.Column("expected_result", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["id_test_case"], ["test_cases.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "test_result_attachments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("id_test_result", sa.Integer(), nullable=False),
        sa.Column("id_project", sa.Integer(), nullable=False),
        sa.Column("id_uploaded_by", sa.Integer(), nullable=True),
        sa.Column("bucket", sa.String(length=255), nullable=False),
        sa.Column("object_key", sa.String(length=1024), nullable=False),
        sa.Column("original_name", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=255), nullable=True),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("etag", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["id_project"], ["projects.id"]),
        sa.ForeignKeyConstraint(["id_test_result"], ["test_results.id"]),
        sa.ForeignKeyConstraint(["id_uploaded_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("object_key"),
    )


def downgrade() -> None:
    op.drop_table("test_result_attachments")
    op.drop_table("test_steps")
    op.drop_table("test_results")
    op.drop_table("release_test_cases")
    op.drop_table("release_test_plans")
    op.drop_table("test_cases")
    op.drop_table("test_plans")
    op.drop_table("releases")
    op.drop_table("project_members")
    op.drop_table("users")
    op.drop_index(op.f("ix_statuses_code"), table_name="statuses")
    op.drop_table("statuses")
    op.drop_table("projects")
