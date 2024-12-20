"""add employee education table

Revision ID: b899a7c89ca6
Revises: 9d0a4010c042
Create Date: 2024-11-29 14:02:04.737325

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'b899a7c89ca6'
down_revision = '9d0a4010c042'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('employees', schema=None) as batch_op:
        batch_op.drop_index('user_id')
        batch_op.drop_constraint('employees_ibfk_1', type_='foreignkey')
        batch_op.drop_column('address')
        batch_op.drop_column('user_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('employees', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('address', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=200), nullable=True))
        batch_op.create_foreign_key('employees_ibfk_1', 'users', ['user_id'], ['id'])
        batch_op.create_index('user_id', ['user_id'], unique=True)

    # ### end Alembic commands ###
