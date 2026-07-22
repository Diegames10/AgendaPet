from datetime import datetime

from app import db


class FotoUsuario(db.Model):
    """
    Relaciona um usuário à sua foto de perfil.

    Cada usuário poderá possuir apenas uma foto de perfil.
    O conteúdo da imagem ficará armazenado na tabela arquivos.
    """

    __tablename__ = "fotos_usuarios"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "usuarios.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        unique=True,
        index=True
    )

    arquivo_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "arquivos.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        unique=True,
        index=True
    )

    criado_em = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    atualizado_em = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    usuario = db.relationship(
        "Usuario",
        back_populates="foto_perfil"
    )

    arquivo = db.relationship(
        "Arquivo",
        cascade="all, delete-orphan",
        single_parent=True,
        uselist=False,
        lazy="joined"
    )

    def __repr__(self):
        return (
            f"<FotoUsuario {self.id} "
            f"- usuario_id={self.usuario_id}>"
        )