from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    abort
)

from flask_login import login_required, current_user

from app import db
from app.models.agendamentoConsulta import AgendamentoConsulta


atendimentos_bp = Blueprint(
    "atendimentos",
    __name__,
    url_prefix="/atendimentos"
)


@atendimentos_bp.route("/")
@login_required
def listar():

    if not current_user.pode_registrar_atendimento:
        abort(403)

    agendamentos = (
        AgendamentoConsulta.query
        .filter(
            AgendamentoConsulta.status.in_(
                [
                    "Confirmado",
                    "Em atendimento"
                ]
            )
        )
        .order_by(
            AgendamentoConsulta.data.asc(),
            AgendamentoConsulta.horario.asc()
        )
        .all()
    )

    return render_template(
        "atendimentos/listar.html",
        agendamentos=agendamentos
    )


@atendimentos_bp.route(
    "/<int:agendamento_id>/iniciar",
    methods=["POST"]
)
@login_required
def iniciar(agendamento_id):

    if not current_user.pode_registrar_atendimento:
        abort(403)

    agendamento = AgendamentoConsulta.query.get_or_404(
        agendamento_id
    )

    if agendamento.status != "Confirmado":
        flash(
            "Somente agendamentos confirmados podem ser iniciados.",
            "warning"
        )

        return redirect(
            url_for("atendimentos.listar")
        )

    agendamento.status = "Em atendimento"

    db.session.commit()

    flash(
        "Atendimento iniciado com sucesso!",
        "success"
    )

    return redirect(
        url_for("atendimentos.listar")
    )
    
