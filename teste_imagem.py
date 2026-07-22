from pathlib import Path

from werkzeug.datastructures import FileStorage

from app.services.imagem import processar_imagem


CAMINHO_IMAGEM = Path(
    "teste.jpg"
)


with CAMINHO_IMAGEM.open("rb") as arquivo:
    file_storage = FileStorage(
        stream=arquivo,
        filename=CAMINHO_IMAGEM.name,
        content_type="image/jpeg"
    )

    resultado = processar_imagem(
        file_storage
    )


print("Nome:", resultado.nome_original)
print("MIME:", resultado.tipo_mime)
print("Extensão:", resultado.extensao)

print(
    "Imagem:",
    resultado.largura,
    "x",
    resultado.altura
)

print(
    "Miniatura:",
    resultado.largura_miniatura,
    "x",
    resultado.altura_miniatura
)

print(
    "Tamanho da imagem:",
    round(
        resultado.tamanho_bytes / 1024,
        2
    ),
    "KB"
)

print(
    "Tamanho da miniatura:",
    round(
        resultado.tamanho_miniatura_bytes / 1024,
        2
    ),
    "KB"
)

print("Qualidade:", resultado.qualidade)
print("Hash:", resultado.hash_sha256)
print(
    "Orientação corrigida:",
    resultado.orientacao_corrigida
)


Path(
    "resultado.webp"
).write_bytes(
    resultado.dados
)

Path(
    "resultado_miniatura.webp"
).write_bytes(
    resultado.miniatura
)