from PIL import Image

from .excecoes import (
    FormatoNaoPermitidoError,
    ImagemInvalidaError,
    ArquivoMuitoGrandeError
)

FORMATOS_PERMITIDOS = {
    "JPEG",
    "JPG",
    "PNG",
    "WEBP"
}

TAMANHO_MAXIMO_MB = 15


def validar_imagem(file_storage):
    """
    Valida a imagem enviada.
    """

    if file_storage is None:
        raise ImagemInvalidaError(
            "Nenhuma imagem enviada."
        )

    dados = file_storage.read()

    tamanho = len(dados)

    if tamanho > TAMANHO_MAXIMO_MB * 1024 * 1024:
        raise ArquivoMuitoGrandeError(
            f"Imagem acima de {TAMANHO_MAXIMO_MB} MB."
        )

    file_storage.seek(0)

    try:
        imagem = Image.open(file_storage)

        formato = (
            imagem.format or ""
        ).upper()

        if formato not in FORMATOS_PERMITIDOS:
            raise FormatoNaoPermitidoError(
                f"Formato '{formato or 'desconhecido'}' "
                "não permitido."
            )

        imagem.verify()

    except FormatoNaoPermitidoError:
        raise

    except Exception as erro:
        raise ImagemInvalidaError(
            "O arquivo enviado não é uma imagem válida "
            "ou está corrompido."
        ) from erro

    finally:
        file_storage.seek(0)

    return True