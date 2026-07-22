from flask import Blueprint, render_template, request, redirect, url_for, flash

from flask_login import login_required

from app import db

from app.models.veterinario import Veterinario

from flask import abort

veterinarios_bp = Blueprint(
    "veterinarios",
    __name__,
    url_prefix="/veterinarios"
)


@veterinarios_bp.route("/")
@login_required
def listar():

    veterinarios = Veterinario.query.all()

    return render_template(
        "veterinarios/listar_veterinarios.html",
        veterinarios=veterinarios
    )


@veterinarios_bp.route(
    "/cadastrar",
    methods=["GET", "POST"]
)
@login_required
def cadastrar():

    if request.method == "POST":

        nome = request.form.get("nome")
        crmv = request.form.get("crmv")
        especialidade = request.form.get("especialidade")
        telefone = request.form.get("telefone")
        email = request.form.get("email")


        novo_veterinario = Veterinario(
            nome=nome,
            crmv=crmv,
            especialidade=especialidade,
            telefone=telefone,
            email=email
        )


        db.session.add(novo_veterinario)

        db.session.commit()


        flash(
            "Veterinário cadastrado com sucesso!",
            "success"
        )


        return redirect(
            url_for("veterinarios.listar")
        )


    return render_template(
        "veterinarios/cadastrar_veterinarios.html"
    )
    
@veterinarios_bp.route(
    "/editar/<int:id>",
    methods=["GET", "POST"]
)
@login_required
def editar(id):

    veterinario = Veterinario.query.get_or_404(id)


    if request.method == "POST":

        veterinario.nome = request.form.get("nome")
        veterinario.crmv = request.form.get("crmv")
        veterinario.especialidade = request.form.get("especialidade")
        veterinario.telefone = request.form.get("telefone")
        veterinario.email = request.form.get("email")


        db.session.commit()


        flash(
            "Veterinário atualizado com sucesso!",
            "success"
        )


        return redirect(
            url_for("veterinarios.listar")
        )


    return render_template(
        "veterinarios/editar_veterinario.html",
        veterinario=veterinario
    )
    
@veterinarios_bp.route(
    "/excluir/<int:id>"
)
@login_required
def excluir(id):

    veterinario = Veterinario.query.get_or_404(id)


    db.session.delete(veterinario)

    db.session.commit()


    flash(
        "Veterinário removido com sucesso!",
        "success"
    )


    return redirect(
        url_for("veterinarios.listar")
    )
    
