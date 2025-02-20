"""init

Revision ID: a88f785891f4
Revises:
Create Date: 2024-01-03 16:36:23.018211

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "a88f785891f4"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("first_name", sa.String(), nullable=True),
        sa.Column("last_name", sa.String(), nullable=True),
        sa.Column("cpf", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("phone", sa.String(), nullable=False),
        sa.Column("permission", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("is_superuser", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_cpf"), "users", ["cpf"], unique=True)
    op.create_index(op.f("ix_user_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_user_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_user_first_name"), "users", ["first_name"], unique=False)
    op.create_index(op.f("ix_user_last_name"), "users", ["last_name"], unique=False)
    op.create_index(op.f("ix_user_phone"), "users", ["phone"], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_user_phone"), table_name="users")
    op.drop_index(op.f("ix_user_first_name"), table_name="users")
    op.drop_index(op.f("ix_user_last_name"), table_name="users")
    op.drop_index(op.f("ix_user_id"), table_name="users")
    op.drop_index(op.f("ix_user_email"), table_name="users")
    op.drop_index(op.f("ix_user_cpf"), table_name="users")
    op.drop_table("users")
    # ### end Alembic commands ###
