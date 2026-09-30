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

TABLE_NAME = 'resource_equipment_link'


def upgrade():
    # Older releases exposed this migration as ``semantic_media_wiki``. Keep
    # upgrades from them safe while establishing machine_link's version record.
    if sa.inspect(op.get_bind()).has_table(TABLE_NAME):
        return

    op.create_table(
        TABLE_NAME,
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('resource_id', sa.UnicodeText(), sa.ForeignKey('resource.id'), nullable=False),
        sa.Column('url', sa.UnicodeText(), nullable=False),
        sa.Column('link_name', sa.UnicodeText()),
        sa.Column('create_at', sa.DateTime(timezone=False), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=False), nullable=False),
    )


def downgrade():
    op.drop_table(TABLE_NAME)
