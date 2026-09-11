from datetime import datetime, timedelta

from app import db
from app.models.agendamentoConsulta import AgendamentoConsulta
from app.services.notificacao_service import NotificacaoService


class LembreteService:

    @staticmethod
    def _proximo_dia_util(data_base):
        dia = data_base + timedelta(days=1)

        # 5 = sábado
        # 6 = domingo
        while dia.weekday() in (5, 6):
            dia += timedelta(days=1)

        return dia

    @staticmethod
    def verificar_lembretes_proximo_dia_util():

        hoje = datetime.now().date()

        proximo_dia_util = (
            LembreteService._proximo_dia_util(hoje)
        )

        agendamentos = (
            AgendamentoConsulta.query
            .filter(
                AgendamentoConsulta.data == proximo_dia_util,
                AgendamentoConsulta.status.in_(
                    [
                        "Agendado",
                        "Confirmado"
                    ]
                ),
                AgendamentoConsulta.lembrete_24h_enviado_em.is_(None)
            )
            .order_by(
                AgendamentoConsulta.horario.asc()
            )
            .all()
        )

        total_enviados = 0

        for agendamento in agendamentos:

            try:
                resultado = (
                    NotificacaoService
                    .lembrete_agendamento(
                        agendamento
                    )
                )

                if resultado is not False:

                    agendamento.lembrete_24h_enviado_em = (
                        datetime.now()
                    )

                    db.session.commit()

                    total_enviados += 1

                    print(
                        "Lembrete enviado:",
                        agendamento.id
                    )

            except Exception as erro:

                db.session.rollback()

                print(
                    "Erro ao enviar lembrete:",
                    agendamento.id,
                    repr(erro)
                )

        print(
            "Próximo dia útil:",
            proximo_dia_util
        )

        print(
            "Total de lembretes enviados:",
            total_enviados
        )

        return total_enviados