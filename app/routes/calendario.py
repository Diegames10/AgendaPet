from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user

from app.models.agendamentoConsulta import AgendamentoConsulta
from app.models.usuario import TipoUsuario
from flask import Blueprint, render_template, jsonify, abort

calendario_bp = Blueprint(
    "calendario",
    __name__,
    url_prefix="/calendario"
)


@calendario_bp.route("/")
@login_required
def visualizar():

    tipos_permitidos = {
        TipoUsuario.ADMIN,
        TipoUsuario.RECEPCIONISTA,
        TipoUsuario.VETERINARIO
    }

    if current_user.tipo_usuario not in tipos_permitidos:
        abort(403)

    pode_gerenciar = current_user.tipo_usuario in {
        TipoUsuario.ADMIN,
        TipoUsuario.RECEPCIONISTA
    }

    return render_template(
        "calendario/calendario.html",
        pode_gerenciar=pode_gerenciar
    )


@calendario_bp.route("/eventos")
@login_required
def eventos():


    tipos_permitidos = {
    TipoUsuario.ADMIN,
    TipoUsuario.RECEPCIONISTA,
    TipoUsuario.VETERINARIO
    }

    if current_user.tipo_usuario not in tipos_permitidos:
        abort(403)

    consulta = AgendamentoConsulta.query

    # Veterinário visualiza somente os próprios agendamentos.
    if current_user.tipo_usuario == TipoUsuario.VETERINARIO:
        consulta = consulta.filter(
            AgendamentoConsulta.veterinario_id == current_user.id
        )

    
    agendamentos = consulta.all()

    eventos_calendario = []

    for agendamento in agendamentos:

        inicio = (
            f"{agendamento.data.isoformat()}"
            f"T{agendamento.horario.strftime('%H:%M:%S')}"
        )

        nome_pet = (
            agendamento.pet.nome
            if agendamento.pet
            else "Pet não informado"
        )

        eventos_calendario.append({
            "id": agendamento.id,
            "title": f"{nome_pet} - {agendamento.tipo}",
            "start": inicio,
            "extendedProps": {
                "status": agendamento.status,
                "pet": nome_pet,
                "tipo": agendamento.tipo,
                "tutor": (
                    agendamento.tutor.nome
                    if agendamento.tutor
                    else "Não informado"
                ),
                "veterinario": (
                    agendamento.veterinario.nome
                    if agendamento.veterinario
                    else "Não informado"
                ),
                "observacoes": agendamento.observacoes or "",

                "podeGerenciar": current_user.tipo_usuario in {
                    TipoUsuario.ADMIN,
                    TipoUsuario.RECEPCIONISTA
                }
            }
        })

    return jsonify(eventos_calendario)