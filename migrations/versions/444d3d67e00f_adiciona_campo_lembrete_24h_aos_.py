"""adiciona campo lembrete 24h aos agendamentos

Revision ID: 444d3d67e00f
Revises: bfeadff8d4b1
Create Date: 2026-09-21 19:31:57.690271

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '444d3d67e00f'
down_revision = 'bfeadff8d4b1'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'agendamentos',
        sa.Column(
            'lembrete_24h_enviado_em',
            sa.DateTime(),
            nullable=True
        )
    )


def downgrade():
    op.drop_column(
        'agendamentos',
        'lembrete_24h_enviado_em'
    )
