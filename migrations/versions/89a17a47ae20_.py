"""empty message

Revision ID: 89a17a47ae20
Revises: a8c3bc6d8601
Create Date: 2021-10-16 18:29:39.013974

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '89a17a47ae20'
down_revision = 'a8c3bc6d8601'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venue', sa.Column('genres', sa.ARRAY(sa.String()), nullable=True))
    op.drop_column('venue', 'genresl')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venue', sa.Column('genresl', postgresql.ARRAY(sa.VARCHAR()), autoincrement=False, nullable=True))
    op.drop_column('venue', 'genres')
    # ### end Alembic commands ###