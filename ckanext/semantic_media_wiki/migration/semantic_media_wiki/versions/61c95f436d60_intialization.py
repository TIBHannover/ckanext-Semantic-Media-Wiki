"""intialization

Revision ID: 61c95f436d60
Revises: 
Create Date: 2021-10-22 13:30:05.495509

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '61c95f436d60'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
     op.create_table(
        'resource_equipment_link',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('resource_id', sa.UnicodeText(), sa.ForeignKey('resource.id'), nullable=False),
        sa.Column('url', sa.UnicodeText(), nullable=False),
        sa.Column('link_name', sa.UnicodeText()),
        sa.Column('create_at', sa.DateTime(timezone=False), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=False), nullable=False),
    )


def downgrade():
   op.drop_table('resource_equipment_link')
