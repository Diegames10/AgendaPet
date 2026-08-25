from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash
from abc import ABC, abstractmethod

from app import db
from app.models.usuario import Usuario

from flask_login import login_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import logout_user, current_user

from app.models.pet import Pet

from app.models.agendamentoConsulta import AgendamentoConsulta

from app.utils.validacoes import (
    cpf_valido,
    telefone_valido
)

import requests

from io import BytesIO
from werkzeug.datastructures import FileStorage

from app.services.foto_service import FotoService

auth_bp = Blueprint("auth", __name__)


class Request(ABC):
    """Utilitário para acesso seguro a dados de requisição.

    A implementação concentra a lógica de leitura de parâmetros, JSON e
    conversão de tipos em um único ponto, mantendo o uso em rotas simples e
    previsível.
    """

    @property
    @abstractmethod
    def data(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def files(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def method(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def headers(self):
        raise NotImplementedError

    def get(self, key, default=None, type=None):
        valor = self.data.get(key, default)
        if valor is None or valor == "":
            return default
        if type is not None:
            try:
                return type(valor)
            except (TypeError, ValueError):
                return default
        return valor

    def getlist(self, key, default=None):
        valores = self.data.getlist(key)
        return valores if valores else (default or [])

    def get_json(self, default=None, silent=False):
        payload = self.data.get_json(silent=silent)
        return payload if payload is not None else default

    def get_int(self, key, default=0):
        return self.get(key, default, int)

    def get_float(self, key, default=0.0):
        return self.get(key, default, float)

    def get_bool(self, key, default=False):
        valor = self.get(key)
        if isinstance(valor, bool):
            return valor
        if valor is None:
            return default
        if isinstance(valor, str):
            return valor.strip().lower() in {"1", "true", "yes", "on"}
        return bool(valor)

    def is_json(self):
        return "application/json" in (self.headers.get("Content-Type", "") or "")


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

from app.models.conta_oauth import ContaOAuth
from app.auth.oauth import oauth

import secrets

# =========================================================
# AUXILIAR - LOGIN OAUTH
# =========================================================

def _processar_login_oauth(
    provedor,
    provedor_usuario_id,
    nome,
    email,
    foto_url=None,
    token=None,
):

    email = (email or "").strip().lower()
    nome = (nome or "").strip()

    if not provedor_usuario_id:

        flash(
            "Não foi possível identificar a conta externa.",
            "danger"
        )

        return redirect(
            url_for("auth.login")
        )

    if not email:

        flash(
            "O provedor não forneceu um endereço de e-mail.",
            "danger"
        )

        return redirect(
            url_for("auth.login")
        )

    # =====================================================
    # 1. JÁ EXISTE VÍNCULO OAUTH?
    # =====================================================

    conta_oauth = ContaOAuth.query.filter_by(
        provedor=provedor,
        provedor_usuario_id=provedor_usuario_id
    ).first()

    if conta_oauth:

        usuario = conta_oauth.usuario

        if not usuario.ativo:

            flash(
                "Esta conta está desativada.",
                "danger"
            )

            return redirect(
                url_for("auth.login")
            )

        if provedor == "google":
            # Importa foto do Google caso ainda não exista
            _importar_foto_google(
                usuario,
                foto_url
            )
        
        elif provedor == "microsoft":

            _importar_foto_microsoft(
                usuario,
                token
            )
        
        login_user(
            usuario,
            remember=True
        )

        flash(
            f"Login com {provedor.title()} realizado com sucesso!",
            "success"
        )

        return redirect(
            url_for("auth.painel")
        )

    # =====================================================
    # 2. PROCURA USUÁRIO PELO E-MAIL
    # =====================================================

    usuario = Usuario.query.filter_by(
        email=email
    ).first()

    if usuario:

        if not usuario.ativo:

            flash(
                "Esta conta está desativada.",
                "danger"
            )

            return redirect(
                url_for("auth.login")
            )

        # =================================================
        # VINCULA OAUTH À CONTA EXISTENTE
        # =================================================

        nova_conta_oauth = ContaOAuth(
            usuario_id=usuario.id,
            provedor=provedor,
            provedor_usuario_id=provedor_usuario_id,
            email_provedor=email
        )

        try:

            db.session.add(
                nova_conta_oauth
            )

            db.session.commit()

        except Exception as erro:

            db.session.rollback()

            print(
                "Erro ao vincular conta OAuth:",
                repr(erro)
            )

            flash(
                "Não foi possível vincular a conta externa.",
                "danger"
            )

            return redirect(
                url_for("auth.login")
            )

        # =================================================
        # LOGIN APÓS VÍNCULO
        # =================================================

        login_user(
            usuario,
            remember=True
        )

        flash(
            f"Conta {provedor.title()} vinculada com sucesso!",
            "success"
        )

        return redirect(
            url_for("auth.painel")
        )
        
    # =====================================================
    # 3. USUÁRIO NOVO
    # =====================================================

    session["oauth_cadastro"] = {
        "provedor": provedor,
        "provedor_usuario_id": provedor_usuario_id,
        "nome": nome,
        "email": email,
        "foto_url": foto_url
    }

    return redirect(
        url_for(
            "auth.completar_cadastro_oauth"
        )
    )

@auth_bp.route("/")
def index():
    return render_template("index.html")

# =========================================================
# SALVAR FOTO RECEBIDA DO OAUTH
# =========================================================

def _salvar_foto_oauth(
    usuario,
    dados_imagem,
    nome_arquivo="foto_oauth.jpg",
    content_type="image/jpeg"
):

    if not dados_imagem:
        return False

    try:

        arquivo = FileStorage(
            stream=BytesIO(dados_imagem),
            filename=nome_arquivo,
            content_type=content_type
        )

        FotoService.salvar_foto_usuario(
            usuario,
            arquivo
        )

        return True

    except Exception as erro:

        print(
            "Erro ao salvar foto OAuth:",
            repr(erro)
        )

        return False
    
    
# =========================================================
# LOGIN GOOGLE
# =========================================================

@auth_bp.route("/login/google")
def login_google():

    if current_user.is_authenticated:

        return redirect(
            url_for("auth.painel")
        )

    redirect_uri = url_for(
        "auth.google_callback",
        _external=True
    )

    return oauth.google.authorize_redirect(
        redirect_uri
    )
    
# =========================================================
# CALLBACK GOOGLE
# =========================================================

@auth_bp.route("/login/google/callback")
def google_callback():

    try:

        token = oauth.google.authorize_access_token()

        usuario_google = token.get(
            "userinfo"
        )

        if not usuario_google:

            usuario_google = (
                oauth.google.userinfo(
                    token=token
                )
            )

        return _processar_login_oauth(
            provedor="google",

            provedor_usuario_id=usuario_google.get(
                "sub"
            ),

            nome=usuario_google.get(
                "name"
            ),

            email=usuario_google.get(
                "email"
            ),

            foto_url=usuario_google.get(
                "picture"
            )
        )

    except Exception as erro:

        print(
            "Erro no login Google:",
            repr(erro)
        )

        flash(
            "Não foi possível realizar o login com Google.",
            "danger"
        )

        return redirect(
            url_for("auth.login")
        )

# =========================================================
# IMPORTAR FOTO DE PERFIL DO GOOGLE
# =========================================================

def _importar_foto_google(
    usuario,
    foto_url
):
    print("=== TESTE FOTO GOOGLE ===")
    print("Usuário:", usuario.id)
    print("URL recebida:", foto_url)
    print("Foto atual:", usuario.foto_perfil)

    if not foto_url:
        print("ERRO: Google não enviou picture")
        return False
    
    # Não sobrescreve foto escolhida pelo usuário
    if usuario.foto_perfil:
         return False

    try:

        resposta = requests.get(
            foto_url,
            timeout=10
        )

        if not resposta.ok:

            print(
                "Google foto HTTP:",
                resposta.status_code
            )

            return False

        sucesso = _salvar_foto_oauth(
            usuario,
            resposta.content,
            nome_arquivo="google_perfil.jpg",
            content_type=(
                resposta.headers.get(
                    "Content-Type",
                    "image/jpeg"
                )
            )
        )

        if sucesso:

            db.session.commit()

            print(
                "Foto Google importada com sucesso."
            )

            return True

    except Exception as erro:

        db.session.rollback()

        print(
            "Erro ao importar foto Google:",
            repr(erro)
        )

    return False

# =========================================================
# LOGIN MICROSOFT
# =========================================================

@auth_bp.route("/login/microsoft")
def login_microsoft():

    if current_user.is_authenticated:

        return redirect(
            url_for("auth.painel")
        )

    redirect_uri = url_for(
        "auth.microsoft_callback",
        _external=True
    )

    return oauth.microsoft.authorize_redirect(
        redirect_uri
    )
    
# =========================================================
# CALLBACK MICROSOFT
# =========================================================

@auth_bp.route("/login/microsoft/callback")
def microsoft_callback():

    try:

        token = (
            oauth.microsoft.authorize_access_token()
        )

        usuario_microsoft = token.get(
            "userinfo"
        )

        if not usuario_microsoft:

            usuario_microsoft = (
                oauth.microsoft.userinfo(
                    token=token
                )
            )

        email = (
            usuario_microsoft.get("email")
            or usuario_microsoft.get(
                "preferred_username"
            )
        )

        access_token = token.get(
            "access_token"
        )

        return _processar_login_oauth(
            provedor="microsoft",

            provedor_usuario_id=usuario_microsoft.get(
                "sub"
            ),

            nome=usuario_microsoft.get(
                "name"
            ),

            email=email,

            token=access_token
        )

    except Exception as erro:

        print(
            "Erro no login Microsoft:",
            repr(erro)
        )

        flash(
            "Não foi possível realizar o login com Microsoft.",
            "danger"
        )

        return redirect(
            url_for("auth.login")
        )
        
        
# =========================================================
# IMPORTAR FOTO DE PERFIL MICROSOFT
# =========================================================

def _importar_foto_microsoft(
    usuario,
    access_token
):

    if not access_token:
        return False

    # Não sobrescreve foto escolhida manualmente
    if usuario.foto_perfil:
        return False

    try:

        resposta = requests.get(
            "https://graph.microsoft.com/v1.0/me/photo/$value",

            headers={
                "Authorization": (
                    f"Bearer {access_token}"
                )
            },

            timeout=10
        )

        if resposta.status_code == 404:

            print(
                "Conta Microsoft sem foto de perfil."
            )

            return False

        if not resposta.ok:

            print(
                "Erro Microsoft foto HTTP:",
                resposta.status_code,
                resposta.text
            )

            return False

        sucesso = _salvar_foto_oauth(
            usuario,
            resposta.content,
            nome_arquivo="microsoft_perfil.jpg",
            content_type=(
                resposta.headers.get(
                    "Content-Type",
                    "image/jpeg"
                )
            )
        )

        if sucesso:

            db.session.commit()

            print(
                "Foto Microsoft importada com sucesso."
            )

            return True

    except Exception as erro:

        db.session.rollback()

        print(
            "Erro ao importar foto Microsoft:",
            repr(erro)
        )

    return False

# =========================================================
# COMPLETAR CADASTRO OAUTH
# =========================================================

@auth_bp.route(
    "/cadastro/oauth/completar",
    methods=["GET", "POST"]
)
def completar_cadastro_oauth():

    dados_oauth = session.get(
        "oauth_cadastro"
    )

    if not dados_oauth:

        flash(
            "Sessão de cadastro social expirada.",
            "warning"
        )

        return redirect(
            url_for("auth.login")
        )

    if request.method == "POST":

        # ================================================
        # DADOS DO FORMULÁRIO
        # ================================================

        cpf = request.form.get(
            "cpf",
            ""
        ).strip()

        telefone = request.form.get(
            "telefone",
            ""
        ).strip()

        cpf_numeros = re.sub(
            r"\D",
            "",
            cpf
        )

        telefone_numeros = re.sub(
            r"\D",
            "",
            telefone
        )

        # ================================================
        # VALIDAÇÃO DO TELEFONE
        # ================================================

        if telefone and not telefone_valido(
            telefone
        ):

            flash(
                "Informe um telefone válido com DDD.",
                "warning"
            )

            return redirect(
                url_for(
                    "auth.completar_cadastro_oauth"
                )
            )

        # ================================================
        # CPF OBRIGATÓRIO
        # ================================================

        if not cpf_numeros:

            flash(
                "Informe o CPF.",
                "danger"
            )

            return redirect(
                url_for(
                    "auth.completar_cadastro_oauth"
                )
            )

        # ================================================
        # TAMANHO DO CPF
        # ================================================

        if len(cpf_numeros) != 11:

            flash(
                "O CPF deve possuir 11 números.",
                "warning"
            )

            return redirect(
                url_for(
                    "auth.completar_cadastro_oauth"
                )
            )

        # ================================================
        # CPF VÁLIDO
        # ================================================

        if not cpf_valido(
            cpf_numeros
        ):

            flash(
                "Informe um CPF válido.",
                "warning"
            )

            return redirect(
                url_for(
                    "auth.completar_cadastro_oauth"
                )
            )

        # ================================================
        # CPF DUPLICADO
        # ================================================

        cpf_existente = Usuario.query.filter_by(
            cpf=cpf_numeros
        ).first()

        if cpf_existente:

            flash(
                "Este CPF já está cadastrado em outra conta.",
                "warning"
            )

            return redirect(
                url_for(
                    "auth.completar_cadastro_oauth"
                )
            )

        # ================================================
        # E-MAIL DUPLICADO
        # ================================================

        usuario_existente = Usuario.query.filter_by(
            email=dados_oauth["email"]
        ).first()

        if usuario_existente:

            session.pop(
                "oauth_cadastro",
                None
            )

            flash(
                "Este e-mail já possui uma conta no AgendaPet.",
                "warning"
            )

            return redirect(
                url_for("auth.login")
            )

        # ================================================
        # CRIA SENHA INTERNA ALEATÓRIA
        # ================================================

        senha_interna = secrets.token_urlsafe(
            48
        )

        # ================================================
        # CRIA USUÁRIO
        # ================================================

        usuario = Usuario(
            nome=dados_oauth["nome"],
            email=dados_oauth["email"],
            cpf=cpf_numeros,

            # Telefone NÃO é único.
            telefone=telefone_numeros or None,

            senha_hash=generate_password_hash(
                senha_interna
            ),

            tipo_usuario="CLIENTE",
            ativo=True
        )

        try:

            db.session.add(
                usuario
            )

            # Precisamos do ID antes de criar ContaOAuth
            db.session.flush()

            # ============================================
            # CRIA VÍNCULO OAUTH
            # ============================================

            conta_oauth = ContaOAuth(
                usuario_id=usuario.id,

                provedor=dados_oauth[
                    "provedor"
                ],

                provedor_usuario_id=dados_oauth[
                    "provedor_usuario_id"
                ],

                email_provedor=dados_oauth[
                    "email"
                ]
            )

            db.session.add(
                conta_oauth
            )

            # ============================================
            # SALVA USUÁRIO + OAUTH
            # ============================================

            db.session.commit()

            if (
                dados_oauth["provedor"] == "google"
                and dados_oauth.get("foto_url")
            ):

                _importar_foto_google(
                    usuario,
                    dados_oauth.get("foto_url")
                )
                
        except Exception as erro:

            db.session.rollback()

            print(
                "Erro no cadastro OAuth:",
                repr(erro)
            )

            flash(
                "Não foi possível concluir o cadastro.",
                "danger"
            )

            return redirect(
                url_for(
                    "auth.completar_cadastro_oauth"
                )
            )

        # ================================================
        # REMOVE DADOS TEMPORÁRIOS DA SESSÃO
        # ================================================

        session.pop(
            "oauth_cadastro",
            None
        )

        # ================================================
        # LOGIN AUTOMÁTICO
        # ================================================

        login_user(
            usuario,
            remember=True
        )

        flash(
            "Cadastro realizado com sucesso!",
            "success"
        )

        return redirect(
            url_for(
                "auth.painel"
            )
        )

    return render_template(
        "completar_cadastro_oauth.html",
        dados_oauth=dados_oauth
    )

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    
    if current_user.is_authenticated:

        return redirect(
            url_for("auth.painel")
        )
    
    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        senha = request.form.get(
            "senha",
            ""
        )

        remember = (
            request.form.get("remember") == "1"
        )

        usuario = Usuario.query.filter_by(
            email=email
        ).first()

        if (
            usuario
            and check_password_hash(
                usuario.senha_hash,
                senha
            )
        ):

            login_user(
                usuario,
                remember=remember
            )

            flash(
                "Login realizado com sucesso!",
                "success"
            )

            return redirect(
                url_for("auth.painel")
            )

        flash(
            "E-mail ou senha inválidos.",
            "danger"
        )

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "login.html"
    )

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

        if telefone and not telefone_valido(telefone):

            flash(
                "Informe um telefone válido com DDD.",
                "warning"
            )

            return render_template(
                "cadastro.html",
                dados=dados_formulario
            )
        
        
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