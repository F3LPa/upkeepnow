import mimetypes
from pathlib import Path
from fastapi import HTTPException, UploadFile
from uuid import uuid4

from app.services.activities.activities_repositories import update_activity
from app.services.auth.auth_repositories import update_user_data
from logger import logger
from app.db.firebase import get_bucket

MAX_BYTES = 10 * 1024 * 1024
ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp", "image/gif"}


def _safe_ext_from_mime(mime: str, fallback: str = "") -> str:
    """
    Retorna uma extensão de arquivo com base no tipo MIME informado.

    Caso não seja possível deduzir a extensão a partir do MIME,
    utiliza o valor de fallback fornecido.

    Args:
        mime (str): Tipo MIME do arquivo (exemplo: "image/png").
        fallback (str, opcional): Extensão padrão a ser usada se o MIME não for reconhecido.
            Padrão é uma string vazia.

    Returns:
        str: Extensão do arquivo, incluindo o ponto (exemplo: ".png").
    """
    guessed = mimetypes.guess_extension(mime) or ""
    if guessed:
        return guessed
    return fallback


def add_image_to_storage(file: UploadFile, data: bytes, source: str) -> dict:
    """
    Envia uma imagem para o Firebase Storage e retorna os dados do objeto armazenado.

    Este método gera automaticamente um nome de arquivo único,
    define o tipo de conteúdo correto, aplica configurações de cache
    e tenta tornar o arquivo publicamente acessível.

    Args:
        file (UploadFile): Arquivo de imagem recebido via upload.
        data (bytes): Conteúdo binário da imagem.
        source (str): Origem do arquivo (ex: "users", "activities"), usada para organizar o caminho.

    Returns:
        dict: Dicionário contendo:
            - "ok" (bool): Indica se o upload foi bem-sucedido.
            - "url" (str | None): URL pública da imagem, caso tenha sido tornada pública.
            - "path" (str): Caminho completo do arquivo dentro do bucket.

    Raises:
        Exception: Caso ocorra erro durante o envio ao bucket ou na geração da URL pública.
    """
    original_ext = Path(file.filename).suffix.lower()
    ext = _safe_ext_from_mime(file.content_type, original_ext) or ".bin"

    object_path = f"{source}/images/{uuid4().hex}{ext}"

    # Envia ao Firebase Storage
    bucket = get_bucket()
    blob = bucket.blob(object_path)

    # Define cache e tipo de conteúdo
    blob.cache_control = "public, max-age=31536000, immutable"
    blob.upload_from_string(data, content_type=file.content_type)
    logger.info("Imagem salva no bucket com sucesso")

    # Torna o objeto público (opcional)
    try:
        blob.make_public()
        public_url = blob.public_url
    except Exception:
        logger.error("Erro ao adicionar imagem no bucket")
        public_url = None

    return {
        "ok": True,
        "url": public_url,
        "path": object_path,
    }


async def handle_image_update(
    file: UploadFile,
    upload_type: str,
    user_doc: dict | None = None,
    ordem_servico: str | None = None,
) -> dict:
    """
    Valida, lê e envia uma imagem ao storage e atualiza o registro correspondente.

    upload_type:
        - "user" -> atualiza imagem do usuário
        - "activity" -> atualiza imagem da atividade
    """
    if file.content_type not in ALLOWED_MIME:
        raise HTTPException(
            status_code=415, detail=f"Tipo não suportado: {file.content_type}"
        )

    data = await file.read()

    if len(data) == 0:
        raise HTTPException(status_code=400, detail="Arquivo vazio.")

    if len(data) > MAX_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Arquivo excede {MAX_BYTES // (1024 * 1024)} MB.",
        )

    # Define comportamento com base no tipo
    if upload_type == "user":
        folder = "users"
        image = add_image_to_storage(file, data, folder)
        update_user_data(user_doc["id"], {"image_url": image["url"]})
    elif upload_type == "activity":
        if not ordem_servico:
            raise HTTPException(
                status_code=400, detail="Número da ordem de serviço é obrigatório."
            )
        folder = "activities"
        image = add_image_to_storage(file, data, folder)
        update_activity(ordem_servico, {"image_url": image["url"]})
    else:
        raise HTTPException(
            status_code=400, detail=f"Tipo de upload inválido: {upload_type}"
        )

    return image
