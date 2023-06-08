"""initiation

Revision ID: 6aaf13631cdf
Revises: 
Create Date: 2023-06-08 13:31:43.017895

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6aaf13631cdf'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'dataset_protocol_link',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('dataset_id', sa.UnicodeText(), sa.ForeignKey('package.id'), nullable=False),
        sa.Column('protocol_url', sa.UnicodeText(), nullable=False),
        sa.Column('protocol_name', sa.UnicodeText()),
        sa.Column('created_at', sa.DateTime(timezone=False), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=False), nullable=False),
    )


def downgrade():
    op.drop_table('dataset_protocol_link')
