from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from app.services.auth.auth_repositories import update_user_data
from app.services.auth.user_token import get_current_user
from app.services.auth.auth_services import (
    create_user_service,
    login_user_service,
    update_user_service,
    delete_user_service,
)
from app.services.utils import add_image_to_storage
from app.schemas.auth.create_user import CreateUserRequest

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/create_user", status_code=status.HTTP_201_CREATED)
async def create_user(request: CreateUserRequest):
    """
    Cria um novo usuário no sistema.

    Endpoint:
        POST /auth/create_user

    Args:
        request (CreateUserRequest): Dados do usuário a serem criados (Pydantic).

    Raises:
        HTTPException 409: Se o usuário já existir.
        HTTPException 500: Em caso de erro interno do servidor.

    Returns:
        dict: Mensagem de sucesso.
    """
    try:
        return create_user_service(request.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(request: OAuth2PasswordRequestForm = Depends()):
    """
    Autentica um usuário e retorna um token JWT junto com os dados do usuário.

    Endpoint:
        POST /auth/login

    Args:
        request (OAuth2PasswordRequestForm): Contém 'username' (email) e 'password'.

    Raises:
        HTTPException 401: Se credenciais forem inválidas.
        HTTPException 500: Em caso de erro interno do servidor.

    Returns:
        dict: Contendo 'access_token', 'token_type' e 'user'.
    """
    try:
        return login_user_service(request.username, request.password)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/current_user", status_code=status.HTTP_200_OK)
async def get_current(user_doc: dict = Depends(get_current_user)):
    """
    Retorna os dados do usuário atualmente autenticado.

    Endpoint:
        GET /auth/current_user

    Args:
        user_doc (dict, optional): Dados do usuário fornecidos pelo dependency get_current_user.

    Returns:
        dict: Dados do usuário autenticado.
    """
    return user_doc


@router.put("/update", status_code=status.HTTP_200_OK)
async def update_user(
    updated_data: CreateUserRequest, user_doc: dict = Depends(get_current_user)
):
    """
    Atualiza os dados do usuário atualmente autenticado.

    Endpoint:
        PUT /auth/update

    Args:
        updated_data (CreateUserRequest): Novos dados do usuário (Pydantic).
        user_doc (dict): Dados do usuário autenticado fornecidos pelo dependency get_current_user.

    Raises:
        HTTPException 500: Em caso de erro interno do servidor.

    Returns:
        dict: Mensagem de sucesso.
    """
    try:
        return update_user_service(user_doc, updated_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/change-user-image/")
async def change_user_image(
    file: UploadFile = File(), user_doc: dict = Depends(get_current_user)
):
    MAX_BYTES = 10 * 1024 * 1024
    ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp", "image/gif"}

    if file.content_type not in ALLOWED_MIME:
        raise HTTPException(
            status_code=415, detail=f"Tipo não suportado: {file.content_type}"
        )

    data = await file.read()

    if len(data) == 0:
        raise HTTPException(status_code=400, detail="Arquivo vazio.")
    if len(data) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=413, detail=f"Arquivo excede {MAX_BYTES // (1024*1024)} MB."
        )

    image: dict = add_image_to_storage(file, data, "users")

    update_user_data(user_doc["id"], {"image_url": image["url"]})

    return JSONResponse(image, 200)


@router.delete("/delete", status_code=status.HTTP_200_OK)
async def delete_user(user_doc: dict = Depends(get_current_user)):
    """
    Deleta o usuário atualmente autenticado.

    Endpoint:
        DELETE /auth/delete

    Args:
        user_doc (dict): Dados do usuário autenticado fornecidos pelo dependency get_current_user.

    Raises:
        HTTPException 404: Se o usuário não for encontrado.
        HTTPException 500: Em caso de erro interno do servidor.

    Returns:
        dict: Mensagem de sucesso.
    """
    try:
        return delete_user_service(user_doc)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
