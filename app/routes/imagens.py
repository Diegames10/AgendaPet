from io import BytesIO

from flask import Blueprint, abort, send_file
from flask_login import current_user, login_required

from app.models.pet import Pet
from app.models.foto_pet import FotoPet
from app.services.storage_service import StorageService


imagens_bp = Blueprint(
    "imagens",
    __name__,
    url_prefix="/imagens"
)


# =========================================================
# FUNÇÃO INTERNA PARA ENVIAR IMAGEM
# =========================================================

def _enviar_imagem(
    arquivo,
    nome_download,
    usar_miniatura=False
):
    """
    Retorna uma imagem.

    Prioridade:
    1. Arquivo físico no storage.
    2. Dados binários antigos no PostgreSQL.

    Isso permite manter compatibilidade durante
    a migração do armazenamento.
    """

    if arquivo is None:
        abort(404)

    # =====================================================
    # NOVO MODELO: ARQUIVO NO STORAGE
    # =====================================================

    caminho_relativo = (
        arquivo.caminho_miniatura
        if usar_miniatura
        else arquivo.caminho
    )

    # Se foi solicitada miniatura, mas ela não existir,
    # usa a imagem principal.
    if (
        usar_miniatura
        and not caminho_relativo
    ):
        caminho_relativo = arquivo.caminho

    if caminho_relativo:

        try:
            caminho_fisico = (
                StorageService.obter_caminho(
                    caminho_relativo
                )
            )

        except ValueError:
            abort(404)

        if caminho_fisico.is_file():

            resposta = send_file(
                caminho_fisico,
                mimetype=(
                    arquivo.tipo_mime
                    or "image/webp"
                ),
                download_name=nome_download,
                as_attachment=False,
                max_age=3600
            )

            resposta.headers["Cache-Control"] = (
                "private, max-age=3600, must-revalidate"
            )

            return resposta

    # =====================================================
    # MODELO ANTIGO: ARQUIVO NO POSTGRESQL
    # =====================================================

    dados = None

    if usar_miniatura:

        dados = (
            arquivo.miniatura
            or arquivo.dados
        )

    else:

        dados = arquivo.dados

    if not dados:
        abort(404)

    resposta = send_file(
        BytesIO(dados),
        mimetype=(
            arquivo.tipo_mime
            or "image/webp"
        ),
        download_name=nome_download,
        as_attachment=False,
        max_age=3600
    )

    resposta.headers["Cache-Control"] = (
        "private, max-age=3600, must-revalidate"
    )

    return resposta


# =========================================================
# FOTO DE PERFIL
# =========================================================

@imagens_bp.route("/perfil")
@login_required
def foto_perfil():
    """
    Retorna a imagem completa do usuário autenticado.
    """

    foto_usuario = current_user.foto_perfil

    if foto_usuario is None:
        abort(404)

    arquivo = foto_usuario.arquivo

    return _enviar_imagem(
        arquivo=arquivo,
        nome_download=(
            f"foto_perfil_usuario_{current_user.id}."
            f"{arquivo.extensao or 'webp'}"
            if arquivo
            else "foto_perfil.webp"
        ),
        usar_miniatura=False
    )


# =========================================================
# MINIATURA DA FOTO DE PERFIL
# =========================================================

@imagens_bp.route("/perfil/miniatura")
@login_required
def miniatura_foto_perfil():
    """
    Retorna a miniatura da foto de perfil.
    """

    foto_usuario = current_user.foto_perfil

    if foto_usuario is None:
        abort(404)

    arquivo = foto_usuario.arquivo

    return _enviar_imagem(
        arquivo=arquivo,
        nome_download=(
            f"miniatura_perfil_usuario_"
            f"{current_user.id}.webp"
        ),
        usar_miniatura=True
    )


# =========================================================
# FOTO PRINCIPAL DO PET
# =========================================================

@imagens_bp.route("/pets/<int:pet_id>")
@login_required
def foto_principal_pet(pet_id):
    """
    Retorna a foto principal completa do pet.
    """

    pet = _buscar_pet_do_usuario(
        pet_id
    )

    foto = pet.foto_principal

    if foto is None:
        abort(404)

    arquivo = foto.arquivo

    return _enviar_imagem(
        arquivo=arquivo,
        nome_download=(
            f"pet_{pet.id}_foto_principal."
            f"{arquivo.extensao or 'webp'}"
            if arquivo
            else f"pet_{pet.id}.webp"
        ),
        usar_miniatura=False
    )


# =========================================================
# MINIATURA DA FOTO PRINCIPAL DO PET
# =========================================================

@imagens_bp.route(
    "/pets/<int:pet_id>/miniatura"
)
@login_required
def miniatura_foto_principal_pet(pet_id):
    """
    Retorna a miniatura da foto principal do pet.
    """

    pet = _buscar_pet_do_usuario(
        pet_id
    )

    foto = pet.foto_principal

    if foto is None:
        abort(404)

    arquivo = foto.arquivo

    return _enviar_imagem(
        arquivo=arquivo,
        nome_download=(
            f"pet_{pet.id}_miniatura.webp"
        ),
        usar_miniatura=True
    )


# =========================================================
# FOTO ESPECÍFICA DO PET
# =========================================================

@imagens_bp.route(
    "/pets/<int:pet_id>/fotos/<int:foto_id>"
)
@login_required
def foto_pet(pet_id, foto_id):
    """
    Retorna uma foto específica do pet.
    """

    pet = _buscar_pet_do_usuario(
        pet_id
    )

    foto = FotoPet.query.filter_by(
        id=foto_id,
        pet_id=pet.id
    ).first()

    if foto is None:
        abort(404)

    arquivo = foto.arquivo

    return _enviar_imagem(
        arquivo=arquivo,
        nome_download=(
            f"pet_{pet.id}_foto_{foto.id}."
            f"{arquivo.extensao or 'webp'}"
            if arquivo
            else f"pet_{pet.id}_foto.webp"
        ),
        usar_miniatura=False
    )


# =========================================================
# MINIATURA DE FOTO ESPECÍFICA
# =========================================================

@imagens_bp.route(
    "/pets/<int:pet_id>/fotos/<int:foto_id>/miniatura"
)
@login_required
def miniatura_foto_pet(
    pet_id,
    foto_id
):
    """
    Retorna a miniatura de uma foto específica do pet.
    """

    pet = _buscar_pet_do_usuario(
        pet_id
    )

    foto = FotoPet.query.filter_by(
        id=foto_id,
        pet_id=pet.id
    ).first()

    if foto is None:
        abort(404)

    arquivo = foto.arquivo

    return _enviar_imagem(
        arquivo=arquivo,
        nome_download=(
            f"pet_{pet.id}_foto_{foto.id}_miniatura.webp"
        ),
        usar_miniatura=True
    )


# =========================================================
# VALIDAÇÃO DE ACESSO AO PET
# =========================================================

def _buscar_pet_do_usuario(pet_id):
    """
    Controla o acesso às imagens dos pets.

    Funcionários podem visualizar todos os pets.
    Clientes podem visualizar somente os próprios pets.
    """

    if current_user.pode_ver_todos_os_pets:

        pet = Pet.query.filter_by(
            id=pet_id
        ).first()

    else:

        pet = Pet.query.filter_by(
            id=pet_id,
            tutor_id=current_user.id
        ).first()

    if pet is None:
        abort(404)

    return pet