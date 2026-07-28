from datetime import date

from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user

from app.models.usuario import TipoUsuario
from app.models.agendamentoConsulta import AgendamentoConsulta


recepcionista_bp = Blueprint(
    "recepcionista",
    __name__,
    url_prefix="/recepcionista"
)


@recepcionista_bp.route("/")
@login_required
def painel():

    perfis_permitidos = (
        TipoUsuario.ADMIN,
        TipoUsuario.RECEPCIONISTA
    )

    if current_user.tipo_usuario not in perfis_permitidos:
        abort(403)

    hoje = date.today()

    agendamentos_hoje = (
        AgendamentoConsulta.query
        .filter(
            AgendamentoConsulta.data == hoje,
            AgendamentoConsulta.status != "Cancelado"
        )
        .order_by(
            AgendamentoConsulta.horario.asc()
        )
        .all()
    )

    aguardando_chegada = [
        agendamento
        for agendamento in agendamentos_hoje
        if agendamento.status in ("Agendado", "Confirmado")
    ]

    em_atendimento = [
        agendamento
        for agendamento in agendamentos_hoje
        if agendamento.status == "Em atendimento"
    ]

    return render_template(
        "recepcionista/painel.html",
        agendamentos_hoje=agendamentos_hoje,
        total_agendamentos_hoje=len(agendamentos_hoje),
        total_aguardando_chegada=len(aguardando_chegada),
        total_em_atendimento=len(em_atendimento)
    )