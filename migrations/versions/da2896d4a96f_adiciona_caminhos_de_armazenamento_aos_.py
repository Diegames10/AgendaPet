"""adiciona caminhos de armazenamento aos arquivos

Revision ID: da2896d4a96f
Revises: 24aa2240351a
Create Date: 2026-08-18 19:16:02.474252
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "da2896d4a96f"
down_revision = "24aa2240351a"
branch_labels = None
depends_on = None


def upgrade():

    with op.batch_alter_table("arquivos", schema=None) as batch_op:

        batch_op.add_column(
            sa.Column(
                "caminho",
                sa.String(length=500),
                nullable=True
            )
        )

        batch_op.add_column(
            sa.Column(
                "caminho_miniatura",
                sa.String(length=500),
                nullable=True
            )
        )

        batch_op.create_unique_constraint(
            "uq_arquivos_caminho",
            ["caminho"]
        )

        batch_op.create_unique_constraint(
            "uq_arquivos_caminho_miniatura",
            ["caminho_miniatura"]
        )


def downgrade():

    with op.batch_alter_table("arquivos", schema=None) as batch_op:

        batch_op.drop_constraint(
            "uq_arquivos_caminho_miniatura",
            type_="unique"
        )

        batch_op.drop_constraint(
            "uq_arquivos_caminho",
            type_="unique"
        )

        batch_op.drop_column(
            "caminho_miniatura"
        )

        batch_op.drop_column(
            "caminho"
        )