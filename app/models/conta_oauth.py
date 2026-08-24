from datetime import datetime

from app import db


class ContaOAuth(db.Model):

    __tablename__ = "contas_oauth"

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
        index=True
    )

    provedor = db.Column(
        db.String(20),
        nullable=False
    )

    provedor_usuario_id = db.Column(
        db.String(255),
        nullable=False
    )

    email_provedor = db.Column(
        db.String(255),
        nullable=True
    )

    criado_em = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    usuario = db.relationship(
        "Usuario",
        back_populates="contas_oauth"
    )

    __table_args__ = (

        db.UniqueConstraint(
            "provedor",
            "provedor_usuario_id",
            name="uq_conta_oauth_provedor_usuario"
        ),

    )

    def __repr__(self):

        return (
            f"<ContaOAuth "
            f"{self.provedor}:"
            f"{self.provedor_usuario_id}>"
        )