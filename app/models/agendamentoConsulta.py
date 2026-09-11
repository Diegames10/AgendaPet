from datetime import datetime

from app import db


class AgendamentoConsulta(db.Model):
    __tablename__ = "agendamentos"

    id = db.Column(db.Integer, primary_key=True)

    tipo = db.Column(
        db.String(50),
        nullable=False
    )

    data = db.Column(
        db.Date,
        nullable=False
    )

    horario = db.Column(
        db.Time,
        nullable=False
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="Agendado"
    )

    observacoes = db.Column(
        db.Text,
        nullable=True
    )

    criado_em = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    lembrete_24h_enviado_em = db.Column(
        db.DateTime,
        nullable=True
    )

    pet_id = db.Column(
        db.Integer,
        db.ForeignKey("pets.id"),
        nullable=False
    )

    tutor_id = db.Column(
            db.Integer,
            db.ForeignKey("usuarios.id"),
            nullable=False
        )
    
    pet = db.relationship(
        "Pet",
        back_populates="agendamentos"
    )
    
    tutor = db.relationship(
        "Usuario",
        foreign_keys=[tutor_id],
        back_populates="agendamentos"
    )

    def __repr__(self):
        return (
            f"<Agendamento {self.tipo} "
            f"- {self.data} {self.horario}>"
        )
        
    veterinario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=True
    )


    veterinario = db.relationship(
        "Usuario",
        foreign_keys=[veterinario_id],
        back_populates="agendamentos_como_veterinario"
    )
   
    historico = db.relationship(
        "Historico",
        back_populates="agendamento",
        uselist=False
    ) 