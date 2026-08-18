from app import db

from app.models.arquivo import Arquivo
from app.services.imagem import processar_imagem
from app.services.storage_service import StorageService


class UploadService:

    @staticmethod
    def criar_arquivo(
        file_storage,
        pasta="geral"
    ) -> Arquivo:

        resultado = processar_imagem(
            file_storage
        )

        caminho = None
        caminho_miniatura = None

        try:

            # =====================================================
            # SALVAR IMAGEM PRINCIPAL
            # =====================================================

            caminho = StorageService.salvar(
                dados=resultado.dados,
                pasta=pasta,
                extensao=resultado.extensao
            )

            # =====================================================
            # SALVAR MINIATURA
            # =====================================================

            if resultado.miniatura:

                caminho_miniatura = StorageService.salvar(
                    dados=resultado.miniatura,
                    pasta=f"{pasta}/miniaturas",
                    extensao=resultado.extensao
                )

            # =====================================================
            # REGISTRAR METADADOS NO BANCO
            # =====================================================

            arquivo = Arquivo(

                nome_original=resultado.nome_original,

                tipo_mime=resultado.tipo_mime,

                extensao=resultado.extensao,

                # Novos arquivos não ficam armazenados
                # diretamente no PostgreSQL.
                dados=None,
                miniatura=None,

                caminho=caminho,

                caminho_miniatura=caminho_miniatura,

                tamanho_bytes=resultado.tamanho_bytes,

                tamanho_miniatura_bytes=(
                    resultado.tamanho_miniatura_bytes
                ),

                largura=resultado.largura,

                altura=resultado.altura,

                largura_miniatura=(
                    resultado.largura_miniatura
                ),

                altura_miniatura=(
                    resultado.altura_miniatura
                ),

                hash_sha256=resultado.hash_sha256,

                qualidade=resultado.qualidade,

                modelo_compactacao=(
                    resultado.modelo_compactacao
                ),

                versao_processador=(
                    resultado.versao_processador
                ),

                orientacao_corrigida=(
                    resultado.orientacao_corrigida
                )

            )

            db.session.add(arquivo)

            db.session.flush()

            return arquivo

        except Exception:

            # Se ocorrer algum erro depois de salvar o
            # arquivo físico, remove o arquivo para não
            # deixar conteúdo órfão no storage.

            if caminho:
                StorageService.excluir(
                    caminho
                )

            if caminho_miniatura:
                StorageService.excluir(
                    caminho_miniatura
                )

            raise