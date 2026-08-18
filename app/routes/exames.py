from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user

from app import db
from app.models.exame import Exame
from app.models.historico import Historico
from app.models.pet import Pet

from datetime import datetime

exames_bp = Blueprint(
    "exames",
    __name__,
    url_prefix="/exames"
)

def _buscar_historico_permitido(historico_id):

    consulta = (
        Historico.query
        .join(Pet, Historico.pet_id == Pet.id)
        .filter(
            Historico.id == historico_id
        )
    )

    if not current_user.pode_ver_historico_completo:
        consulta = consulta.filter(
            Pet.tutor_id == current_user.id
        )

    return consulta.first_or_404()


def _buscar_exame_permitido(exame_id):

    consulta = (
        Exame.query
        .join(Historico)
        .join(Pet)
        .filter(
            Exame.id == exame_id
        )
    )

    if not current_user.pode_ver_historico_completo:
        consulta = consulta.filter(
            Pet.tutor_id == current_user.id
        )

    return consulta.first_or_404()

# ==========================================================
# LISTAR EXAMES DE UM PRONTUÁRIO
# ==========================================================

@exames_bp.route("/historico/<int:historico_id>")
@login_required
def listar(historico_id):

    historico = _buscar_historico_permitido(
        historico_id
    )

    exames = (
        Exame.query
        .filter_by(historico_id=historico.id)
        .order_by(
            Exame.data_exame.desc(),
            Exame.id.desc()
        )
        .all()
    )

    return render_template(
        "exames/listar.html",
        historico=historico,
        exames=exames
    )


# ==========================================================
# NOVO EXAME
# ==========================================================

@exames_bp.route(
    "/novo/<int:historico_id>",
    methods=["GET", "POST"]
)
@login_required
def novo(historico_id):

    historico = _buscar_historico_permitido(
        historico_id
    )

    if request.method == "POST":

        nome = request.form.get(
            "nome",
            ""
        ).strip()

        categoria = request.form.get(
            "categoria",
            ""
        ).strip()

        resultado = request.form.get(
            "resultado",
            ""
        ).strip()

        observacoes = request.form.get(
            "observacoes",
            ""
        ).strip()

        data_exame = request.form.get("data_exame")

        if data_exame:

            data_exame = datetime.strptime(
                data_exame,
                "%Y-%m-%d"
            ).date()

        else:

            data_exame = None

        if not nome:

            flash(
                "Informe o nome do exame.",
                "erro"
            )

            return render_template(
                "exames/novo.html",
                historico=historico
            )

        exame = Exame(

            historico_id=historico.id,

            nome=nome,

            categoria=categoria,

            resultado=resultado,

            observacoes=observacoes,

            data_exame=data_exame

        )

        db.session.add(exame)

        db.session.commit()

        flash(
            "Exame cadastrado com sucesso.",
            "sucesso"
        )

        return redirect(
            url_for(
                "historico.detalhes",
                historico_id=historico.id,
                aba="exames"
            )
        )

    return render_template(
        "exames/novo.html",
        historico=historico
    )
    
# ==========================================================
# EDITAR EXAME
# ==========================================================

@exames_bp.route("/editar/<int:exame_id>", methods=["GET", "POST"])
@login_required
def editar(exame_id):

    exame = _buscar_exame_permitido(
        exame_id
    )

    if request.method == "POST":

        nome = request.form.get(
            "nome",
            ""
        ).strip()

        categoria = request.form.get(
            "categoria",
            ""
        ).strip()

        resultado = request.form.get(
            "resultado",
            ""
        ).strip()

        observacoes = request.form.get(
            "observacoes",
            ""
        ).strip()

        if not nome:

            flash(
                "Informe o nome do exame.",
                "erro"
            )

            return render_template(
                "exames/editar.html",
                exame=exame
            )

        exame.nome = nome
        exame.categoria = categoria
        exame.resultado = resultado
        exame.observacoes = observacoes

        data = request.form.get("data_exame")

        if data:
            exame.data_exame = datetime.strptime(
                data,
                "%Y-%m-%d"
            ).date()
        else:
            exame.data_exame = None

        db.session.commit()

        flash(
            "Exame atualizado com sucesso.",
            "sucesso"
        )

        return redirect(
            url_for(
                "historico.detalhes",
                historico_id=exame.historico_id,
                aba="exames"
            )
        )

    return render_template(
        "exames/editar.html",
        exame=exame
    )


# ==========================================================
# EXCLUIR EXAME
# ==========================================================

@exames_bp.route(
    "/excluir/<int:exame_id>",
    methods=["POST"]
)
@login_required
def excluir(exame_id):

    exame = _buscar_exame_permitido(
        exame_id
    )

    historico_id = exame.historico_id

    db.session.delete(exame)

    db.session.commit()

    flash(
        "Exame removido com sucesso.",
        "sucesso"
    )

    return redirect(
        url_for(
            "historico.detalhes",
            historico_id=historico_id,
            aba="exames"
        )
    )