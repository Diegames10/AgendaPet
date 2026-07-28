from datetime import date, datetime

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
        default=date.today
    )

    tipo_atendimento = db.Column(
        db.String(100),
        nullable=False
    )

    # =====================================================
    # AVALIAÇÃO CLÍNICA
    # =====================================================

    motivo_consulta = db.Column(
        db.Text,
        nullable=True
    )

    anamnese = db.Column(
        db.Text,
        nullable=True
    )

    exame_clinico = db.Column(
        db.Text,
        nullable=True
    )

    # =====================================================
    # DIAGNÓSTICO E TRATAMENTO
    # =====================================================

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

    # =====================================================
    # SINAIS VITAIS
    # =====================================================

    peso_atendimento = db.Column(
        db.Numeric(6, 2),
        nullable=True
    )

    temperatura = db.Column(
        db.Numeric(4, 1),
        nullable=True
    )

    frequencia_cardiaca = db.Column(
        db.Integer,
        nullable=True
    )

    frequencia_respiratoria = db.Column(
        db.Integer,
        nullable=True
    )

    # =====================================================
    # RETORNO
    # =====================================================

    retorno_previsto = db.Column(
        db.Date,
        nullable=True
    )

    # =====================================================
    # CONTROLE
    # =====================================================

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
    # CHAVES ESTRANGEIRAS
    # =====================================================

    pet_id = db.Column(
        db.Integer,
        db.ForeignKey("pets.id"),
        nullable=False
    )

    veterinario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=True
    )

    agendamento_id = db.Column(
        db.Integer,
        db.ForeignKey("agendamentos.id"),
        nullable=True,
        unique=True
    )

    # =====================================================
    # RELACIONAMENTOS
    # =====================================================

    pet = db.relationship(
        "Pet",
        back_populates="historicos"
    )

    veterinario = db.relationship(
        "Usuario",
        foreign_keys=[veterinario_id],
        back_populates="historicos_como_veterinario"
    )

    
    agendamento = db.relationship(
        "AgendamentoConsulta",
        back_populates="historico"
    )

    exames = db.relationship(
    "Exame",
    back_populates="historico",
    cascade="all, delete-orphan",
    lazy=True
    )
    
    def __repr__(self):
        return (
            f"<Historico {self.id} - "
            f"{self.tipo_atendimento}>"
        )
        
    