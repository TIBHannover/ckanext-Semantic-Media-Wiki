"""initialization

Revision ID: ea3d7799ce62
Revises: 
Create Date: 2022-04-06 13:42:08.704289

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ea3d7799ce62'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'resource_sample_link',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('resource_id', sa.UnicodeText(), sa.ForeignKey('resource.id'), nullable=False),
        sa.Column('sample_url', sa.UnicodeText(), nullable=False),
        sa.Column('sample_name', sa.UnicodeText()),
        sa.Column('create_at', sa.DateTime(timezone=False), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=False), nullable=False),
    )


def downgrade():
    op.drop_table('resource_sample_link')
