"""empty message

Revision ID: 7632d88b0cb8
Revises: 8385449aba16
Create Date: 2024-09-14 17:11:11.549582

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '7632d88b0cb8'
down_revision = '8385449aba16'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('testcases', schema=None) as batch_op:
        batch_op.add_column(sa.Column('content', sa.Text(), nullable=False))
        batch_op.add_column(sa.Column('assignment_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key(None, 'assignments', ['assignment_id'], ['id'])
        batch_op.drop_column('md5')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('testcases', schema=None) as batch_op:
        batch_op.add_column(sa.Column('md5', mysql.VARCHAR(collation='utf8mb4_general_ci', length=32), nullable=False))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('assignment_id')
        batch_op.drop_column('content')

    # ### end Alembic commands ###