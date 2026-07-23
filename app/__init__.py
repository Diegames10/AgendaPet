from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message = "Faça login para acessar esta página."
    login_manager.login_message_category = "aviso"

    from app.models import Usuario

    from app.routes.agendamentoConsulta import agendamento_consulta_bp
    
    from app.models.exame import Exame
    
    @login_manager.user_loader
    def carregar_usuario(usuario_id):
        try:
            return db.session.get(Usuario, int(usuario_id))
        except (TypeError, ValueError):
            return None

    from app.routes import registrar_rotas
    registrar_rotas(app)

    return app