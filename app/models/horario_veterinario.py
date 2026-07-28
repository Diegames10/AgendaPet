from app import db


class HorarioVeterinario(db.Model):
    __tablename__ = "horarios_veterinarios"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    veterinario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False
    )

    dia_semana = db.Column(
        db.Integer,
        nullable=False
    )
    # 0 = Segunda
    # 1 = Terça
    # 2 = Quarta
    # 3 = Quinta
    # 4 = Sexta
    # 5 = Sábado
    # 6 = Domingo

    hora_inicio = db.Column(
        db.Time,
        nullable=False
    )

    hora_fim = db.Column(
        db.Time,
        nullable=False
    )

    inicio_almoco = db.Column(
        db.Time
    )

    fim_almoco = db.Column(
        db.Time
    )

    intervalo_minutos = db.Column(
        db.Integer,
        nullable=False,
        default=30
    )

    ativo = db.Column(
        db.Boolean,
        default=True
    )

    veterinario = db.relationship(
        "Usuario",
        back_populates="horarios_trabalho"
    )