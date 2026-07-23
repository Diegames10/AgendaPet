"""adiciona campos clinicos ao prontuario

Revision ID: 04aea8325a8a
Revises: 7fd06330a8e3
Create Date: 2026-07-22 18:17:35.326162

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '04aea8325a8a'
down_revision = '7fd06330a8e3'
branch_labels = None
depends_on = None


def upgrade():
    # Novos campos clínicos: podem permanecer vazios
    with op.batch_alter_table("historicos", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("motivo_consulta", sa.Text(), nullable=True)
        )

        batch_op.add_column(
            sa.Column("anamnese", sa.Text(), nullable=True)
        )

        batch_op.add_column(
            sa.Column("exame_clinico", sa.Text(), nullable=True)
        )

        batch_op.add_column(
            sa.Column(
                "peso_atendimento",
                sa.Numeric(precision=6, scale=2),
                nullable=True
            )
        )

        batch_op.add_column(
            sa.Column(
                "temperatura",
                sa.Numeric(precision=4, scale=1),
                nullable=True
            )
        )

        batch_op.add_column(
            sa.Column(
                "frequencia_cardiaca",
                sa.Integer(),
                nullable=True
            )
        )

        batch_op.add_column(
            sa.Column(
                "frequencia_respiratoria",
                sa.Integer(),
                nullable=True
            )
        )

        batch_op.add_column(
            sa.Column(
                "retorno_previsto",
                sa.Date(),
                nullable=True
            )
        )

        # O valor temporário preenche os registros antigos
        batch_op.add_column(
            sa.Column(
                "criado_em",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP")
            )
        )

        batch_op.add_column(
            sa.Column(
                "atualizado_em",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP")
            )
        )

        batch_op.create_unique_constraint(
            "uq_historicos_agendamento_id",
            ["agendamento_id"]
        )

    # Remove o default temporário do banco.
    # Os próximos registros utilizarão os defaults do modelo Python.
    with op.batch_alter_table("historicos", schema=None) as batch_op:
        batch_op.alter_column(
            "criado_em",
            server_default=None
        )

        batch_op.alter_column(
            "atualizado_em",
            server_default=None
        )


def downgrade():
    with op.batch_alter_table("historicos", schema=None) as batch_op:
        batch_op.drop_constraint(
            "uq_historicos_agendamento_id",
            type_="unique"
        )

        batch_op.drop_column("atualizado_em")
        batch_op.drop_column("criado_em")
        batch_op.drop_column("retorno_previsto")
        batch_op.drop_column("frequencia_respiratoria")
        batch_op.drop_column("frequencia_cardiaca")
        batch_op.drop_column("temperatura")
        batch_op.drop_column("peso_atendimento")
        batch_op.drop_column("exame_clinico")
        batch_op.drop_column("anamnese")
        batch_op.drop_column("motivo_consulta")
