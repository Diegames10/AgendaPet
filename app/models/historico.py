from datetime import datetime

from app import db


class Historico(db.Model):

    __tablename__ = "historicos"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    data_atendimento = db.Column(
        db.Date,
        nullable=False,
        default=datetime.utcnow
    )

    tipo_atendimento = db.Column(
        db.String(100),
        nullable=False
    )

    diagnostico = db.Column(
        db.Text,
        nullable=True
    )

    tratamento = db.Column(
        db.Text,
        nullable=True
    )

    observacoes = db.Column(
        db.Text,
        nullable=True
    )

    pet_id = db.Column(
        db.Integer,
        db.ForeignKey("pets.id"),
        nullable=False
    )

    veterinario_id = db.Column(
        db.Integer,
        db.ForeignKey("veterinarios.id"),
        nullable=True
    )

    agendamento_id = db.Column(
        db.Integer,
        db.ForeignKey("agendamentos.id"),
        nullable=True
    )

    pet = db.relationship(
        "Pet",
        backref="historicos"
    )

    veterinario = db.relationship(
        "Veterinario",
        backref="historicos"
    )

    agendamento = db.relationship(
        "AgendamentoConsulta",
        back_populates="historico"
    )

    def __repr__(self):
        return f"<Historico {self.id} - {self.tipo_atendimento}>"