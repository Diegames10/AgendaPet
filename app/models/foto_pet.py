from datetime import datetime

from app import db


class FotoPet(db.Model):
    """
    Relaciona um pet às suas fotos.

    Regras:
    - cada pet poderá possuir no máximo três fotos;
    - as posições válidas são 1, 2 e 3;
    - apenas uma foto deverá ser marcada como principal;
    - a primeira foto cadastrada será definida como principal
      pela lógica da rota de upload.
    """

    __tablename__ = "fotos_pets"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    pet_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "pets.id",
            ondelete="CASCADE"
        ),
        nullable=False,
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

    posicao = db.Column(
        db.SmallInteger,
        nullable=False
    )

    principal = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    descricao = db.Column(
        db.String(255),
        nullable=True
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

    pet = db.relationship(
        "Pet",
        back_populates="fotos"
    )

    arquivo = db.relationship(
        "Arquivo",
        cascade="all, delete-orphan",
        single_parent=True,
        uselist=False,
        lazy="joined"
    )

    __table_args__ = (
        db.CheckConstraint(
            "posicao >= 1 AND posicao <= 3",
            name="ck_foto_pet_posicao_entre_1_e_3"
        ),
        db.UniqueConstraint(
            "pet_id",
            "posicao",
            name="uq_foto_pet_pet_posicao"
        ),
        db.Index(
            "uq_foto_pet_principal_por_pet",
            "pet_id",
            unique=True,
            postgresql_where=db.text("principal = true")
        ),
    )

    def __repr__(self):
        return (
            f"<FotoPet {self.id} "
            f"- pet_id={self.pet_id} "
            f"- posicao={self.posicao} "
            f"- principal={self.principal}>"
        )