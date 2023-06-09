"""correct mistake

Revision ID: 295063f05364
Revises: 3f637799f62e
Create Date: 2023-03-24 14:26:43.906216

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '295063f05364'
down_revision = '3f637799f62e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('inventories', schema=None) as batch_op:
        batch_op.add_column(sa.Column('quantity_reserved', sa.Integer(), nullable=True))
        batch_op.drop_column('qauntity_reserved')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('inventories', schema=None) as batch_op:
        batch_op.add_column(sa.Column('qauntity_reserved', sa.INTEGER(), autoincrement=False, nullable=True))
        batch_op.drop_column('quantity_reserved')

    # ### end Alembic commands ###
