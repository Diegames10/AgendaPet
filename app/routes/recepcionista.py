from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user

from app.models.usuario import TipoUsuario


recepcionista_bp = Blueprint(
    "recepcionista",
    __name__,
    url_prefix="/recepcionista"
)


@recepcionista_bp.route("/")
@login_required
def painel():
    """
    Exibe o painel operacional da recepção.

    O acesso é permitido apenas para administradores
    e recepcionistas.
    """

    perfis_permitidos = (
        TipoUsuario.ADMIN,
        TipoUsuario.RECEPCIONISTA
    )

    if current_user.tipo_usuario not in perfis_permitidos:
        abort(403)

    return render_template(
        "recepcionista/painel.html"
    )