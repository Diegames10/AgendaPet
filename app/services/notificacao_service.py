from app.services.email_service import EmailService


class NotificacaoService:

    @staticmethod
    def agendamento_criado(agendamento):
        tutor = agendamento.tutor
        pet = agendamento.pet
        veterinario = agendamento.veterinario

        if not tutor or not tutor.email:
            return False

        data_formatada = agendamento.data.strftime(
            "%d/%m/%Y"
        )

        horario_formatado = agendamento.horario.strftime(
            "%H:%M"
        )

        nome_veterinario = (
            veterinario.nome
            if veterinario
            else "A definir"
        )

        html = f"""
        <div style="
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: auto;
            padding: 30px;
        ">
            <h2 style="color: #198754;">
                AgendaPet Paranaguá
            </h2>

            <p>
                Olá, <strong>{tutor.nome}</strong>.
            </p>

            <p>
                Seu agendamento foi realizado
                com sucesso.
            </p>

            <div style="
                background: #f5f5f5;
                padding: 20px;
                border-radius: 8px;
                margin: 25px 0;
            ">
                <p>
                    <strong>Pet:</strong>
                    {pet.nome}
                </p>

                <p>
                    <strong>Atendimento:</strong>
                    {agendamento.tipo}
                </p>

                <p>
                    <strong>Data:</strong>
                    {data_formatada}
                </p>

                <p>
                    <strong>Horário:</strong>
                    {horario_formatado}
                </p>

                <p>
                    <strong>Veterinário:</strong>
                    {nome_veterinario}
                </p>

                <p>
                    <strong>Status:</strong>
                    {agendamento.status}
                </p>
            </div>

            <p>
                Caso seja necessário alterar ou
                cancelar o atendimento, acesse
                o AgendaPet Paranaguá.
            </p>

            <hr>

            <small>
                AgendaPet Paranaguá<br>
                Sistema de Agendamento da SEMMA
            </small>
        </div>
        """

        return EmailService.enviar(
            destinatario_email=tutor.email,
            destinatario_nome=tutor.nome,
            assunto=(
                f"Agendamento realizado - {pet.nome}"
            ),
            html=html
        )
        
    @staticmethod
    def agendamento_alterado(agendamento):
        tutor = agendamento.tutor
        pet = agendamento.pet
        veterinario = agendamento.veterinario

        if not tutor or not tutor.email:
            return False

        data_formatada = agendamento.data.strftime(
            "%d/%m/%Y"
        )

        horario_formatado = agendamento.horario.strftime(
            "%H:%M"
        )

        nome_veterinario = (
            veterinario.nome
            if veterinario
            else "A definir"
        )

        html = f"""
        <div style="
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: auto;
            padding: 30px;
        ">
            <h2 style="color: #198754;">
                AgendaPet Paranaguá
            </h2>

            <p>
                Olá, <strong>{tutor.nome}</strong>.
            </p>

            <p>
                O agendamento do seu pet
                <strong>{pet.nome}</strong>
                foi atualizado.
            </p>

            <div style="
                background: #f5f5f5;
                padding: 20px;
                border-radius: 8px;
                margin: 25px 0;
            ">
                <p>
                    <strong>Pet:</strong>
                    {pet.nome}
                </p>

                <p>
                    <strong>Atendimento:</strong>
                    {agendamento.tipo}
                </p>

                <p>
                    <strong>Data:</strong>
                    {data_formatada}
                </p>

                <p>
                    <strong>Horário:</strong>
                    {horario_formatado}
                </p>

                <p>
                    <strong>Veterinário:</strong>
                    {nome_veterinario}
                </p>

                <p>
                    <strong>Status:</strong>
                    {agendamento.status}
                </p>
            </div>

            <p>
                Acesse o AgendaPet Paranaguá
                para acompanhar seu agendamento.
            </p>

            <hr>

            <small>
                AgendaPet Paranaguá<br>
                Sistema de Agendamento da SEMMA
            </small>
        </div>
        """

        return EmailService.enviar(
            destinatario_email=tutor.email,
            destinatario_nome=tutor.nome,
            assunto=(
                f"Agendamento atualizado - {pet.nome}"
            ),
            html=html
        )
        
    @staticmethod
    def agendamento_cancelado(agendamento):
        tutor = agendamento.tutor
        pet = agendamento.pet
        veterinario = agendamento.veterinario

        if not tutor or not tutor.email:
            return False

        data_formatada = agendamento.data.strftime(
            "%d/%m/%Y"
        )

        horario_formatado = agendamento.horario.strftime(
            "%H:%M"
        )

        nome_veterinario = (
            veterinario.nome
            if veterinario
            else "A definir"
        )

        html = f"""
        <div style="
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: auto;
            padding: 30px;
        ">
            <h2 style="color: #dc3545;">
                AgendaPet Paranaguá
            </h2>

            <p>
                Olá, <strong>{tutor.nome}</strong>.
            </p>

            <p>
                O agendamento do seu pet
                <strong>{pet.nome}</strong>
                foi cancelado.
            </p>

            <div style="
                background: #f5f5f5;
                padding: 20px;
                border-radius: 8px;
                margin: 25px 0;
            ">
                <p>
                    <strong>Pet:</strong>
                    {pet.nome}
                </p>

                <p>
                    <strong>Atendimento:</strong>
                    {agendamento.tipo}
                </p>

                <p>
                    <strong>Data:</strong>
                    {data_formatada}
                </p>

                <p>
                    <strong>Horário:</strong>
                    {horario_formatado}
                </p>

                <p>
                    <strong>Veterinário:</strong>
                    {nome_veterinario}
                </p>

                <p>
                    <strong>Status:</strong>
                    Cancelado
                </p>
            </div>

            <p>
                Caso seja necessário, você poderá realizar
                um novo agendamento pelo AgendaPet Paranaguá.
            </p>

            <hr>

            <small>
                AgendaPet Paranaguá<br>
                Sistema de Agendamento da SEMMA
            </small>
        </div>
        """

        return EmailService.enviar(
            destinatario_email=tutor.email,
            destinatario_nome=tutor.nome,
            assunto=(
                f"Agendamento cancelado - {pet.nome}"
            ),
            html=html
        )
        
    @staticmethod
    def lembrete_agendamento(agendamento):
        tutor = agendamento.tutor
        pet = agendamento.pet
        veterinario = agendamento.veterinario

        if not tutor or not tutor.email:
            return False

        data_formatada = agendamento.data.strftime(
            "%d/%m/%Y"
        )

        horario_formatado = agendamento.horario.strftime(
            "%H:%M"
        )

        nome_veterinario = (
            veterinario.nome
            if veterinario
            else "A definir"
        )

        html = f"""
        <div style="
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: auto;
            padding: 30px;
        ">
            <h2 style="color: #198754;">
                AgendaPet Paranaguá
            </h2>

            <p>
                Olá, <strong>{tutor.nome}</strong>.
            </p>

            <p>
                Este é um lembrete de que o atendimento do seu pet
                <strong>{pet.nome}</strong>
                está agendado para o próximo dia útil.
            </p>

            <div style="
                background: #f5f5f5;
                padding: 20px;
                border-radius: 8px;
                margin: 25px 0;
            ">
                <p>
                    <strong>Pet:</strong>
                    {pet.nome}
                </p>

                <p>
                    <strong>Atendimento:</strong>
                    {agendamento.tipo}
                </p>

                <p>
                    <strong>Data:</strong>
                    {data_formatada}
                </p>

                <p>
                    <strong>Horário:</strong>
                    {horario_formatado}
                </p>

                <p>
                    <strong>Veterinário:</strong>
                    {nome_veterinario}
                </p>

                <p>
                    <strong>Status:</strong>
                    {agendamento.status}
                </p>
            </div>

            <p>
                Caso não possa comparecer, acesse o AgendaPet Paranaguá
                para verificar seu agendamento.
            </p>

            <hr>

            <small>
                AgendaPet Paranaguá<br>
                Sistema de Agendamento da SEMMA
            </small>
        </div>
        """

        return EmailService.enviar(
            destinatario_email=tutor.email,
            destinatario_nome=tutor.nome,
            assunto=(
                f"Lembrete de agendamento - {pet.nome}"
            ),
            html=html
        )        