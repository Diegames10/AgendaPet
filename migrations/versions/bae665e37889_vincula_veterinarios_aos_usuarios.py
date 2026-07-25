"""vincula veterinarios aos usuarios

Revision ID: bae665e37889
Revises: 6c9fe05d9632
Create Date: 2026-07-24 22:40:28.339012

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bae665e37889'
down_revision = '6c9fe05d9632'
branch_labels = None
depends_on = None


def upgrade():
    # Remove primeiro as chaves estrangeiras que apontam
    # para a tabela antiga veterinarios.
    with op.batch_alter_table("agendamentos", schema=None) as batch_op:
        batch_op.drop_constraint(
            "agendamentos_veterinario_id_fkey",
            type_="foreignkey"
        )

    with op.batch_alter_table("historicos", schema=None) as batch_op:
        batch_op.drop_constraint(
            "historicos_veterinario_id_fkey",
            type_="foreignkey"
        )

    # Os IDs da tabela veterinarios antiga não necessariamente
    # correspondem aos IDs dos usuários veterinários.
    # Por segurança, remove os vínculos antigos.
    op.execute(
        "UPDATE agendamentos SET veterinario_id = NULL"
    )

    op.execute(
        "UPDATE historicos SET veterinario_id = NULL"
    )

    # Cria as novas chaves estrangeiras apontando para usuarios.
    with op.batch_alter_table("agendamentos", schema=None) as batch_op:
        batch_op.create_foreign_key(
            "agendamentos_veterinario_usuario_id_fkey",
            "usuarios",
            ["veterinario_id"],
            ["id"],
            ondelete="SET NULL"
        )

    with op.batch_alter_table("historicos", schema=None) as batch_op:
        batch_op.create_foreign_key(
            "historicos_veterinario_usuario_id_fkey",
            "usuarios",
            ["veterinario_id"],
            ["id"],
            ondelete="SET NULL"
        )

    # Agora a tabela antiga pode ser removida.
    op.drop_table("veterinarios")


def downgrade():
    # Primeiro recria a tabela antiga.
    op.create_table(
        "veterinarios",
        sa.Column(
            "id",
            sa.INTEGER(),
            autoincrement=True,
            nullable=False
        ),
        sa.Column(
            "nome",
            sa.VARCHAR(length=100),
            nullable=False
        ),
        sa.Column(
            "crmv",
            sa.VARCHAR(length=30),
            nullable=False
        ),
        sa.Column(
            "especialidade",
            sa.VARCHAR(length=100),
            nullable=True
        ),
        sa.Column(
            "telefone",
            sa.VARCHAR(length=20),
            nullable=True
        ),
        sa.Column(
            "email",
            sa.VARCHAR(length=120),
            nullable=True
        ),
        sa.Column(
            "ativo",
            sa.BOOLEAN(),
            nullable=True
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name=op.f("veterinarios_pkey")
        ),
        sa.UniqueConstraint(
            "crmv",
            name=op.f("veterinarios_crmv_key")
        )
    )

    # Remove os vínculos novos com usuarios.
    with op.batch_alter_table("agendamentos", schema=None) as batch_op:
        batch_op.drop_constraint(
            "agendamentos_veterinario_usuario_id_fkey",
            type_="foreignkey"
        )

    with op.batch_alter_table("historicos", schema=None) as batch_op:
        batch_op.drop_constraint(
            "historicos_veterinario_usuario_id_fkey",
            type_="foreignkey"
        )

    # Os valores foram zerados no upgrade, então podem ser
    # vinculados novamente à tabela antiga sem conflito.
    with op.batch_alter_table("agendamentos", schema=None) as batch_op:
        batch_op.create_foreign_key(
            "agendamentos_veterinario_id_fkey",
            "veterinarios",
            ["veterinario_id"],
            ["id"]
        )

    with op.batch_alter_table("historicos", schema=None) as batch_op:
        batch_op.create_foreign_key(
            "historicos_veterinario_id_fkey",
            "veterinarios",
            ["veterinario_id"],
            ["id"]
        )