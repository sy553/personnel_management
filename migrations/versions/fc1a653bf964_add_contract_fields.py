"""add contract fields

Revision ID: fc1a653bf964
Revises: cf4bb5557511
Create Date: 2024-11-29 13:23:12.304596

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'fc1a653bf964'
down_revision = 'cf4bb5557511'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('employee_education')
    with op.batch_alter_table('employee_contracts', schema=None) as batch_op:
        batch_op.drop_index('number')

    op.drop_table('employee_contracts')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('employee_contracts',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('employee_no', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=50), nullable=False),
    sa.Column('number', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=100), nullable=False),
    sa.Column('type', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=50), nullable=False),
    sa.Column('duration', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('start_date', sa.DATE(), nullable=False),
    sa.Column('end_date', sa.DATE(), nullable=False),
    sa.Column('sign_date', sa.DATE(), nullable=False),
    sa.Column('status', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=20), nullable=False),
    sa.Column('created_by', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=50), nullable=True),
    sa.Column('updated_by', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=50), nullable=True),
    sa.Column('created_at', mysql.DATETIME(), nullable=True),
    sa.Column('updated_at', mysql.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['employee_no'], ['employees.employee_no'], name='employee_contracts_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_unicode_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    with op.batch_alter_table('employee_contracts', schema=None) as batch_op:
        batch_op.create_index('number', ['number'], unique=True)

    op.create_table('employee_education',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('employee_no', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=50), nullable=False),
    sa.Column('start_date', sa.DATE(), nullable=False),
    sa.Column('end_date', sa.DATE(), nullable=False),
    sa.Column('school', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=100), nullable=False),
    sa.Column('major', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=100), nullable=False),
    sa.Column('degree', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=50), nullable=False),
    sa.Column('description', mysql.TEXT(collation='utf8mb4_unicode_ci'), nullable=True),
    sa.Column('created_by', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=50), nullable=True),
    sa.Column('updated_by', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=50), nullable=True),
    sa.Column('created_at', mysql.DATETIME(), nullable=True),
    sa.Column('updated_at', mysql.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['employee_no'], ['employees.employee_no'], name='employee_education_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_unicode_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    # ### end Alembic commands ###
