from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app.auth.permissions import roles_permitidas
from app.models.usuario import Usuario, TipoUsuario

from werkzeug.security import generate_password_hash
from app import db

from app.services.foto_service import FotoService

usuarios_bp = Blueprint(
    "usuarios",
    __name__,
    url_prefix="/usuarios"
)


@usuarios_bp.route("/")
@login_required
@roles_permitidas(TipoUsuario.ADMIN)
def listar():

    pesquisa = request.args.get("pesquisa", "").strip()

    pagina = request.args.get(
        "pagina",
        1,
        type=int
    )

    consulta = Usuario.query

    if pesquisa:
        termo = f"%{pesquisa}%"

        consulta = consulta.filter(
            db.or_(
                Usuario.nome.ilike(termo),
                Usuario.cpf.ilike(termo),
                Usuario.email.ilike(termo)
            )
        )

    paginacao = consulta.order_by(
        Usuario.nome.asc()
    ).paginate(
        page=pagina,
        per_page=10,
        error_out=False
    )

    return render_template(
        "usuarios/listar.html",
        usuarios=paginacao.items,
        paginacao=paginacao,
        pesquisa=pesquisa
    )
    
@usuarios_bp.route("/novo", methods=["GET", "POST"])
@login_required
@roles_permitidas(TipoUsuario.ADMIN)
def novo():

    if request.method == "POST":

        nome = request.form.get("nome", "").strip()
        cpf = request.form.get("cpf", "").strip()
        telefone = request.form.get("telefone", "").strip()
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")
        confirmar_senha = request.form.get("confirmar_senha", "")
        tipo_usuario = request.form.get("tipo_usuario", "").strip()
        ativo = request.form.get("ativo") == "on"

        crmv = request.form.get(
            "crmv",
            ""
        ).strip().upper()

        especialidade = request.form.get(
            "especialidade",
            ""
        ).strip()

        foto_perfil = request.files.get(
            "foto_perfil"
        )
        
        # Mantém somente os números do CPF
        cpf_numeros = "".join(
            caractere
            for caractere in cpf
            if caractere.isdigit()
        )

        # ==========================================
        # CAMPOS OBRIGATÓRIOS
        # ==========================================

        if not nome:
            flash(
                "Informe o nome completo do usuário.",
                "erro"
            )

            return render_template(
                "usuarios/novo.html"
            )

        if len(cpf_numeros) != 11:
            flash(
                "Informe um CPF válido com 11 números.",
                "erro"
            )

            return render_template(
                "usuarios/novo.html"
            )

        if not email:
            flash(
                "Informe o e-mail do usuário.",
                "erro"
            )

            return render_template(
                "usuarios/novo.html"
            )

        if not senha:
            flash(
                "Informe uma senha para o usuário.",
                "erro"
            )

            return render_template(
                "usuarios/novo.html"
            )

        # ==========================================
        # CONFIRMAÇÃO DA SENHA
        # ==========================================

        if senha != confirmar_senha:
            flash(
                "A senha e a confirmação não são iguais.",
                "erro"
            )

            return render_template(
                "usuarios/novo.html"
            )

        if len(senha) < 6:
            flash(
                "A senha deve possuir pelo menos 6 caracteres.",
                "erro"
            )

            return render_template(
                "usuarios/novo.html"
            )

        # ==========================================
        # TIPO DE USUÁRIO
        # ==========================================

        if tipo_usuario not in TipoUsuario.TODOS:
            flash(
                "Selecione um tipo de usuário válido.",
                "erro"
            )

            return render_template(
                "usuarios/novo.html"
            )

        # ==========================================
        # DADOS PROFISSIONAIS
        # ==========================================

        if tipo_usuario == TipoUsuario.VETERINARIO:

            if not crmv:
                flash(
                    "Informe o CRMV do veterinário.",
                    "erro"
                )

                return render_template(
                    "usuarios/novo.html",
                    nome=nome,
                    cpf=cpf,
                    telefone=telefone,
                    email=email,
                    tipo_usuario=tipo_usuario,
                    ativo=ativo,
                    crmv=crmv,
                    especialidade=especialidade
                )

            if not especialidade:
                flash(
                    "Informe a especialidade do veterinário.",
                    "erro"
                )

                return render_template(
                    "usuarios/novo.html",
                    nome=nome,
                    cpf=cpf,
                    telefone=telefone,
                    email=email,
                    tipo_usuario=tipo_usuario,
                    ativo=ativo,
                    crmv=crmv,
                    especialidade=especialidade
                )

            crmv_existente = Usuario.query.filter(
                Usuario.crmv == crmv
            ).first()

            if crmv_existente:
                flash(
                    "Já existe um veterinário cadastrado com este CRMV.",
                    "erro"
                )

                return render_template(
                    "usuarios/novo.html",
                    nome=nome,
                    cpf=cpf,
                    telefone=telefone,
                    email=email,
                    tipo_usuario=tipo_usuario,
                    ativo=ativo,
                    crmv=crmv,
                    especialidade=especialidade
                )

        else:
            crmv = None
            especialidade = None
        
        # ==========================================
        # VERIFICAÇÃO DE CPF
        # ==========================================

        usuario_com_cpf = Usuario.query.filter_by(
            cpf=cpf_numeros
        ).first()

        if usuario_com_cpf:
            flash(
                "Já existe um usuário cadastrado com este CPF.",
                "erro"
            )

            return render_template(
                "usuarios/novo.html"
            )

        # ==========================================
        # VERIFICAÇÃO DE E-MAIL
        # ==========================================

        usuario_com_email = Usuario.query.filter_by(
            email=email
        ).first()

        if usuario_com_email:
            flash(
                "Já existe um usuário cadastrado com este e-mail.",
                "erro"
            )

            return render_template(
                "usuarios/novo.html"
            )

        # ==========================================
        # CRIAÇÃO DO USUÁRIO
        # ==========================================

        novo_usuario = Usuario(
            nome=nome,
            cpf=cpf_numeros,
            telefone=telefone or None,
            email=email,
            senha_hash=generate_password_hash(senha),
            tipo_usuario=tipo_usuario,
            ativo=ativo,
            crmv=crmv,
            especialidade=especialidade
        )

        try:

            db.session.add(novo_usuario)

            # Garante que o usuário receba um ID antes
            # de relacionar a foto.
            db.session.flush()

            if (
                foto_perfil is not None
                and foto_perfil.filename
            ):
                FotoService.salvar_foto_usuario(
                    novo_usuario,
                    foto_perfil
                )

            db.session.commit()

            flash(
                "Usuário cadastrado com sucesso.",
                "sucesso"
            )

            return redirect(
                url_for("usuarios.listar")
            )

        except Exception as erro:

            db.session.rollback()

            print(
                "Erro ao cadastrar usuário:",
                repr(erro)
            )

            flash(
                "Não foi possível cadastrar o usuário.",
                "erro"
            )

            return render_template(
                "usuarios/novo.html",
                nome=nome,
                cpf=cpf,
                telefone=telefone,
                email=email,
                tipo_usuario=tipo_usuario,
                ativo=ativo,
                crmv=crmv or "",
                especialidade=especialidade or ""
            )

            db.session.add(novo_usuario)
            db.session.commit()

            flash(
                "Usuário cadastrado com sucesso.",
                "sucesso"
            )

            return redirect(
                url_for("usuarios.listar")
            )

        except Exception:

            db.session.rollback()

            flash(
                "Não foi possível cadastrar o usuário.",
                "erro"
            )

            return render_template(
                "usuarios/novo.html",
                nome=nome,
                cpf=cpf,
                telefone=telefone,
                email=email,
                tipo_usuario=tipo_usuario,
                ativo=True
            )
            
    # GET: abre o formulário vazio
    return render_template(
        "usuarios/novo.html",
        nome="",
        cpf="",
        telefone="",
        email="",
        tipo_usuario="",
        ativo=True
    )
    
@usuarios_bp.route("/<int:id>/editar", methods=["GET", "POST"])
@login_required
@roles_permitidas(TipoUsuario.ADMIN)
def editar(id):

    usuario = Usuario.query.get_or_404(id)

    if request.method == "POST":

        nome = request.form.get("nome", "").strip()
        cpf = request.form.get("cpf", "").strip()
        telefone = request.form.get("telefone", "").strip()
        email = request.form.get("email", "").strip().lower()
        tipo_usuario = request.form.get("tipo_usuario", "").strip()
        ativo = request.form.get("ativo") == "on"

        cpf_numeros = "".join(
            caractere
            for caractere in cpf
            if caractere.isdigit()
        )

        # ==========================================
        # VALIDAÇÕES
        # ==========================================

        if not nome:
            flash(
                "Informe o nome completo do usuário.",
                "erro"
            )

            return render_template(
                "usuarios/editar.html",
                usuario=usuario,
                nome=nome,
                cpf=cpf,
                telefone=telefone,
                email=email,
                tipo_usuario=tipo_usuario,
                ativo=ativo
            )

        if len(cpf_numeros) != 11:
            flash(
                "Informe um CPF válido com 11 números.",
                "erro"
            )

            return render_template(
                "usuarios/editar.html",
                usuario=usuario,
                nome=nome,
                cpf=cpf,
                telefone=telefone,
                email=email,
                tipo_usuario=tipo_usuario,
                ativo=ativo
            )

        if not email:
            flash(
                "Informe o e-mail do usuário.",
                "erro"
            )

            return render_template(
                "usuarios/editar.html",
                usuario=usuario,
                nome=nome,
                cpf=cpf,
                telefone=telefone,
                email=email,
                tipo_usuario=tipo_usuario,
                ativo=ativo
            )

        if tipo_usuario not in TipoUsuario.TODOS:
            flash(
                "Selecione um tipo de usuário válido.",
                "erro"
            )

            return render_template(
                "usuarios/editar.html",
                usuario=usuario,
                nome=nome,
                cpf=cpf,
                telefone=telefone,
                email=email,
                tipo_usuario=tipo_usuario,
                ativo=ativo
            )

        # ==========================================
        # CPF DUPLICADO
        # ==========================================

        usuario_com_cpf = Usuario.query.filter(
            Usuario.cpf == cpf_numeros,
            Usuario.id != usuario.id
        ).first()

        if usuario_com_cpf:
            flash(
                "Já existe outro usuário cadastrado com este CPF.",
                "erro"
            )

            return render_template(
                "usuarios/editar.html",
                usuario=usuario,
                nome=nome,
                cpf=cpf,
                telefone=telefone,
                email=email,
                tipo_usuario=tipo_usuario,
                ativo=ativo
            )

        # ==========================================
        # E-MAIL DUPLICADO
        # ==========================================

        usuario_com_email = Usuario.query.filter(
            Usuario.email == email,
            Usuario.id != usuario.id
        ).first()

        if usuario_com_email:
            flash(
                "Já existe outro usuário cadastrado com este e-mail.",
                "erro"
            )

            return render_template(
                "usuarios/editar.html",
                usuario=usuario,
                nome=nome,
                cpf=cpf,
                telefone=telefone,
                email=email,
                tipo_usuario=tipo_usuario,
                ativo=ativo
            )

        # ==========================================
        # ATUALIZAÇÃO
        # ==========================================

        usuario.nome = nome
        usuario.cpf = cpf_numeros
        usuario.telefone = telefone or None
        usuario.email = email
        usuario.tipo_usuario = tipo_usuario
        usuario.ativo = ativo

        try:

            db.session.commit()

            flash(
                "Usuário atualizado com sucesso.",
                "sucesso"
            )

            return redirect(
                url_for("usuarios.listar")
            )

        except Exception:

            db.session.rollback()

            flash(
                "Não foi possível atualizar o usuário.",
                "erro"
            )

    return render_template(
        "usuarios/editar.html",
        usuario=usuario,
        nome=usuario.nome,
        cpf=usuario.cpf,
        telefone=usuario.telefone or "",
        email=usuario.email,
        tipo_usuario=usuario.tipo_usuario,
        ativo=usuario.ativo
    )
    
@usuarios_bp.route("/<int:id>/alterar-status", methods=["POST"])
@login_required
@roles_permitidas(TipoUsuario.ADMIN)
def alterar_status(id):

    usuario = Usuario.query.get_or_404(id)

    # Impede que o administrador desative a própria conta
    from flask_login import current_user

    if usuario.id == current_user.id:
        flash(
            "Você não pode desativar a própria conta.",
            "warning"
        )

        return redirect(
            url_for("usuarios.listar")
        )

    usuario.ativo = not usuario.ativo

    try:

        db.session.commit()

        if usuario.ativo:
            flash(
                f"O usuário {usuario.nome} foi ativado com sucesso.",
                "success"
            )
        else:
            flash(
                f"O usuário {usuario.nome} foi desativado com sucesso.",
                "warning"
            )

    except Exception:

        db.session.rollback()

        flash(
            "Não foi possível alterar o status do usuário.",
            "danger"
        )

    return redirect(
        url_for("usuarios.listar")
    )
    
@usuarios_bp.route("/<int:id>/resetar-senha", methods=["GET", "POST"])
@login_required
@roles_permitidas(TipoUsuario.ADMIN)
def resetar_senha(id):

    usuario = Usuario.query.get_or_404(id)

    if request.method == "POST":

        senha = request.form.get("senha", "")
        confirmar = request.form.get("confirmar_senha", "")

        if len(senha) < 6:
            flash(
                "A senha deve possuir pelo menos 6 caracteres.",
                "warning"
            )

            return render_template(
                "usuarios/resetar_senha.html",
                usuario=usuario
            )

        if senha != confirmar:

            flash(
                "As senhas não conferem.",
                "warning"
            )

            return render_template(
                "usuarios/resetar_senha.html",
                usuario=usuario
            )

        usuario.senha_hash = generate_password_hash(senha)

        try:

            db.session.commit()

            flash(
                "Senha alterada com sucesso.",
                "success"
            )

            return redirect(
                url_for("usuarios.listar")
            )

        except Exception:

            db.session.rollback()

            flash(
                "Não foi possível alterar a senha.",
                "danger"
            )

    return render_template(
        "usuarios/resetar_senha.html",
        usuario=usuario
    )