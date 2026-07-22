from datetime import datetime

from app import db


class Arquivo(db.Model):
    """
    Armazena arquivos binários utilizados pelo sistema.

    Inicialmente será usado para:
    - fotos dos usuários;
    - fotos dos pets.

    Futuramente poderá ser reutilizado para:
    - exames;
    - receitas;
    - laudos;
    - documentos;
    - imagens de atendimentos.
    """

    __tablename__ = "arquivos"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nome_original = db.Column(
        db.String(255),
        nullable=False
    )

    tipo_mime = db.Column(
        db.String(100),
        nullable=False,
        default="image/webp"
    )

    extensao = db.Column(
        db.String(20),
        nullable=False,
        default="webp"
    )

    dados = db.Column(
        db.LargeBinary,
        nullable=False
    )

    miniatura = db.Column(
        db.LargeBinary,
        nullable=True
    )

    tamanho_bytes = db.Column(
        db.Integer,
        nullable=False
    )

    tamanho_miniatura_bytes = db.Column(
        db.Integer,
        nullable=True
    )

    largura = db.Column(
        db.Integer,
        nullable=True
    )

    altura = db.Column(
        db.Integer,
        nullable=True
    )

    largura_miniatura = db.Column(
        db.Integer,
        nullable=True
    )

    altura_miniatura = db.Column(
        db.Integer,
        nullable=True
    )

    hash_sha256 = db.Column(
        db.String(64),
        nullable=True,
        index=True
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

    qualidade = db.Column(
        db.SmallInteger,
        nullable=False,
        default=82
    )

    modelo_compactacao = db.Column(
        db.String(30),
        nullable=False,
        default="WEBP_LOSSY"
    )

    versao_processador = db.Column(
        db.String(10),
        nullable=False,
        default="1.0"
    )

    orientacao_corrigida = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )
    
    def __repr__(self):
        return (
            f"<Arquivo {self.id} "
            f"- {self.nome_original} "
            f"- {self.tamanho_bytes} bytes>"
        )