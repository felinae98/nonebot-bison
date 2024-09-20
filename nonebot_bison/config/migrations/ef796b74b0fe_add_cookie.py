"""empty message

Revision ID: ef796b74b0fe
Revises: f9baef347cc8
Create Date: 2024-09-13 00:34:08.601438

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy import Text
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "ef796b74b0fe"
down_revision = "f9baef347cc8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "nonebot_bison_cookie",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("site_name", sa.String(length=100), nullable=False),
        sa.Column("content", sa.String(length=1024), nullable=False),
        sa.Column("last_usage", sa.DateTime(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("cd_milliseconds", sa.Integer(), nullable=False),
        sa.Column("is_universal", sa.Boolean(), nullable=False),
        sa.Column("is_anonymous", sa.Boolean(), nullable=False),
        sa.Column("tags", sa.JSON().with_variant(postgresql.JSONB(astext_type=Text()), "postgresql"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_nonebot_bison_cookie")),
    )
    op.create_table(
        "nonebot_bison_cookietarget",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("target_id", sa.Integer(), nullable=False),
        sa.Column("cookie_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["cookie_id"],
            ["nonebot_bison_cookie.id"],
            name=op.f("fk_nonebot_bison_cookietarget_cookie_id_nonebot_bison_cookie"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["target_id"],
            ["nonebot_bison_target.id"],
            name=op.f("fk_nonebot_bison_cookietarget_target_id_nonebot_bison_target"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_nonebot_bison_cookietarget")),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("nonebot_bison_cookietarget")
    op.drop_table("nonebot_bison_cookie")
    # ### end Alembic commands ###