import requests

from flask import current_app


class EmailService:

    URL = "https://api.brevo.com/v3/smtp/email"

    @staticmethod
    def enviar(
        destinatario_email,
        destinatario_nome,
        assunto,
        html
    ):

        api_key = current_app.config.get(
            "BREVO_API_KEY"
        )

        remetente_email = current_app.config.get(
            "BREVO_SENDER_EMAIL"
        )

        remetente_nome = current_app.config.get(
            "BREVO_SENDER_NAME"
        )

        if not api_key:
            raise RuntimeError(
                "BREVO_API_KEY não configurada."
            )

        if not remetente_email:
            raise RuntimeError(
                "BREVO_SENDER_EMAIL não configurado."
            )

        payload = {
            "sender": {
                "name": remetente_nome,
                "email": remetente_email
            },

            "to": [
                {
                    "email": destinatario_email,
                    "name": destinatario_nome
                }
            ],

            "subject": assunto,

            "htmlContent": html
        }

        headers = {
            "accept": "application/json",
            "api-key": api_key,
            "content-type": "application/json"
        }

        resposta = requests.post(
            EmailService.URL,
            json=payload,
            headers=headers,
            timeout=15
        )

        if resposta.status_code not in (
            200,
            201,
            202
        ):

            raise RuntimeError(
                f"Erro Brevo "
                f"{resposta.status_code}: "
                f"{resposta.text}"
            )

        return resposta.json()