from io import BytesIO

from flask import Blueprint, abort, send_file
from flask_login import current_user, login_required

from app.models.pet import Pet
from app.models.foto_pet import FotoPet


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
    dados,
    nome_download
):
    """
    Retorna uma imagem armazenada no banco.
    """

    if (
        arquivo is None
        or dados is None
        or not dados
    ):
        abort(404)

    resposta = send_file(
        BytesIO(dados),
        mimetype=arquivo.tipo_mime or "image/webp",
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
        dados=arquivo.dados if arquivo else None,
        nome_download=(
            f"foto_perfil_usuario_{current_user.id}."
            f"{arquivo.extensao or 'webp'}"
            if arquivo
            else "foto_perfil.webp"
        )
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

    dados = (
        arquivo.miniatura or arquivo.dados
        if arquivo
        else None
    )

    return _enviar_imagem(
        arquivo=arquivo,
        dados=dados,
        nome_download=(
            f"miniatura_perfil_usuario_"
            f"{current_user.id}.webp"
        )
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
        dados=arquivo.dados if arquivo else None,
        nome_download=(
            f"pet_{pet.id}_foto_principal."
            f"{arquivo.extensao or 'webp'}"
            if arquivo
            else f"pet_{pet.id}.webp"
        )
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

    dados = (
        arquivo.miniatura or arquivo.dados
        if arquivo
        else None
    )

    return _enviar_imagem(
        arquivo=arquivo,
        dados=dados,
        nome_download=(
            f"pet_{pet.id}_miniatura.webp"
        )
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
        dados=arquivo.dados if arquivo else None,
        nome_download=(
            f"pet_{pet.id}_foto_{foto.id}."
            f"{arquivo.extensao or 'webp'}"
            if arquivo
            else f"pet_{pet.id}_foto.webp"
        )
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

    dados = (
        arquivo.miniatura or arquivo.dados
        if arquivo
        else None
    )

    return _enviar_imagem(
        arquivo=arquivo,
        dados=dados,
        nome_download=(
            f"pet_{pet.id}_foto_{foto.id}_miniatura.webp"
        )
    )


# =========================================================
# VALIDAÇÃO DE ACESSO AO PET
# =========================================================

def _buscar_pet_do_usuario(pet_id):
    """
    Garante que o usuário autenticado só visualize
    imagens dos próprios pets.

    Administradores poderão receber uma regra adicional
    futuramente.
    """

    pet = Pet.query.filter_by(
        id=pet_id,
        tutor_id=current_user.id
    ).first()

    if pet is None:
        abort(404)

    return pet