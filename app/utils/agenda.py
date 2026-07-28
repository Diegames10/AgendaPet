from datetime import datetime, timedelta


def gerar_horarios_disponiveis(
    hora_inicio,
    hora_fim,
    inicio_almoco,
    fim_almoco,
    intervalo,
    horarios_ocupados
):

    horarios = []

    atual = datetime.combine(
        datetime.today(),
        hora_inicio
    )

    fim = datetime.combine(
        datetime.today(),
        hora_fim
    )

    almoco_inicio = (
        datetime.combine(datetime.today(), inicio_almoco)
        if inicio_almoco else None
    )

    almoco_fim = (
        datetime.combine(datetime.today(), fim_almoco)
        if fim_almoco else None
    )

    while atual < fim:

        horario = atual.time()

        ocupado = horario in horarios_ocupados

        em_almoco = (
            almoco_inicio
            and almoco_inicio.time() <= horario < almoco_fim.time()
        )

        if not ocupado and not em_almoco:

            horarios.append(horario)

        atual += timedelta(
            minutes=intervalo
        )

    return horarios