"""Initial migration

Revision ID: 579b6acb5615
Revises: 
Create Date: 2022-05-07 16:12:35.119575

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '579b6acb5615'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('bio', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'bio')
    # ### end Alembic commands ###