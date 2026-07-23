from app import db


class Exame(db.Model):

    __tablename__ = "exames"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    historico_id = db.Column(
        db.Integer,
        db.ForeignKey("historicos.id"),
        nullable=False
    )

    nome = db.Column(
        db.String(150),
        nullable=False
    )

    categoria = db.Column(
        db.String(100),
        nullable=True
    )

    resultado = db.Column(
        db.Text,
        nullable=True
    )

    observacoes = db.Column(
        db.Text,
        nullable=True
    )

    data_exame = db.Column(
        db.Date,
        nullable=True
    )

    historico = db.relationship(
        "Historico",
        back_populates="exames"
    )