from app import db


class Veterinario(db.Model):

    __tablename__ = "veterinarios"


    id = db.Column(
        db.Integer,
        primary_key=True
    )


    nome = db.Column(
        db.String(100),
        nullable=False
    )


    crmv = db.Column(
        db.String(30),
        unique=True,
        nullable=False
    )


    especialidade = db.Column(
        db.String(100),
        nullable=True
    )


    telefone = db.Column(
        db.String(20),
        nullable=True
    )


    email = db.Column(
        db.String(120),
        nullable=True
    )


    ativo = db.Column(
        db.Boolean,
        default=True
    )


    def __repr__(self):

        return f"<Veterinario {self.nome}>"
    
    agendamentos = db.relationship(
        "AgendamentoConsulta",
        back_populates="veterinario"
    )