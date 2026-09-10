# Copyright 2026 Cloudbase Solutions Srl
# All Rights Reserved.

"""add parent_task_id and inline to task

Revision ID: 026
Revises: 025
Create Date: 2026-09-10 14:00:00.000000
"""

import sqlalchemy
from alembic import op

# revision identifiers, used by Alembic.
revision = "026"
down_revision = "025"
branch_labels = None
depends_on = None


def upgrade():
    inspector = sqlalchemy.inspect(op.get_bind())
    columns = [c["name"] for c in inspector.get_columns("task")]
    if "parent_task_id" not in columns:
        op.add_column(
            "task",
            sqlalchemy.Column(
                "parent_task_id",
                sqlalchemy.String(36),
                sqlalchemy.ForeignKey("task.id"),
                nullable=True,
            ),
        )
    if "inline" not in columns:
        op.add_column(
            "task",
            sqlalchemy.Column(
                "inline",
                sqlalchemy.Boolean,
                nullable=False,
                server_default=sqlalchemy.text("0"),
            ),
        )


def downgrade():
    raise NotImplementedError()
