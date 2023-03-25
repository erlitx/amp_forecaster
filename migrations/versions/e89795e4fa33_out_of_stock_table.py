"""Out_of_stock_table

Revision ID: e89795e4fa33
Revises: bfc970bbdec4
Create Date: 2023-03-25 06:35:21.325408

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e89795e4fa33'
down_revision = 'bfc970bbdec4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('out_of_stock_products',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=True),
    sa.Column('quantity_reserved', sa.Integer(), nullable=True),
    sa.Column('quantity_available', sa.Integer(), nullable=True),
    sa.Column('inventory_date', sa.DateTime(), nullable=True),
    sa.Column('out_of_stock', sa.Boolean(), nullable=True),
    sa.Column('product_id', sa.Integer(), nullable=True),
    sa.Column('warehouse_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
    sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('out_of_stock_products')
    # ### end Alembic commands ###
