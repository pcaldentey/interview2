"""add_fields_to_user_and_organisation_v2

Revision ID: 2100cccd5a57
Revises: af98f6e5a276
Create Date: 2021-01-12 08:00:57.579067

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2100cccd5a57'
down_revision = 'af98f6e5a276'
branch_labels = None
depends_on = None

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('organisations', sa.Column('enable_user_login', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('users', sa.Column('state', sa.Integer(), nullable=True, server_default='0'))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'state')
    op.drop_column('organisations', 'enable_user_login')
    # ### end Alembic commands ###