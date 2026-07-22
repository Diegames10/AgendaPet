from app import db

from app.models.arquivo import Arquivo
from app.services.imagem import processar_imagem


class UploadService:

    @staticmethod
    def criar_arquivo(file_storage) -> Arquivo:

        resultado = processar_imagem(file_storage)

        arquivo = Arquivo(

            nome_original=resultado.nome_original,

            tipo_mime=resultado.tipo_mime,

            extensao=resultado.extensao,

            dados=resultado.dados,

            miniatura=resultado.miniatura,

            tamanho_bytes=resultado.tamanho_bytes,

            tamanho_miniatura_bytes=resultado.tamanho_miniatura_bytes,

            largura=resultado.largura,

            altura=resultado.altura,

            largura_miniatura=resultado.largura_miniatura,

            altura_miniatura=resultado.altura_miniatura,

            hash_sha256=resultado.hash_sha256,

            qualidade=resultado.qualidade,

            modelo_compactacao=resultado.modelo_compactacao,

            versao_processador=resultado.versao_processador,

            orientacao_corrigida=resultado.orientacao_corrigida

        )

        db.session.add(arquivo)

        db.session.flush()

        return arquivo