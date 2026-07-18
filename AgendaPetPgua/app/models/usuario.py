from datetime import datetime

from flask_login import UserMixin

from app import db


class Usuario(db.Model, UserMixin):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)

    nome = db.Column(
        db.String(120),
        nullable=False
    )

    cpf = db.Column(
        db.String(14),
        unique=True,
        nullable=False,
        index=True
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False,
        index=True
    )

    telefone = db.Column(
        db.String(20),
        nullable=True
    )

    senha_hash = db.Column(
        db.String(255),
        nullable=False
    )

    tipo_usuario = db.Column(
        db.String(20),
        nullable=False,
        default="CLIENTE"
    )

    ativo = db.Column(
        db.Boolean,
        nullable=False,
        default=True
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

    pets = db.relationship(
        "Pet",
        back_populates="tutor",
        cascade="all, delete-orphan"
    )
    def __repr__(self):
        return f"<Usuario {self.email}>"
    
    agendamentos = db.relationship(
    "AgendamentoConsulta",
    back_populates="tutor",
    cascade="all, delete-orphan"
)
    