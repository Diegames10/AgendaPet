from io import BytesIO

from flask import (
    Blueprint,
    render_template,
    send_file,
    abort
)

from flask_login import login_required

from app.models.usuario import Usuario, TipoUsuario


veterinarios_bp = Blueprint(
    "veterinarios",
    __name__,
    url_prefix="/veterinarios"
)


@veterinarios_bp.route("/")
@login_required
def listar():

    veterinarios = (
        Usuario.query
        .filter(
            Usuario.tipo_usuario == TipoUsuario.VETERINARIO,
            Usuario.ativo == True
        )
        .order_by(Usuario.nome)
        .all()
    )

    return render_template(
        "veterinarios/listar_veterinarios.html",
        veterinarios=veterinarios
    )


@veterinarios_bp.route("/<int:id>/foto")
@login_required
def foto(id):

    veterinario = Usuario.query.get_or_404(id)

    if not veterinario.foto_perfil:
        abort(404)

    arquivo = veterinario.foto_perfil.arquivo

    return send_file(
        BytesIO(arquivo.dados),
        mimetype=arquivo.tipo_mime
    )