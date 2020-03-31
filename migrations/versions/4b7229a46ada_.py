"""empty message

Revision ID: 4b7229a46ada
Revises: 
Create Date: 2020-03-28 21:04:54.409960

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4b7229a46ada'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('spotify_id', sa.String(), nullable=True),
    sa.Column('slack_id', sa.String(), nullable=True),
    sa.Column('display_name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    # ### end Alembic commands ###