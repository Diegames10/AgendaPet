from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash

from app import db
from app.models.usuario import Usuario

from flask_login import login_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import logout_user, current_user

from app.models.pet import Pet

from app.models.agendamentoConsulta import AgendamentoConsulta

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def index():
    return render_template("index.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        senha = request.form.get("senha")

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and check_password_hash(usuario.senha_hash, senha):

            login_user(usuario)

            flash("Login realizado com sucesso!", "success")

            return redirect(url_for("auth.painel"))

        flash("E-mail ou senha inválidos.", "danger")

        return redirect(url_for("auth.login"))

    return render_template("login.html")


@auth_bp.route("/cadastro", methods=["GET", "POST"])
def cadastro():

    if request.method == "POST":

        nome = request.form.get("nome")
        email = request.form.get("email")
        cpf = request.form.get("cpf")
        senha = request.form.get("senha")
        confirmar = request.form.get("confirmar_senha")

        # valida senha
        if senha != confirmar:
            flash("As senhas não coincidem.", "danger")
            return redirect(url_for("auth.cadastro"))

        # email existente
        if Usuario.query.filter_by(email=email).first():
            flash("Este e-mail já está cadastrado.", "warning")
            return redirect(url_for("auth.cadastro"))

        # cpf existente
        if Usuario.query.filter_by(cpf=cpf).first():
            flash("Este CPF já está cadastrado.", "warning")
            return redirect(url_for("auth.cadastro"))

        senha_hash = generate_password_hash(senha)

        novo_usuario = Usuario(
            nome=nome,
            email=email,
            cpf=cpf,
            senha_hash=senha_hash
        )

        db.session.add(novo_usuario)
        db.session.commit()

        flash("Cadastro realizado com sucesso!", "success")

        return redirect(url_for("auth.login"))

    return render_template("cadastro.html")


@auth_bp.route("/painel")
@login_required
def painel():

    total_pets = Pet.query.filter_by(
        tutor_id=current_user.id
    ).count()


    lista_agendamentos = AgendamentoConsulta.query.filter(
        AgendamentoConsulta.tutor_id == current_user.id,
        AgendamentoConsulta.status != "Cancelado"
    ).order_by(
        AgendamentoConsulta.data.asc(),
        AgendamentoConsulta.horario.asc()
    ).limit(3).all()


    proximo_atendimento = None

    if lista_agendamentos:
        proximo_atendimento = lista_agendamentos[0]


    return render_template(
        "painel.html",
        total_pets=total_pets,
        proximos_agendamentos=len(lista_agendamentos),
        proximo_atendimento=proximo_atendimento,
        lista_agendamentos=lista_agendamentos
    )
    
# =========================================================
# MINHA CONTA
# =========================================================

@auth_bp.route("/minha-conta", methods=["GET", "POST"])
@login_required
def minha_conta():

    if request.method == "POST":

        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip().lower()
        telefone = request.form.get("telefone", "").strip()

        # Validação do nome
        if not nome:
            flash("Informe o seu nome completo.", "danger")

            return redirect(
                url_for("auth.minha_conta")
            )

        # Validação do e-mail
        if not email:
            flash("Informe um endereço de e-mail.", "danger")

            return redirect(
                url_for("auth.minha_conta")
            )

        # Verifica se o novo e-mail já pertence a outra conta
        email_existente = Usuario.query.filter(
            Usuario.email == email,
            Usuario.id != current_user.id
        ).first()

        if email_existente:
            flash(
                "Este e-mail já está sendo utilizado por outra conta.",
                "warning"
            )

            return redirect(
                url_for("auth.minha_conta")
            )

        current_user.nome = nome
        current_user.email = email
        current_user.telefone = telefone or None

        try:
            db.session.commit()

            flash(
                "Dados pessoais atualizados com sucesso!",
                "success"
            )

        except Exception:
            db.session.rollback()

            flash(
                "Não foi possível atualizar os dados da conta.",
                "danger"
            )

        return redirect(
            url_for("auth.minha_conta")
        )

    return render_template(
        "minha_conta.html"
    )


# =========================================================
# ALTERAR SENHA
# =========================================================

@auth_bp.route("/minha-conta/alterar-senha", methods=["POST"])
@login_required
def alterar_senha():

    senha_atual = request.form.get("senha_atual", "")
    nova_senha = request.form.get("nova_senha", "")
    confirmar_senha = request.form.get(
        "confirmar_senha",
        ""
    )

    if not senha_atual:
        flash(
            "Informe a sua senha atual.",
            "danger"
        )

        return redirect(
            url_for("auth.minha_conta")
        )

    if not check_password_hash(
        current_user.senha_hash,
        senha_atual
    ):
        flash(
            "A senha atual está incorreta.",
            "danger"
        )

        return redirect(
            url_for("auth.minha_conta")
        )

    if len(nova_senha) < 8:
        flash(
            "A nova senha deve possuir pelo menos 8 caracteres.",
            "warning"
        )

        return redirect(
            url_for("auth.minha_conta")
        )

    if nova_senha != confirmar_senha:
        flash(
            "A nova senha e a confirmação não coincidem.",
            "warning"
        )

        return redirect(
            url_for("auth.minha_conta")
        )

    if check_password_hash(
        current_user.senha_hash,
        nova_senha
    ):
        flash(
            "A nova senha deve ser diferente da senha atual.",
            "warning"
        )

        return redirect(
            url_for("auth.minha_conta")
        )

    current_user.senha_hash = generate_password_hash(
        nova_senha
    )

    try:
        db.session.commit()

        flash(
            "Senha alterada com sucesso!",
            "success"
        )

    except Exception:
        db.session.rollback()

        flash(
            "Não foi possível alterar a senha.",
            "danger"
        )

    return redirect(
        url_for("auth.minha_conta")
    )

@auth_bp.route("/logout")
@login_required
def logout():

    logout_user()

    flash("Você saiu do sistema com sucesso.", "success")

    return redirect(url_for("auth.login"))