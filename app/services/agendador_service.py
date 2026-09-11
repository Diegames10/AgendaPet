from apscheduler.schedulers.background import BackgroundScheduler

from app import db
from app.services.lembrete_service import LembreteService


scheduler = BackgroundScheduler(
    timezone="America/Sao_Paulo"
)


def iniciar_agendador(app):
 
    def verificar_lembretes():

        with app.app_context():

            try:
                total = (
                    LembreteService
                    .verificar_lembretes_proximo_dia_util()
                )

                print(
                    f"[AGENDADOR] Lembretes enviados: {total}"
                )

            except Exception as erro:

                db.session.rollback()

                print(
                    "[AGENDADOR] Erro ao verificar lembretes:",
                    repr(erro)
                )

    scheduler.add_job(
        func=verificar_lembretes,
        trigger="cron",
        day_of_week="mon-fri",
        hour="8-17",
        minute=0,
        id="verificar_lembretes_agendamentos",
        replace_existing=True
    )

    if not scheduler.running:
        scheduler.start()

        print(
            "[AGENDADOR] Agendador iniciado."
        )