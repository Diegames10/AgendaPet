from datetime import datetime

from app import db


class Pet(db.Model):
    __tablename__ = "pets"

    id = db.Column(db.Integer, primary_key=True)

    nome = db.Column(db.String(100), nullable=False)

    especie = db.Column(db.String(50), nullable=False)

    raca = db.Column(db.String(100))

    sexo = db.Column(db.String(20))

    data_nascimento = db.Column(db.Date)

    peso = db.Column(db.Float)

    cor = db.Column(db.String(50))

    observacoes = db.Column(db.Text)

    tutor_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False
    )

    criado_em = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    atualizado_em = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    tutor = db.relationship(
        "Usuario",
        back_populates="pets"
    )
    
    agendamentos = db.relationship(
    "AgendamentoConsulta",
    back_populates="pet",
    cascade="all, delete-orphan"
)
    
