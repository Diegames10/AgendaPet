from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user

from app.models.agendamentoConsulta import AgendamentoConsulta
from app.models.usuario import TipoUsuario
from flask import Blueprint, render_template, jsonify, abort

from flask import request
from app import db

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

@calendario_bp.route("/confirmar/<int:id>", methods=["POST"])
@login_required
def confirmar_agendamento(id):

    if current_user.tipo_usuario not in {
        TipoUsuario.ADMIN,
        TipoUsuario.RECEPCIONISTA
    }:
        abort(403)

    agendamento = AgendamentoConsulta.query.get_or_404(id)

    if agendamento.status != "Agendado":
        return jsonify({
            "sucesso": False,
            "mensagem": "Este agendamento não pode ser confirmado."
        }), 400

    agendamento.status = "Confirmado"

    db.session.commit()

    return jsonify({
        "sucesso": True,
        "novo_status": "Confirmado"
    })
    
@calendario_bp.route("/iniciar-atendimento/<int:id>", methods=["POST"])
@login_required
def iniciar_atendimento(id):

    if current_user.tipo_usuario not in {
        TipoUsuario.ADMIN,
        TipoUsuario.RECEPCIONISTA,
        TipoUsuario.VETERINARIO
    }:
        abort(403)

    agendamento = AgendamentoConsulta.query.get_or_404(id)

    # Veterinário só pode iniciar os próprios atendimentos.
    if (
        current_user.tipo_usuario == TipoUsuario.VETERINARIO
        and agendamento.veterinario_id != current_user.id
    ):
        abort(403)

    if agendamento.status != "Confirmado":
        return jsonify({
            "sucesso": False,
            "mensagem": "Somente agendamentos confirmados podem ser iniciados."
        }), 400

    agendamento.status = "Em atendimento"

    db.session.commit()

    return jsonify({
        "sucesso": True,
        "novo_status": "Em atendimento"
    })
    
@calendario_bp.route("/finalizar/<int:id>", methods=["POST"])
@login_required
def finalizar_agendamento(id):

    if current_user.tipo_usuario not in {
        TipoUsuario.ADMIN,
        TipoUsuario.RECEPCIONISTA,
        TipoUsuario.VETERINARIO
    }:
        abort(403)

    agendamento = AgendamentoConsulta.query.get_or_404(id)

    # Veterinário só pode finalizar os próprios atendimentos.
    if (
        current_user.tipo_usuario == TipoUsuario.VETERINARIO
        and agendamento.veterinario_id != current_user.id
    ):
        abort(403)

    if agendamento.status != "Em atendimento":
        return jsonify({
            "sucesso": False,
            "mensagem": "Somente atendimentos em andamento podem ser finalizados."
        }), 400

    agendamento.status = "Finalizado"

    db.session.commit()

    return jsonify({
        "sucesso": True,
        "novo_status": "Finalizado"
    })
    
@calendario_bp.route("/cancelar/<int:id>", methods=["POST"])
@login_required
def cancelar_agendamento(id):

    if current_user.tipo_usuario not in {
        TipoUsuario.ADMIN,
        TipoUsuario.RECEPCIONISTA
    }:
        abort(403)

    agendamento = AgendamentoConsulta.query.get_or_404(id)

    if agendamento.status not in {
        "Agendado",
        "Confirmado"
    }:
        return jsonify({
            "sucesso": False,
            "mensagem": (
                "Somente agendamentos agendados ou confirmados "
                "podem ser cancelados."
            )
        }), 400

    agendamento.status = "Cancelado"

    db.session.commit()

    return jsonify({
        "sucesso": True,
        "novo_status": "Cancelado"
    })