from .excecoes import (
    ArquivoMuitoGrandeError,
    CompressaoError,
    FormatoNaoPermitidoError,
    ImagemInvalidaError,
)

from .processador import (
    ResultadoImagem,
    processar_imagem,
)


__all__ = [
    "ArquivoMuitoGrandeError",
    "CompressaoError",
    "FormatoNaoPermitidoError",
    "ImagemInvalidaError",
    "ResultadoImagem",
    "processar_imagem",
]