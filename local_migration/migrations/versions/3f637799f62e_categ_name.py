"""categ_name

Revision ID: 3f637799f62e
Revises: bf5cd7255fc4
Create Date: 2023-03-23 17:38:27.527645

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3f637799f62e'
down_revision = 'bf5cd7255fc4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.add_column(sa.Column('categ_name', sa.String(length=128), nullable=True))
        batch_op.drop_index('ix_products_categ_id')
        batch_op.create_index(batch_op.f('ix_products_categ_name'), ['categ_name'], unique=False)
        batch_op.drop_column('categ_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.add_column(sa.Column('categ_id', sa.VARCHAR(length=128), autoincrement=False, nullable=True))
        batch_op.drop_index(batch_op.f('ix_products_categ_name'))
        batch_op.create_index('ix_products_categ_id', ['categ_id'], unique=False)
        batch_op.drop_column('categ_name')

    # ### end Alembic commands ###
