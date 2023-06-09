"""odoo_id_tmpl

Revision ID: cb3034482d8d
Revises: e89795e4fa33
Create Date: 2023-03-28 07:03:36.398021

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cb3034482d8d'
down_revision = 'e89795e4fa33'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.add_column(sa.Column('odoo_tmpl_id', sa.Integer(), nullable=True))
        batch_op.create_index(batch_op.f('ix_products_odoo_tmpl_id'), ['odoo_tmpl_id'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_products_odoo_tmpl_id'))
        batch_op.drop_column('odoo_tmpl_id')

    # ### end Alembic commands ###
