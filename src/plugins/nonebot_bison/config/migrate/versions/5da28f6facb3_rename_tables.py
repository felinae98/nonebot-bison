"""rename tables

Revision ID: 5da28f6facb3
Revises: 5f3370328e44
Create Date: 2023-01-15 19:04:54.987491

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "5da28f6facb3"
down_revision = "5f3370328e44"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.rename_table("target", "nonebot_bison_target")
    op.rename_table("user", "nonebot_bison_user")
    op.rename_table("schedule_time_weight", "nonebot_bison_scheduletimeweight")
    op.rename_table("subscribe", "nonebot_bison_subscribe")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.rename_table("nonebot_bison_subscribe", "subscribe")
    op.rename_table("nonebot_bison_scheduletimeweight", "schedule_time_weight")
    op.rename_table("nonebot_bison_user", "user")
    op.rename_table("nonebot_bison_target", "target")
    # ### end Alembic commands ###
