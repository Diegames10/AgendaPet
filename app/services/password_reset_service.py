import hashlib

from flask import current_app
from itsdangerous import (
    URLSafeTimedSerializer,
    BadSignature,
    SignatureExpired
)

from app.models.usuario import Usuario


class PasswordResetService:

    SALT = "agendapet-redefinicao-senha"
    EXPIRACAO_SEGUNDOS = 30 * 60

    @staticmethod
    def _serializer():

        return URLSafeTimedSerializer(
            current_app.config["SECRET_KEY"]
        )

    @staticmethod
    def _assinatura_senha(usuario):

        return hashlib.sha256(
            usuario.senha_hash.encode("utf-8")
        ).hexdigest()[:20]

    @classmethod
    def gerar_token(cls, usuario):

        dados = {
            "usuario_id": usuario.id,
            "email": usuario.email,
            "senha": cls._assinatura_senha(usuario)
        }

        return cls._serializer().dumps(
            dados,
            salt=cls.SALT
        )

    @classmethod
    def validar_token(cls, token):

        try:

            dados = cls._serializer().loads(
                token,
                salt=cls.SALT,
                max_age=cls.EXPIRACAO_SEGUNDOS
            )

        except SignatureExpired:
            return None

        except BadSignature:
            return None

        usuario = Usuario.query.get(
            dados.get("usuario_id")
        )

        if not usuario:
            return None

        if usuario.email != dados.get("email"):
            return None

        # Torna o link automaticamente inválido
        # após uma alteração de senha.
        if (
            cls._assinatura_senha(usuario)
            != dados.get("senha")
        ):
            return None

        return usuario