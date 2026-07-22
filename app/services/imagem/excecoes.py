class ImagemInvalidaError(Exception):
    """Imagem inválida."""
    pass


class FormatoNaoPermitidoError(Exception):
    """Formato não permitido."""
    pass


class ArquivoMuitoGrandeError(Exception):
    """Arquivo acima do limite permitido."""
    pass


class CompressaoError(Exception):
    """Erro durante a compressão."""
    pass