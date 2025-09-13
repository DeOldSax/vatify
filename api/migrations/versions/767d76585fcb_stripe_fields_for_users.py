"""stripe fields for users

Revision ID: 767d76585fcb
Revises: 3cfeac80b2f7
Create Date: 2025-09-13 17:35:30.036505

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '767d76585fcb'
down_revision: Union[str, Sequence[str], None] = '3cfeac80b2f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
     # Spalten hinzufügen (idempotent: IF NOT EXISTS gibt es bei Alembic/SQLA nicht portable,
    # deshalb einfach hinzufügen; bei erneutem Ausführen schlägt es erwartungsgemäß fehl.)
    op.add_column("users", sa.Column("stripe_customer_id", sa.String(), nullable=True))
    op.add_column("users", sa.Column("stripe_subscription_id", sa.String(), nullable=True))
    op.add_column("users", sa.Column("subscription_status", sa.String(), nullable=True))
    op.add_column("users", sa.Column("current_period_end", sa.DateTime(timezone=True), nullable=True))
    op.add_column("users", sa.Column("vat_number", sa.String(), nullable=True))
    op.add_column("users", sa.Column("tax_exempt", sa.String(), nullable=True))

    # Index auf customer_id für schnelle lookups
    op.create_index(
        "ix_users_stripe_customer_id",
        "users",
        ["stripe_customer_id"],
        unique=False,
        postgresql_where=sa.text("stripe_customer_id IS NOT NULL"),
    )

    # Partieller Unique-Index auf subscription_id (nur wenn nicht NULL)
    op.create_index(
        "uq_users_stripe_subscription_id_not_null",
        "users",
        ["stripe_subscription_id"],
        unique=True,
        postgresql_where=sa.text("stripe_subscription_id IS NOT NULL"),
    )


def downgrade() -> None:
    """Downgrade schema."""
     # Indizes zuerst entfernen
    op.drop_index("uq_users_stripe_subscription_id_not_null", table_name="users")
    op.drop_index("ix_users_stripe_customer_id", table_name="users")

    # Spalten entfernen
    op.drop_column("users", "tax_exempt")
    op.drop_column("users", "vat_number")
    op.drop_column("users", "current_period_end")
    op.drop_column("users", "subscription_status")
    op.drop_column("users", "stripe_subscription_id")
    op.drop_column("users", "stripe_customer_id")
