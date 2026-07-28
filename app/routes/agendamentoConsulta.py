from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    jsonify,
    flash
)

from flask_login import login_required, current_user

from app import db
from app.models.agendamentoConsulta import AgendamentoConsulta
from app.models.pet import Pet
from app.models.usuario import Usuario, TipoUsuario
from app.models.horario_veterinario import HorarioVeterinario
from app.utils.agenda import gerar_horarios_disponiveis

agendamento_consulta_bp = Blueprint(
    "agendamento_consulta",
    __name__,
    url_prefix="/agendamentos"
)

def buscar_agendamento_permitido(agendamento_id):
    """
    Administradores e recepcionistas podem acessar qualquer agendamento.

    Clientes podem acessar somente os próprios agendamentos.
    """

    consulta = AgendamentoConsulta.query.filter_by(
        id=agendamento_id
    )

    if not current_user.pode_ver_todos_os_agendamentos:
        consulta = consulta.filter_by(
            tutor_id=current_user.id
        )

    return consulta.first_or_404()

@agendamento_consulta_bp.route("/")
@login_required
def listar():

    consulta = AgendamentoConsulta.query

    # Cliente visualiza somente os próprios agendamentos.
    if not current_user.pode_ver_todos_os_agendamentos:
        consulta = consulta.filter(
            AgendamentoConsulta.tutor_id == current_user.id
        )

    agendamentos = (
        consulta
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



@agendamento_consulta_bp.route("/horarios")
@login_required
def horarios_disponiveis():

    veterinario_id = request.args.get(
        "veterinario_id",
        type=int
    )

    data_texto = request.args.get("data")

    if not veterinario_id or not data_texto:

        return jsonify([])

    try:

        data = datetime.strptime(
            data_texto,
            "%Y-%m-%d"
        ).date()

    except ValueError:

        return jsonify([])

    dia_semana = data.weekday()

    print("Veterinário:", veterinario_id)
    print("Data:", data)
    print("Dia da semana:", dia_semana)

    expediente = (
        HorarioVeterinario.query
        .filter_by(
            veterinario_id=veterinario_id,
            dia_semana=dia_semana,
            ativo=True
        )
        .first()
    )

    print("Expediente:", expediente)

    if expediente is None:

        return jsonify([])

    ocupados = [

        agendamento.horario

        for agendamento in (
            AgendamentoConsulta.query
            .filter_by(
                veterinario_id=veterinario_id,
                data=data
            )
            .all()
        )

    ]

    horarios = gerar_horarios_disponiveis(

        expediente.hora_inicio,
        expediente.hora_fim,
        expediente.inicio_almoco,
        expediente.fim_almoco,
        expediente.intervalo_minutos,
        ocupados

    )

    return jsonify(

        [

            horario.strftime("%H:%M")

            for horario in horarios

        ]

    )
    
@agendamento_consulta_bp.route(
    "/cadastrar",
    methods=["GET", "POST"]
)
@login_required
def cadastrar():

    pode_agendar_para_outros = (
        current_user.pode_ver_todos_os_agendamentos
    )

    clientes = []

    # Recepcionista e administrador podem escolher o cliente.
    if pode_agendar_para_outros:

        clientes = (
            Usuario.query
            .filter(
                Usuario.tipo_usuario == TipoUsuario.CLIENTE,
                Usuario.ativo.is_(True)
            )
            .order_by(Usuario.nome.asc())
            .all()
        )

        pets = (
            Pet.query
            .order_by(Pet.nome.asc())
            .all()
        )

    else:

        # Cliente acessa somente os próprios pets.
        pets = (
            Pet.query
            .filter_by(tutor_id=current_user.id)
            .order_by(Pet.nome.asc())
            .all()
        )

        if not pets:
            flash(
                "Cadastre pelo menos um pet antes de realizar "
                "um agendamento.",
                "warning"
            )

            return redirect(
                url_for("pets.cadastrar")
            )

    veterinarios = (
        Usuario.query
        .filter(
            Usuario.tipo_usuario == TipoUsuario.VETERINARIO,
            Usuario.ativo.is_(True)
        )
        .order_by(Usuario.nome.asc())
        .all()
    )

    if request.method == "POST":

        # Define o tutor responsável pelo agendamento.
        if pode_agendar_para_outros:

            tutor_id = request.form.get(
                "tutor_id",
                type=int
            )

            tutor = Usuario.query.filter(
                Usuario.id == tutor_id,
                Usuario.tipo_usuario == TipoUsuario.CLIENTE,
                Usuario.ativo.is_(True)
            ).first()

            if tutor is None:
                flash(
                    "Selecione um cliente válido.",
                    "danger"
                )

                return redirect(
                    url_for(
                        "agendamento_consulta.cadastrar"
                    )
                )

        else:

            tutor = current_user
            tutor_id = current_user.id

        pet_id = request.form.get(
            "pet_id",
            type=int
        )

        veterinario_id = request.form.get(
            "veterinario_id",
            type=int
        )

        tipo = request.form.get(
            "tipo",
            ""
        ).strip()

        data_texto = request.form.get(
            "data",
            ""
        ).strip()

        horario_texto = request.form.get(
            "horario",
            ""
        ).strip()

        observacoes = request.form.get(
            "observacoes",
            ""
        ).strip()

        # O pet precisa pertencer ao cliente selecionado.
        pet = Pet.query.filter_by(
            id=pet_id,
            tutor_id=tutor_id
        ).first()

        if pet is None:
            flash(
                "Selecione um pet válido para o cliente informado.",
                "danger"
            )

            return redirect(
                url_for(
                    "agendamento_consulta.cadastrar"
                )
            )

        veterinario = None

        if veterinario_id:

            veterinario = Usuario.query.filter(
                Usuario.id == veterinario_id,
                Usuario.tipo_usuario == TipoUsuario.VETERINARIO,
                Usuario.ativo.is_(True)
            ).first()

            if veterinario is None:
                flash(
                    "Selecione um veterinário válido.",
                    "danger"
                )

                return redirect(
                    url_for(
                        "agendamento_consulta.cadastrar"
                    )
                )

        if not tipo or not data_texto or not horario_texto:

            flash(
                "Preencha o pet, o tipo, a data e o horário.",
                "danger"
            )

            return redirect(
                url_for(
                    "agendamento_consulta.cadastrar"
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
                    "agendamento_consulta.cadastrar"
                )
            )

        novo_agendamento = AgendamentoConsulta(
            tipo=tipo,
            data=data_agendamento,
            horario=horario_agendamento,
            status="Agendado",
            observacoes=observacoes or None,
            pet_id=pet.id,
            tutor_id=tutor_id,
            veterinario_id=veterinario_id
        )

        db.session.add(novo_agendamento)
        db.session.commit()

        flash(
            "Agendamento realizado com sucesso!",
            "success"
        )

        # Recepção volta para o painel operacional.
        if pode_agendar_para_outros:
            return redirect(
                url_for("recepcionista.painel")
            )

        return redirect(
            url_for("agendamento_consulta.listar")
        )

    return render_template(
        "agendamentos/cadastrar.html",
        pets=pets,
        clientes=clientes,
        veterinarios=veterinarios,
        pode_agendar_para_outros=pode_agendar_para_outros
    )

@agendamento_consulta_bp.route(
    "/<int:agendamento_id>/editar",
    methods=["GET", "POST"]
)
@login_required
def editar(agendamento_id):
    agendamento = buscar_agendamento_permitido(
    agendamento_id
    )

    pets = (
        Pet.query
        .filter_by(tutor_id=agendamento.tutor_id)
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
            tutor_id=agendamento.tutor_id
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
            "Em atendimento",
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
    agendamento = buscar_agendamento_permitido(
    agendamento_id
    )

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
    agendamento = buscar_agendamento_permitido(
        agendamento_id
    )

    db.session.delete(agendamento)
    db.session.commit()

    flash(
        "Agendamento excluído com sucesso.",
        "success"
    )

    return redirect(
        url_for("agendamento_consulta.listar")
    )