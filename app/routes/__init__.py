from app.routes.auth import auth_bp
from app.routes.pets import pets_bp
from app.routes.agendamentoConsulta import agendamento_consulta_bp
from app.routes.veterinario import veterinarios_bp
from app.routes.historico import historico_bp
from app.routes.imagens import imagens_bp
from app.routes.exames import exames_bp


def registrar_rotas(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(pets_bp)
    app.register_blueprint(agendamento_consulta_bp)
    app.register_blueprint(veterinarios_bp)
    app.register_blueprint(historico_bp)
    app.register_blueprint(imagens_bp)
    app.register_blueprint(exames_bp)