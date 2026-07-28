from datetime import datetime

from app import db


class Pet(db.Model):
    __tablename__ = "pets"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nome = db.Column(
        db.String(100),
        nullable=False
    )

    especie = db.Column(
        db.String(50),
        nullable=False
    )

    raca = db.Column(
        db.String(100),
        nullable=True
    )

    sexo = db.Column(
        db.String(20),
        nullable=True
    )

    data_nascimento = db.Column(
        db.Date,
        nullable=True
    )

    peso = db.Column(
        db.Float,
        nullable=True
    )

    cor = db.Column(
        db.String(50),
        nullable=True
    )

    observacoes = db.Column(
        db.Text,
        nullable=True
    )

    tutor_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False
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
    
    

    # =====================================================
    # RELACIONAMENTOS
    # =====================================================

    tutor = db.relationship(
        "Usuario",
        back_populates="pets"
    )

    agendamentos = db.relationship(
        "AgendamentoConsulta",
        back_populates="pet",
        cascade="all, delete-orphan"
    )

    historicos = db.relationship(
        "Historico",
        back_populates="pet",
        cascade="all, delete-orphan"
    )
    
    fotos = db.relationship(
        "FotoPet",
        back_populates="pet",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="FotoPet.posicao.asc()"
    )

    @property
    def foto_principal(self):
        """
        Retorna a foto marcada como principal.

        Caso nenhuma esteja marcada, retorna a primeira foto
        disponível pela ordem de posição.
        """

        if not self.fotos:
            return None

        for foto in self.fotos:
            if foto.principal:
                return foto

        return self.fotos[0]

    def __repr__(self):
        return f"<Pet {self.nome} - tutor_id={self.tutor_id}>"