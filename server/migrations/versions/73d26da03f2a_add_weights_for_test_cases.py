"""add weights for test cases

Revision ID: 73d26da03f2a
Revises: 4d1d336b8d34
Create Date: 2024-09-12 20:23:28.937767

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '73d26da03f2a'
down_revision = '4d1d336b8d34'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('assignments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('weights', sa.JSON(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('assignments', schema=None) as batch_op:
        batch_op.drop_column('weights')

    # ### end Alembic commands ###
