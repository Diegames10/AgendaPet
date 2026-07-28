from datetime import datetime

from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for
)

from flask_login import current_user, login_required

from app import db
from app.models.horario_veterinario import HorarioVeterinario
from app.models.usuario import TipoUsuario, Usuario


agenda_inteligente_bp = Blueprint(
    "agenda_inteligente",
    __name__,
    url_prefix="/agenda-inteligente"
)


DIAS_SEMANA = {
    0: "Segunda-feira",
    1: "Terça-feira",
    2: "Quarta-feira",
    3: "Quinta-feira",
    4: "Sexta-feira",
    5: "Sábado",
    6: "Domingo"
}


def verificar_permissao():
    """
    Permite o acesso somente para administradores
    e recepcionistas.
    """

    if not (
        current_user.is_admin
        or current_user.is_recepcionista
    ):
        abort(403)


def converter_horario(valor):
    """
    Converte um horário recebido pelo formulário HTML
    para um objeto datetime.time.
    """

    if not valor:
        return None

    try:
        return datetime.strptime(
            valor,
            "%H:%M"
        ).time()

    except ValueError:
        return None


def buscar_veterinarios():
    """
    Retorna apenas usuários ativos com perfil
    de veterinário.
    """

    return (
        Usuario.query
        .filter_by(
            tipo_usuario=TipoUsuario.VETERINARIO,
            ativo=True
        )
        .order_by(
            Usuario.nome.asc()
        )
        .all()
    )


@agenda_inteligente_bp.route("/")
@login_required
def listar():

    verificar_permissao()

    horarios = (
        HorarioVeterinario.query
        .join(
            Usuario,
            HorarioVeterinario.veterinario_id == Usuario.id
        )
        .order_by(
            Usuario.nome.asc(),
            HorarioVeterinario.dia_semana.asc(),
            HorarioVeterinario.hora_inicio.asc()
        )
        .all()
    )

    return render_template(
        "agenda_inteligente/listar.html",
        horarios=horarios,
        dias_semana=DIAS_SEMANA
    )


@agenda_inteligente_bp.route(
    "/cadastrar",
    methods=["GET", "POST"]
)
@login_required
def cadastrar():

    verificar_permissao()

    veterinarios = buscar_veterinarios()

    if request.method == "POST":

        veterinario_id = request.form.get(
            "veterinario_id",
            type=int
        )

        dias_semana_recebidos = request.form.getlist("dias_semana")

        try:
            dias_semana = [int(dia) for dia in dias_semana_recebidos]
        except ValueError:
            dias_semana = []

        hora_inicio = converter_horario(
            request.form.get("hora_inicio")
        )

        hora_fim = converter_horario(
            request.form.get("hora_fim")
        )

        inicio_almoco = converter_horario(
            request.form.get("inicio_almoco")
        )

        fim_almoco = converter_horario(
            request.form.get("fim_almoco")
        )

        intervalo_minutos = request.form.get(
            "intervalo_minutos",
            type=int
        )

        ativo = request.form.get("ativo") == "on"

        # -----------------------------
        # VALIDAÇÕES
        # -----------------------------

        veterinario = db.session.get(
            Usuario,
            veterinario_id
        )

        if not veterinario:

            flash(
                "Veterinário não encontrado.",
                "erro"
            )

            return redirect(
                url_for(
                    "agenda_inteligente.cadastrar"
                )
            )

        if veterinario.tipo_usuario != TipoUsuario.VETERINARIO:

            flash(
                "O usuário selecionado não é veterinário.",
                "erro"
            )

            return redirect(
                url_for(
                    "agenda_inteligente.cadastrar"
                )
            )

        if not dias_semana:

            flash(
                "Selecione pelo menos um dia da semana.",
                "erro"
            )

            return redirect(
                url_for("agenda_inteligente.cadastrar")
            )


        if any(dia not in DIAS_SEMANA for dia in dias_semana):

            flash(
                "Foi selecionado um dia da semana inválido.",
                "erro"
            )

            return redirect(
                url_for("agenda_inteligente.cadastrar")
            )

        if not hora_inicio or not hora_fim:

            flash(
                "Informe os horários de início e término.",
                "erro"
            )

            return redirect(
                url_for(
                    "agenda_inteligente.cadastrar"
                )
            )

        if hora_inicio >= hora_fim:

            flash(
                "O horário inicial deve ser anterior ao horário final.",
                "erro"
            )

            return redirect(
                url_for(
                    "agenda_inteligente.cadastrar"
                )
            )

        if intervalo_minutos not in (
            10,
            15,
            20,
            30,
            40,
            45,
            60
        ):

            flash(
                "Selecione um intervalo válido.",
                "erro"
            )

            return redirect(
                url_for(
                    "agenda_inteligente.cadastrar"
                )
            )

        # Os dois horários de almoço devem ser
        # informados juntos.

        if bool(inicio_almoco) != bool(fim_almoco):

            flash(
                "Informe o início e o término do intervalo de almoço.",
                "erro"
            )

            return redirect(
                url_for(
                    "agenda_inteligente.cadastrar"
                )
            )

        if inicio_almoco and fim_almoco:

            if inicio_almoco >= fim_almoco:

                flash(
                    "O início do almoço deve ser anterior ao término.",
                    "erro"
                )

                return redirect(
                    url_for(
                        "agenda_inteligente.cadastrar"
                    )
                )

            if (
                inicio_almoco < hora_inicio
                or fim_almoco > hora_fim
            ):

                flash(
                    "O intervalo de almoço deve estar dentro do expediente.",
                    "erro"
                )

                return redirect(
                    url_for(
                        "agenda_inteligente.cadastrar"
                    )
                )

        # Como a estrutura atual representa um expediente
        # completo por dia, não permitimos dois registros
        # para o mesmo veterinário e mesmo dia.

        dias_ja_cadastrados = {
            horario.dia_semana
            for horario in (
                HorarioVeterinario.query
                .filter(
                    HorarioVeterinario.veterinario_id == veterinario_id,
                    HorarioVeterinario.dia_semana.in_(dias_semana)
                )
                .all()
            )
        }

        if dias_ja_cadastrados:

            nomes_dias = ", ".join(
                DIAS_SEMANA[dia]
                for dia in sorted(dias_ja_cadastrados)
            )

            flash(
                f"O veterinário já possui expediente cadastrado em: "
                f"{nomes_dias}.",
                "erro"
            )

            return redirect(
                url_for("agenda_inteligente.cadastrar")
            )


        try:

            for dia_semana in dias_semana:

                novo_horario = HorarioVeterinario(
                    veterinario_id=veterinario_id,
                    dia_semana=dia_semana,
                    hora_inicio=hora_inicio,
                    hora_fim=hora_fim,
                    inicio_almoco=inicio_almoco,
                    fim_almoco=fim_almoco,
                    intervalo_minutos=intervalo_minutos,
                    ativo=ativo
                )

                db.session.add(novo_horario)

            db.session.commit()

            quantidade = len(dias_semana)

            flash(
                f"{quantidade} expediente(s) cadastrado(s) com sucesso.",
                "sucesso"
            )

            return redirect(
                url_for("agenda_inteligente.listar")
            )

        except Exception:

            db.session.rollback()

            flash(
                "Não foi possível cadastrar os expedientes.",
                "erro"
            )

            db.session.commit()

            flash(
                "Horário de trabalho cadastrado com sucesso.",
                "sucesso"
            )

            return redirect(
                url_for(
                    "agenda_inteligente.listar"
                )
            )

        except Exception:

            db.session.rollback()

            flash(
                "Não foi possível cadastrar o horário.",
                "erro"
            )

    return render_template(
        "agenda_inteligente/cadastrar.html",
        veterinarios=veterinarios,
        dias_semana=DIAS_SEMANA
    )


@agenda_inteligente_bp.route(
    "/<int:id>/editar",
    methods=["GET", "POST"]
)
@login_required
def editar(id):

    verificar_permissao()

    horario = db.get_or_404(
        HorarioVeterinario,
        id
    )

    veterinarios = buscar_veterinarios()

    if request.method == "POST":

        veterinario_id = request.form.get(
            "veterinario_id",
            type=int
        )

        dia_semana = request.form.get(
            "dia_semana",
            type=int
        )

        hora_inicio = converter_horario(
            request.form.get("hora_inicio")
        )

        hora_fim = converter_horario(
            request.form.get("hora_fim")
        )

        inicio_almoco = converter_horario(
            request.form.get("inicio_almoco")
        )

        fim_almoco = converter_horario(
            request.form.get("fim_almoco")
        )

        intervalo_minutos = request.form.get(
            "intervalo_minutos",
            type=int
        )

        ativo = request.form.get("ativo") == "on"

        veterinario = db.session.get(
            Usuario,
            veterinario_id
        )

        if not veterinario:

            flash(
                "Veterinário não encontrado.",
                "erro"
            )

            return redirect(
                url_for(
                    "agenda_inteligente.editar",
                    id=id
                )
            )

        if veterinario.tipo_usuario != TipoUsuario.VETERINARIO:

            flash(
                "O usuário selecionado não é veterinário.",
                "erro"
            )

            return redirect(
                url_for(
                    "agenda_inteligente.editar",
                    id=id
                )
            )

        if dia_semana not in DIAS_SEMANA:

            flash(
                "Selecione um dia da semana válido.",
                "erro"
            )

            return redirect(
                url_for(
                    "agenda_inteligente.editar",
                    id=id
                )
            )

        if not hora_inicio or not hora_fim:

            flash(
                "Informe os horários de início e término.",
                "erro"
            )

            return redirect(
                url_for(
                    "agenda_inteligente.editar",
                    id=id
                )
            )

        if hora_inicio >= hora_fim:

            flash(
                "O horário inicial deve ser anterior ao horário final.",
                "erro"
            )

            return redirect(
                url_for(
                    "agenda_inteligente.editar",
                    id=id
                )
            )

        if intervalo_minutos not in (
            10,
            15,
            20,
            30,
            40,
            45,
            60
        ):

            flash(
                "Selecione um intervalo válido.",
                "erro"
            )

            return redirect(
                url_for(
                    "agenda_inteligente.editar",
                    id=id
                )
            )

        if bool(inicio_almoco) != bool(fim_almoco):

            flash(
                "Informe o início e o término do intervalo de almoço.",
                "erro"
            )

            return redirect(
                url_for(
                    "agenda_inteligente.editar",
                    id=id
                )
            )

        if inicio_almoco and fim_almoco:

            if inicio_almoco >= fim_almoco:

                flash(
                    "O início do almoço deve ser anterior ao término.",
                    "erro"
                )

                return redirect(
                    url_for(
                        "agenda_inteligente.editar",
                        id=id
                    )
                )

            if (
                inicio_almoco < hora_inicio
                or fim_almoco > hora_fim
            ):

                flash(
                    "O intervalo de almoço deve estar dentro do expediente.",
                    "erro"
                )

                return redirect(
                    url_for(
                        "agenda_inteligente.editar",
                        id=id
                    )
                )

        horario_duplicado = (
            HorarioVeterinario.query
            .filter(
                HorarioVeterinario.veterinario_id == veterinario_id,
                HorarioVeterinario.dia_semana == dia_semana,
                HorarioVeterinario.id != horario.id
            )
            .first()
        )

        if horario_duplicado:

            flash(
                "Este veterinário já possui um expediente cadastrado "
                "para esse dia.",
                "erro"
            )

            return redirect(
                url_for(
                    "agenda_inteligente.editar",
                    id=id
                )
            )

        horario.veterinario_id = veterinario_id
        horario.dia_semana = dia_semana
        horario.hora_inicio = hora_inicio
        horario.hora_fim = hora_fim
        horario.inicio_almoco = inicio_almoco
        horario.fim_almoco = fim_almoco
        horario.intervalo_minutos = intervalo_minutos
        horario.ativo = ativo

        try:

            db.session.commit()

            flash(
                "Horário atualizado com sucesso.",
                "sucesso"
            )

            return redirect(
                url_for(
                    "agenda_inteligente.listar"
                )
            )

        except Exception:

            db.session.rollback()

            flash(
                "Não foi possível atualizar o horário.",
                "erro"
            )

    return render_template(
        "agenda_inteligente/editar.html",
        horario=horario,
        veterinarios=veterinarios,
        dias_semana=DIAS_SEMANA
    )


@agenda_inteligente_bp.route(
    "/<int:id>/alternar-status",
    methods=["POST"]
)
@login_required
def alternar_status(id):

    verificar_permissao()

    horario = db.get_or_404(
        HorarioVeterinario,
        id
    )

    try:

        horario.ativo = not horario.ativo

        db.session.commit()

        if horario.ativo:

            mensagem = "Horário ativado com sucesso."

        else:

            mensagem = "Horário desativado com sucesso."

        flash(
            mensagem,
            "sucesso"
        )

    except Exception:

        db.session.rollback()

        flash(
            "Não foi possível alterar o status do horário.",
            "erro"
        )

    return redirect(
        url_for(
            "agenda_inteligente.listar"
        )
    )


@agenda_inteligente_bp.route(
    "/<int:id>/excluir",
    methods=["POST"]
)
@login_required
def excluir(id):

    verificar_permissao()

    horario = db.get_or_404(
        HorarioVeterinario,
        id
    )

    try:

        db.session.delete(horario)
        db.session.commit()

        flash(
            "Horário excluído com sucesso.",
            "sucesso"
        )

    except Exception:

        db.session.rollback()

        flash(
            "Não foi possível excluir o horário.",
            "erro"
        )

    return redirect(
        url_for(
            "agenda_inteligente.listar"
        )
    )