from io import BytesIO

from flask import (
    Blueprint,
    abort,
    render_template,
    send_file
)

from flask_login import login_required

from app.models.usuario import Usuario, TipoUsuario


veterinarios_bp = Blueprint(
    "veterinarios",
    __name__,
    url_prefix="/veterinarios"
)


# =========================================================
# LISTAGEM PÚBLICA PARA USUÁRIOS AUTENTICADOS
# =========================================================

@veterinarios_bp.route("/")
@login_required
def listar():

    veterinarios = (
        Usuario.query
        .filter(
            Usuario.tipo_usuario == TipoUsuario.VETERINARIO,
            Usuario.ativo.is_(True)
        )
        .order_by(
            Usuario.nome.asc()
        )
        .all()
    )

    return render_template(
        "veterinarios/listar_veterinarios.html",
        veterinarios=veterinarios
    )


# =========================================================
# FOTO DO VETERINÁRIO
# =========================================================

@veterinarios_bp.route(
    "/<int:usuario_id>/foto"
)
@login_required
def foto(usuario_id):

    veterinario = (
        Usuario.query
        .filter(
            Usuario.id == usuario_id,
            Usuario.tipo_usuario == TipoUsuario.VETERINARIO,
            Usuario.ativo.is_(True)
        )
        .first_or_404()
    )

    foto_usuario = veterinario.foto_perfil

    if foto_usuario is None:
        abort(404)

    arquivo = foto_usuario.arquivo

    if arquivo is None:
        abort(404)

    dados_imagem = arquivo.miniatura or arquivo.dados

    if not dados_imagem:
        abort(404)

    resposta = send_file(
        BytesIO(dados_imagem),
        mimetype=arquivo.tipo_mime or "image/webp",
        download_name=(
            f"veterinario_{veterinario.id}."
            f"{arquivo.extensao or 'webp'}"
        ),
        as_attachment=False,
        max_age=3600
    )

    resposta.headers["Cache-Control"] = (
        "private, max-age=3600, must-revalidate"
    )

    return resposta