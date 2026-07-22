from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash

from app import db
from app.models.usuario import Usuario

from flask_login import login_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import logout_user, current_user

from app.models.pet import Pet

from app.models.agendamentoConsulta import AgendamentoConsulta

from app.utils.validacoes import cpf_valido

auth_bp = Blueprint("auth", __name__)

import re

from io import BytesIO
from flask import send_file, abort

from app.services.foto_service import FotoService

from app.services.imagem.excecoes import (
    ImagemInvalidaError,
    FormatoNaoPermitidoError,
    ArquivoMuitoGrandeError,
    CompressaoError
)

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

@auth_bp.route("/cadastro", methods=["GET", "POST"])
def cadastro():

    if request.method == "POST":

        nome = request.form.get(
            "nome",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        confirmar_email = request.form.get(
            "confirmar_email",
            ""
        ).strip().lower()

        cpf = request.form.get(
            "cpf",
            ""
        ).strip()

        telefone = request.form.get(
            "telefone",
            ""
        ).strip()

        
        
        
        senha = request.form.get(
            "senha",
            ""
        )

        confirmar_senha = request.form.get(
            "confirmar_senha",
            ""
        )

        cpf_numeros = re.sub(
            r"\D",
            "",
            cpf
        )

        dados_formulario = {
            "nome": nome,
            "email": email,
            "confirmar_email": confirmar_email,
            "cpf": cpf,
            "telefone": telefone
        }

        if not nome:

            flash(
                "Informe o seu nome completo.",
                "danger"
            )

            return render_template(
                "cadastro.html",
                dados=dados_formulario
            )

        if not email:

            flash(
                "Informe um endereço de e-mail.",
                "danger"
            )

            return render_template(
                "cadastro.html",
                dados=dados_formulario
            )

        if not confirmar_email:

            flash(
                "Confirme o endereço de e-mail.",
                "danger"
            )

            return render_template(
                "cadastro.html",
                dados=dados_formulario
            )

        if email != confirmar_email:

            flash(
                "O e-mail e a confirmação de e-mail não coincidem.",
                "warning"
            )

            return render_template(
                "cadastro.html",
                dados=dados_formulario
            )

        if not cpf_numeros:

            flash(
                "Informe o CPF.",
                "danger"
            )

            return render_template(
                "cadastro.html",
                dados=dados_formulario
            )

        if len(cpf_numeros) != 11:

            flash(
                "O CPF deve possuir 11 números.",
                "warning"
            )

            return render_template(
                "cadastro.html",
                dados=dados_formulario
            )


        if not cpf_valido(cpf_numeros):

            flash(
                "Informe um CPF válido.",
                "warning"
            )

            return render_template(
                "cadastro.html",
                dados=dados_formulario
            )

        if not senha:

            flash(
                "Informe uma senha.",
                "danger"
            )

            return render_template(
                "cadastro.html",
                dados=dados_formulario
            )

        if len(senha) < 8:

            flash(
                "A senha deve possuir pelo menos 8 caracteres.",
                "warning"
            )

            return render_template(
                "cadastro.html",
                dados=dados_formulario
            )

        if senha != confirmar_senha:

            flash(
                "A senha e a confirmação não coincidem.",
                "warning"
            )

            return render_template(
                "cadastro.html",
                dados=dados_formulario
            )

        email_existente = Usuario.query.filter(
            Usuario.email == email
        ).first()

        if email_existente:

            flash(
                "Este e-mail já está cadastrado.",
                "warning"
            )

            return render_template(
                "cadastro.html",
                dados=dados_formulario
            )

        cpf_existente = Usuario.query.filter(
            Usuario.cpf == cpf_numeros
        ).first()

        if cpf_existente:

            flash(
                "Este CPF já está cadastrado.",
                "warning"
            )

            return render_template(
                "cadastro.html",
                dados=dados_formulario
            )

        novo_usuario = Usuario(
            nome=nome,
            email=email,
            cpf=cpf_numeros,
            telefone=telefone or None,
            senha_hash=generate_password_hash(
                senha
            )
        )

        try:

            db.session.add(novo_usuario)
            
            db.session.commit()

            flash(
                "Cadastro realizado com sucesso!",
                "success"
            )

            return redirect(
                url_for("auth.login")
            )

        except Exception:

            db.session.rollback()

            flash(
                "Não foi possível realizar o cadastro.",
                "danger"
            )

            return render_template(
                "cadastro.html",
                dados=dados_formulario
            )

    return render_template(
        "cadastro.html",
        dados={}
    )
    
# =========================================================
# MINHA CONTA
# =========================================================

@auth_bp.route("/minha-conta", methods=["GET", "POST"])
@login_required
def minha_conta():

    if request.method == "POST":
        
        foto_perfil = request.files.get(
            "foto_perfil"
        )
        
        nome = request.form.get(
            "nome",
            ""
        ).strip()

        cpf = request.form.get(
            "cpf",
            ""
        ).strip()
        
        cpf = re.sub(r"\D", "", cpf)

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        confirmar_email = request.form.get(
            "confirmar_email",
            ""
        ).strip().lower()

        telefone = request.form.get(
            "telefone",
            ""
        ).strip()

        foto_perfil = request.files.get(
        "foto_perfil"
        )

        # ==========================================
        # ENDEREÇO OPCIONAL
        # ==========================================

        cep = request.form.get(
            "cep",
            ""
        ).strip()

        logradouro = request.form.get(
            "logradouro",
            ""
        ).strip()

        numero = request.form.get(
            "numero",
            ""
        ).strip()

        complemento = request.form.get(
            "complemento",
            ""
        ).strip()

        bairro = request.form.get(
            "bairro",
            ""
        ).strip()

        cidade = request.form.get(
            "cidade",
            ""
        ).strip()

        uf = request.form.get(
            "uf",
            ""
        ).strip().upper()

        cep = re.sub(r"\D", "", cep)

        foto_perfil = request.files.get(
            "foto_perfil"
        )
        
        # ==========================================
        # VALIDAÇÕES
        # ==========================================

        if not nome:

            flash(
                "Informe o seu nome completo.",
                "danger"
            )

            return redirect(
                url_for("auth.minha_conta")
            )


        if not cpf:

            flash(
                "Informe o CPF.",
                "danger"
            )

            return redirect(
                url_for("auth.minha_conta")
            )
            
        if len(cpf) != 11:

            flash(
                "O CPF deve possuir 11 números.",
                "warning"
            )

            return redirect(
                url_for("auth.minha_conta")
            )

        if not cpf_valido(cpf):
            flash(
                "Informe um CPF válido.",
                "danger"
            )

            return redirect(
                url_for("auth.minha_conta")
            )
   
        if not email:

            flash(
                "Informe um endereço de e-mail.",
                "danger"
            )

            return redirect(
                url_for("auth.minha_conta")
            )


        if not confirmar_email:

            flash(
                "Confirme o endereço de e-mail.",
                "danger"
            )

            return redirect(
                url_for("auth.minha_conta")
            )


        if email != confirmar_email:

            flash(
                "O e-mail e a confirmação de e-mail não coincidem.",
                "warning"
            )

            return redirect(
                url_for("auth.minha_conta")
            )


        # ==========================================
        # CPF DUPLICADO
        # ==========================================

        cpf_existente = Usuario.query.filter(
            Usuario.cpf == cpf,
            Usuario.id != current_user.id
        ).first()

        if cpf_existente:

            flash(
                "Este CPF já está cadastrado para outra conta.",
                "warning"
            )

            return redirect(
                url_for("auth.minha_conta")
            )


        # ==========================================
        # EMAIL DUPLICADO
        # ==========================================

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


        # ==========================================
        # ATUALIZA DADOS
        # ==========================================

        current_user.nome = nome
        current_user.cpf = cpf
        current_user.email = email
        current_user.telefone = telefone or None

        current_user.cep = cep or None
        current_user.logradouro = logradouro or None
        current_user.numero = numero or None
        current_user.complemento = complemento or None
        current_user.bairro = bairro or None
        current_user.cidade = cidade or None
        current_user.uf = uf or None

        try:

            if (
                foto_perfil is not None
                and foto_perfil.filename
            ):
                FotoService.salvar_foto_usuario(
                    current_user,
                    foto_perfil
                )

            db.session.commit()

            flash(
                "Dados pessoais atualizados com sucesso!",
                "success"
            )

        except (
            ImagemInvalidaError,
            FormatoNaoPermitidoError,
            ArquivoMuitoGrandeError,
            CompressaoError
        ) as erro:

            db.session.rollback()

            flash(
                str(erro),
                "warning"
            )

        except Exception as erro:

            db.session.rollback()

            print(
                "Erro ao atualizar a conta:",
                repr(erro)
            )

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