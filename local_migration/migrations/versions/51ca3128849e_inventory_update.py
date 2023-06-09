"""Inventory update

Revision ID: 51ca3128849e
Revises: ecf75ac5ea7f
Create Date: 2023-03-23 16:49:18.557209

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '51ca3128849e'
down_revision = 'ecf75ac5ea7f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('inventories', schema=None) as batch_op:
        batch_op.add_column(sa.Column('qauntity_reserved', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('quantity_available', sa.Integer(), nullable=True))

    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.add_column(sa.Column('categ_id', sa.String(length=128), nullable=True))
        batch_op.add_column(sa.Column('sale_ok', sa.Boolean(), nullable=True))
        batch_op.alter_column('name',
               existing_type=sa.VARCHAR(length=64),
               type_=sa.String(length=128),
               existing_nullable=True)
        batch_op.create_index(batch_op.f('ix_products_categ_id'), ['categ_id'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_products_categ_id'))
        batch_op.alter_column('name',
               existing_type=sa.String(length=128),
               type_=sa.VARCHAR(length=64),
               existing_nullable=True)
        batch_op.drop_column('sale_ok')
        batch_op.drop_column('categ_id')

    with op.batch_alter_table('inventories', schema=None) as batch_op:
        batch_op.drop_column('quantity_available')
        batch_op.drop_column('qauntity_reserved')

    # ### end Alembic commands ###
