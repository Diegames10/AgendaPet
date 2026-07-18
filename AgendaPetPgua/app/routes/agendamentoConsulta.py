from datetime import datetime
from app.models.veterinario import Veterinario

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import login_required, current_user

from app import db
from app.models.agendamentoConsulta import AgendamentoConsulta
from app.models.pet import Pet


agendamento_consulta_bp = Blueprint(
    "agendamento_consulta",
    __name__,
    url_prefix="/agendamentos"
)


@agendamento_consulta_bp.route("/")
@login_required
def listar():
    agendamentos = (
        AgendamentoConsulta.query
        .filter_by(tutor_id=current_user.id)
        .order_by(
            AgendamentoConsulta.data.asc(),
            AgendamentoConsulta.horario.asc()
        )
        .all()
    )

    return render_template(
        "agendamentos/listar.html",
        agendamentos=agendamentos
    )


@agendamento_consulta_bp.route(
    "/cadastrar",
    methods=["GET", "POST"]
)
@login_required
def cadastrar():
    pets = (
        Pet.query
        .filter_by(tutor_id=current_user.id)
        .order_by(Pet.nome.asc())
        .all()
    )
    
    veterinarios = (
    Veterinario.query
    .filter_by(ativo=True)
    .order_by(Veterinario.nome.asc())
    .all()
    )

    if not pets:
        flash(
            "Cadastre pelo menos um pet antes de realizar um agendamento.",
            "warning"
        )

        return redirect(url_for("pets.cadastrar"))

    if request.method == "POST":
        pet_id = request.form.get("pet_id", type=int)
        tipo = request.form.get("tipo", "").strip()
        data_texto = request.form.get("data", "").strip()
        horario_texto = request.form.get("horario", "").strip()
        observacoes = request.form.get("observacoes", "").strip()

        veterinario_id = request.form.get(
        "veterinario_id",
        type=int
        )
        
        pet = Pet.query.filter_by(
            id=pet_id,
            tutor_id=current_user.id
        ).first()

        if not pet:
            flash("Selecione um pet válido.", "danger")
            return redirect(
                url_for("agendamento_consulta.cadastrar")
            )

        if not tipo or not data_texto or not horario_texto:
            flash(
                "Preencha o pet, o tipo, a data e o horário.",
                "danger"
            )

            return redirect(
                url_for("agendamento_consulta.cadastrar")
            )

        try:
            data_agendamento = datetime.strptime(
                data_texto,
                "%Y-%m-%d"
            ).date()

            horario_agendamento = datetime.strptime(
                horario_texto,
                "%H:%M"
            ).time()

        except ValueError:
            flash(
                "A data ou o horário informado é inválido.",
                "danger"
            )

            return redirect(
                url_for("agendamento_consulta.cadastrar")
            )

        novo_agendamento = AgendamentoConsulta(
            tipo=tipo,
            data=data_agendamento,
            horario=horario_agendamento,
            status="Agendado",
            observacoes=observacoes or None,
            pet_id=pet.id,
            tutor_id=current_user.id,
            veterinario_id=veterinario_id
        )

        db.session.add(novo_agendamento)
        db.session.commit()

        flash(
            "Agendamento realizado com sucesso!",
            "success"
        )

        return redirect(
            url_for("agendamento_consulta.listar")
        )

    return render_template(
    "agendamentos/cadastrar.html",
    pets=pets,
    veterinarios=veterinarios
)


@agendamento_consulta_bp.route(
    "/<int:agendamento_id>/editar",
    methods=["GET", "POST"]
)
@login_required
def editar(agendamento_id):
    agendamento = AgendamentoConsulta.query.filter_by(
        id=agendamento_id,
        tutor_id=current_user.id
    ).first_or_404()

    pets = (
        Pet.query
        .filter_by(tutor_id=current_user.id)
        .order_by(Pet.nome.asc())
        .all()
    )

    if request.method == "POST":
        pet_id = request.form.get("pet_id", type=int)
        tipo = request.form.get("tipo", "").strip()
        data_texto = request.form.get("data", "").strip()
        horario_texto = request.form.get("horario", "").strip()
        status = request.form.get("status", "").strip()
        observacoes = request.form.get("observacoes", "").strip()

        pet = Pet.query.filter_by(
            id=pet_id,
            tutor_id=current_user.id
        ).first()

        if not pet:
            flash("Selecione um pet válido.", "danger")
            return redirect(
                url_for(
                    "agendamento_consulta.editar",
                    agendamento_id=agendamento.id
                )
            )

        if not tipo or not data_texto or not horario_texto:
            flash(
                "Preencha os campos obrigatórios.",
                "danger"
            )

            return redirect(
                url_for(
                    "agendamento_consulta.editar",
                    agendamento_id=agendamento.id
                )
            )

        try:
            data_agendamento = datetime.strptime(
                data_texto,
                "%Y-%m-%d"
            ).date()

            horario_agendamento = datetime.strptime(
                horario_texto,
                "%H:%M"
            ).time()

        except ValueError:
            flash(
                "A data ou o horário informado é inválido.",
                "danger"
            )

            return redirect(
                url_for(
                    "agendamento_consulta.editar",
                    agendamento_id=agendamento.id
                )
            )

        status_validos = {
            "Agendado",
            "Confirmado",
            "Concluído",
            "Cancelado"
        }

        if status not in status_validos:
            status = "Agendado"

        agendamento.pet_id = pet.id
        agendamento.tipo = tipo
        agendamento.data = data_agendamento
        agendamento.horario = horario_agendamento
        agendamento.status = status
        agendamento.observacoes = observacoes or None

        db.session.commit()

        flash(
            "Agendamento atualizado com sucesso!",
            "success"
        )

        return redirect(
            url_for("agendamento_consulta.listar")
        )

    return render_template(
        "agendamentos/editar.html",
        agendamento=agendamento,
        pets=pets
    )


@agendamento_consulta_bp.route(
    "/<int:agendamento_id>/cancelar",
    methods=["POST"]
)
@login_required
def cancelar(agendamento_id):
    agendamento = AgendamentoConsulta.query.filter_by(
        id=agendamento_id,
        tutor_id=current_user.id
    ).first_or_404()

    agendamento.status = "Cancelado"

    db.session.commit()

    flash(
        "Agendamento cancelado com sucesso.",
        "success"
    )

    return redirect(
        url_for("agendamento_consulta.listar")
    )


@agendamento_consulta_bp.route(
    "/<int:agendamento_id>/excluir",
    methods=["POST"]
)
@login_required
def excluir(agendamento_id):
    agendamento = AgendamentoConsulta.query.filter_by(
        id=agendamento_id,
        tutor_id=current_user.id
    ).first_or_404()

    db.session.delete(agendamento)
    db.session.commit()

    flash(
        "Agendamento excluído com sucesso.",
        "success"
    )

    return redirect(
        url_for("agendamento_consulta.listar")
    )