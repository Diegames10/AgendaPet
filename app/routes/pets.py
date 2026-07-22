from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app import db
from app.models.pet import Pet

from app.services.foto_service import FotoService


pets_bp = Blueprint(
    "pets",
    __name__,
    url_prefix="/pets"
)


@pets_bp.route("/")
@login_required
def listar():

    pets = (
        Pet.query
        .filter_by(tutor_id=current_user.id)
        .order_by(Pet.nome.asc())
        .all()
    )

    return render_template(
        "pets/listar.html",
        pets=pets
    )


@pets_bp.route("/cadastrar", methods=["GET", "POST"])
@login_required
def cadastrar():

    if request.method == "POST":

        nome = request.form.get("nome", "").strip()
        especie = request.form.get("especie", "").strip()
        raca = request.form.get("raca", "").strip()
        sexo = request.form.get("sexo", "").strip()
        data_nascimento_texto = request.form.get("data_nascimento", "").strip()
        peso_texto = request.form.get("peso", "").strip()
        cor = request.form.get("cor", "").strip()
        observacoes = request.form.get("observacoes", "").strip()

        if not nome or not especie:
            flash(
                "Informe pelo menos o nome e a espécie do pet.",
                "danger"
            )
            return redirect(url_for("pets.cadastrar"))

        data_nascimento = None

        if data_nascimento_texto:
            try:
                data_nascimento = datetime.strptime(
                    data_nascimento_texto,
                    "%Y-%m-%d"
                ).date()
            except ValueError:
                flash("Data de nascimento inválida.", "danger")
                return redirect(url_for("pets.cadastrar"))

        peso = None

        if peso_texto:
            try:
                peso = float(peso_texto)

                if peso <= 0:
                    raise ValueError

            except ValueError:
                flash("Informe um peso válido.", "danger")
                return redirect(url_for("pets.cadastrar"))

        novo_pet = Pet(
            nome=nome,
            especie=especie,
            raca=raca or None,
            sexo=sexo or None,
            data_nascimento=data_nascimento,
            peso=peso,
            cor=cor or None,
            observacoes=observacoes or None,
            tutor_id=current_user.id
        )

        db.session.add(novo_pet)

        # Precisamos do ID do pet
        db.session.flush()

        try:

            FotoService.salvar_fotos_pet(
                pet=novo_pet,
                arquivos=request.files.getlist("fotos")
            )

        except ValueError as erro:

            db.session.rollback()

            flash(str(erro), "danger")

            return redirect(
                url_for("pets.cadastrar")
            )

        db.session.commit()

        flash("Pet cadastrado com sucesso!", "success")

        return redirect(url_for("pets.listar"))

    return render_template("pets/cadastrar.html")


@pets_bp.route("/<int:pet_id>/editar", methods=["GET", "POST"])
@login_required
def editar(pet_id):

    pet = Pet.query.filter_by(
        id=pet_id,
        tutor_id=current_user.id
    ).first_or_404()

    if request.method == "POST":

        nome = request.form.get("nome", "").strip()
        especie = request.form.get("especie", "").strip()
        raca = request.form.get("raca", "").strip()
        sexo = request.form.get("sexo", "").strip()
        data_nascimento_texto = request.form.get("data_nascimento", "").strip()
        peso_texto = request.form.get("peso", "").strip()
        cor = request.form.get("cor", "").strip()
        observacoes = request.form.get("observacoes", "").strip()

        if not nome or not especie:
            flash(
                "Informe pelo menos o nome e a espécie do pet.",
                "danger"
            )
            return redirect(
                url_for("pets.editar", pet_id=pet.id)
            )

        data_nascimento = None

        if data_nascimento_texto:
            try:
                data_nascimento = datetime.strptime(
                    data_nascimento_texto,
                    "%Y-%m-%d"
                ).date()
            except ValueError:
                flash("Data de nascimento inválida.", "danger")
                return redirect(
                    url_for("pets.editar", pet_id=pet.id)
                )

        peso = None

        if peso_texto:
            try:
                peso = float(peso_texto)

                if peso <= 0:
                    raise ValueError

            except ValueError:
                flash("Informe um peso válido.", "danger")
                return redirect(
                    url_for("pets.editar", pet_id=pet.id)
                )

        pet.nome = nome
        pet.especie = especie
        pet.raca = raca or None
        pet.sexo = sexo or None
        pet.data_nascimento = data_nascimento
        pet.peso = peso
        pet.cor = cor or None
        pet.observacoes = observacoes or None

           
        try:

            FotoService.salvar_fotos_pet(
                pet=pet,
                arquivos=request.files.getlist("fotos")
            )

        except ValueError as erro:

            db.session.rollback()

            flash(str(erro), "danger")

            return redirect(
                url_for(
                    "pets.editar",
                    pet_id=pet.id
                )
            )   
        
            
        db.session.commit()

        flash("Dados do pet atualizados com sucesso!", "success")

        return redirect(url_for("pets.listar"))

    return render_template(
        "pets/editar.html",
        pet=pet
    )

@pets_bp.route(
    "/<int:pet_id>/fotos/<int:foto_id>/principal",
    methods=["POST"]
)
@login_required
def definir_foto_principal(
    pet_id,
    foto_id
):

    pet = Pet.query.filter_by(
        id=pet_id,
        tutor_id=current_user.id
    ).first_or_404()

    try:

        FotoService.definir_foto_principal(
            pet=pet,
            foto_id=foto_id
        )

        db.session.commit()

        flash(
            "Foto principal alterada com sucesso!",
            "success"
        )

    except ValueError as erro:

        db.session.rollback()
        flash(str(erro), "danger")

    return redirect(
        url_for(
            "pets.editar",
            pet_id=pet.id
        )
    )


@pets_bp.route(
    "/<int:pet_id>/fotos/<int:foto_id>/excluir",
    methods=["POST"]
)
@login_required
def excluir_foto(
    pet_id,
    foto_id
):

    pet = Pet.query.filter_by(
        id=pet_id,
        tutor_id=current_user.id
    ).first_or_404()

    try:

        FotoService.remover_foto_pet(
            pet=pet,
            foto_id=foto_id
        )

        db.session.commit()

        flash(
            "Foto excluída com sucesso!",
            "success"
        )

    except ValueError as erro:

        db.session.rollback()
        flash(str(erro), "danger")

    return redirect(
        url_for(
            "pets.editar",
            pet_id=pet.id
        )
    )


@pets_bp.route("/<int:pet_id>/excluir", methods=["POST"])
@login_required
def excluir(pet_id):

    pet = Pet.query.filter_by(
        id=pet_id,
        tutor_id=current_user.id
    ).first_or_404()

    nome_pet = pet.nome

    db.session.delete(pet)
    db.session.commit()

    flash(
        f"O pet {nome_pet} foi excluído com sucesso.",
        "success"
    )

    return redirect(url_for("pets.listar"))