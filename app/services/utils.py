import mimetypes
from pathlib import Path
from fastapi import UploadFile
from uuid import uuid4

from logger import logger
from app.db.firebase import get_bucket


def _safe_ext_from_mime(mime: str, fallback: str = "") -> str:
    # tenta deduzir a extensão pela mime; se não conseguir, usa a do filename recebido
    guessed = mimetypes.guess_extension(mime) or ""
    if guessed:
        return guessed
    return fallback


def add_image_to_storage(file: UploadFile, data: bytes, source: str):
    original_ext = Path(file.filename).suffix.lower()
    ext = _safe_ext_from_mime(file.content_type, original_ext) or ".bin"

    object_path = f"{source}/images/{uuid4().hex}{ext}"

    # 4) envia ao Firebase Storage
    bucket = get_bucket()
    blob = bucket.blob(object_path)

    # boas práticas de cache para conteúdo imutável (opcional)
    blob.cache_control = "public, max-age=31536000, immutable"

    # content_type garante renderização correta no browser
    blob.upload_from_string(data, content_type=file.content_type)
    logger.info("Imagem salva no bucket com sucesso")

    # 5) opções de acesso:
    #   A) tornar público (simples, mas o objeto fica world-readable):
    try:
        blob.make_public()
        public_url = blob.public_url
    except Exception:
        logger.error("Erro ao adicionar imagem no bucket")
        public_url = (
            None  # se preferir não tornar público, ignore o erro ou pule esse trecho
        )

    return {
        "ok": True,
        "url": public_url,
        "path": object_path,
    }  # acesso temporário seguro
