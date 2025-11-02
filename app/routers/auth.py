from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from app.services.auth.user_token import get_current_user
from app.services.auth.auth_services import (
    get_user,
    get_all_users,
    create_user_service,
    login_user_service,
    update_user_service,
    delete_user_service,
)
from app.services.utils import handle_image_update
from app.schemas.auth.create_user import CreateUserRequest
from logger import logger

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


@router.put(
    "/change-user-image/",
    status_code=status.HTTP_200_OK,
)
async def change_user_image(
    file: UploadFile = File(),
    user_doc: dict = Depends(get_current_user),
):
    """
    Atualiza a imagem do perfil do usuário autenticado.

    Args:
        file (UploadFile): Arquivo de imagem a ser enviado.
        user_doc (dict): Documento do usuário autenticado.

    Returns:
        JSONResponse: Dados da imagem atualizada.

    Raises:
        HTTPException: 400 em caso de erro de validação ou 500 em erro interno do servidor.
    """
    try:
        image = await handle_image_update(file, "user", user_doc)
        return JSONResponse(image, 200)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno do servidor") from e


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


@router.get("/list-users")
def list_users(user_doc: dict = Depends(get_current_user)):
    """Lista todos os usuarios caso o usuario seja gestor ou mestre

    Args:
        user_doc (dict, optional): valida token. Defaults to Depends(get_current_user).

    Raises:
        HTTPException: status 401 pois caso seja um funcionario, Unauthorized

    Returns:
        List[Dict]: Lista de json de usuários 
    """

    if user_doc["nivel"] == "gestor" or user_doc["nivel"] == "mestre":
        return get_all_users()
    
    else:
        raise HTTPException(401,"Usuário não possui acesso a esse recurso")
    

@router.get("/get-user/{email}")
def get_user_by_email(email: str, user_doc: dict = Depends(get_current_user)):
    """retorna um usuario caso o usuario seja gestor ou mestre

    Args:
        email (str): email do usuario procurado.
        user_doc (dict, optional): valida token. Defaults to Depends(get_current_user).

    Raises:
        HTTPException: status 401 pois caso seja um funcionario, Unauthorized

    Returns:
        Dict: retorna um usuario
    """

    if user_doc["nivel"] == "gestor" or user_doc["nivel"] == "mestre":
        return get_user(email)
    
    else:
        raise HTTPException(401,"Usuário não possui acesso a esse recurso")