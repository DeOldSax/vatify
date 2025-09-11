"""use timestamptz everywhere

Revision ID: 993df9f957ca
Revises: 30dcc8632ae0
Create Date: 2025-09-11 22:58:39.935084

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '993df9f957ca'
down_revision: Union[str, Sequence[str], None] = '30dcc8632ae0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
from alembic import op
import sqlalchemy as sa

def upgrade():
    # User.created_at
    op.alter_column("users", "created_at",
        type_=sa.DateTime(timezone=True),
        postgresql_using="created_at AT TIME ZONE 'UTC'"
    )

    # SessionToken.expires_at
    op.alter_column("sessions", "expires_at",
        type_=sa.DateTime(timezone=True),
        postgresql_using="expires_at AT TIME ZONE 'UTC'"
    )

    # ApiKey.created_at
    op.alter_column("api_keys", "created_at",
        type_=sa.DateTime(timezone=True),
        postgresql_using="created_at AT TIME ZONE 'UTC'"
    )

    # UsageCounter.timestamp
    op.alter_column("usage_counters", "timestamp",
        type_=sa.DateTime(timezone=True),
        postgresql_using="timestamp AT TIME ZONE 'UTC'"
    )

def downgrade():
    # zurück auf naive timestamps (nicht empfohlen)
    op.alter_column("usage_counters", "timestamp", type_=sa.DateTime(timezone=False))
    op.alter_column("api_keys", "created_at", type_=sa.DateTime(timezone=False))
    op.alter_column("sessions", "expires_at", type_=sa.DateTime(timezone=False))
    op.alter_column("users", "created_at", type_=sa.DateTime(timezone=False))
