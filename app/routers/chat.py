from typing import List, Optional
from fastapi import APIRouter, Depends, status, HTTPException, Query
from app.schemas.chat import ChatResponse
from app.services.auth.user_token import get_current_user
from app.services.chat.chat_service import ChatService


router = APIRouter(prefix='/chat', tags=['Chat'])
chat_service = ChatService()


@router.post("/", response_model=ChatResponse, status_code=201)
def create_chat(activity_id, user_doc: dict = Depends(get_current_user)):
    """
    Cria um novo chat
    """
    return chat_service.create_chat(activity_id, user_doc['cpf'])


@router.get("/{chat_id}", response_model=ChatResponse)
def get_chat(chat_id: str, user_doc: dict = Depends(get_current_user)):
    """
    Busca um chat específico por ID
    """
    return chat_service.get_chat(chat_id)


@router.get("/", response_model=List[ChatResponse])
def get_chats(user_doc: dict = Depends(get_current_user)):
    """
    Lista todos os chats ou filtra por ID de atividade
    """

    return chat_service.get_all_chats()


@router.delete("/{chat_id}")
def delete_chat(chat_id: str, user_doc: dict = Depends(get_current_user)):
    """
    Deleta um chat específico
    """
    return chat_service.delete_chat(chat_id, user_doc['cpf'])