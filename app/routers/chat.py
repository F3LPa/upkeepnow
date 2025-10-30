from typing import List
from fastapi import APIRouter, Depends

from app.schemas.chat import ChatResponse, MessageRequest
from app.services.auth.user_token import get_current_user
from app.services.chat.chat_service import ChatService


router = APIRouter(prefix="/chat", tags=["Chat"])
chat_service = ChatService()


@router.post("/create-chat", response_model=ChatResponse, status_code=201)
def create_chat(activity_id, user_doc: dict = Depends(get_current_user)):
    """
    Cria um novo chat
    """
    return chat_service.create_chat(activity_id, user_doc["cpf"])


@router.get("/get-chat/{chat_id}", response_model=ChatResponse)
def get_chat(chat_id: str, user_doc: dict = Depends(get_current_user)):
    """
    Busca um chat específico por ID
    """
    return chat_service.get_chat(chat_id)


@router.get("/get-chat", response_model=List[ChatResponse])
def get_chats(user_doc: dict = Depends(get_current_user)):
    """
    Lista todos os chats ou filtra por ID de atividade
    """

    return chat_service.get_all_chats()


@router.get("/check-chat")
def check_chat(activity_id, user_doc: dict = Depends(get_current_user)):
    """Checa pra ver se existe um chat ligado a atividade e retorna True ou False

    Args:
        activity_id (int): Id da atividade checada
        user_doc (dict, optional): Informações de usuario e dependencia de token. Defaults to Depends(get_current_user).
    """

    return {"existe_chat": chat_service.check_chat(activity_id)}


@router.delete("/{chat_id}")
def delete_chat(chat_id: str, user_doc: dict = Depends(get_current_user)):
    """
    Deleta um chat específico
    """
    return chat_service.delete_chat(chat_id, user_doc["cpf"])


@router.post("/{chat_id}/send_message")
def send_message(
    chat_id: str, request: MessageRequest, user_doc: dict = Depends(get_current_user)
):
    """Envia mensagem no chat

    Args:
        chat_id (str): id do chat que vai receber a mensagem
        request (MessageRequest): corpo da mensagem
        user_doc (dict, optional): informações de usuario e validacao de token. Defaults to Depends(get_current_user).

    Returns:
        json: informaçoes da mensagem
    """

    return chat_service.new_message(chat_id, user_doc, request.text)


@router.get("/{chat_id}/get-messages")
def get_messages(chat_id: str, user_doc: dict = Depends(get_current_user)):
    """Lista mensagens

    Args:
        chat_id (str): id do chat
        user_doc (dict, optional): valida token. Defaults to Depends(get_current_user).

    Returns:
        dict: Um dicionário contendo:
            - success (bool): Indica se a operação foi bem-sucedida.
            - chat_id (str): ID do chat consultado.
            - total (int): Quantidade de mensagens retornadas.
            - mensagens (list[dict]): Lista de mensagens, onde cada item contém:
                - id (str): ID da mensagem no Firestore.
                - id_autor (str): ID do usuário autor da mensagem.
                - nome_autor (str): Nome do autor da mensagem.
                - imagem_autor (str): URL da imagem de perfil do autor.
                - conteudo (str): Texto da mensagem.
                - enviado_em (datetime): Data e hora de envio.
                - editado (bool): Indica se a mensagem foi editada.
                - apagado (bool): Indica se a mensagem foi apagada.
    """

    return chat_service.list_messages(chat_id)


@router.put("/{chat_id}/edit_message/{mensagem_id}")
def edit_message(
    chat_id: str,
    mensagem_id: str,
    request: MessageRequest,
    user_doc: dict = Depends(get_current_user),
):
    """Edita mensagem enviada no chat caso ela não esteja apagada

    Args:
        chat_id (str): id do chat
        mensagem_id (str): id da mensagem editada
        request (MessageRequest): corpo da nova mensagem
        user_doc (dict, optional): info de usuario e validacao de token. Defaults to Depends(get_current_user).

    Returns:
        dict: informacoes da mensagem editada
    """
    return chat_service.update_message(chat_id, mensagem_id, user_doc, request.text)


@router.delete("/{chat_id}/edit_message/{mensagem_id}")
def delete_message(
    chat_id: str, mensagem_id: str, user_doc: dict = Depends(get_current_user)
):
    """apaga o conteudo de uma mensagem mas mantem seu registro de envio

    Args:
        chat_id (str): id do chat
        mensagem_id (str): id da mensagem a apagar
        user_doc (dict, optional): info de usuario e validacao de token. Defaults to Depends(get_current_user).

    Returns:
        json: informacoes da mensagem
    """
    return chat_service.delete_message(chat_id, mensagem_id, user_doc)
