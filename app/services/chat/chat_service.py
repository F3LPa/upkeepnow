from app.db.firebase import firestore_db
from app.schemas.chat import ChatResponse
from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException


class ChatService:
    def __init__(self):
        self.collection = firestore_db.collection('chats')
    
    def create_chat(self, activity_id: int, owner: str) -> ChatResponse:
        """Cria um novo chat no Firestore"""
        try:
            existing_chats = self.collection.where('id_atividade', '==', activity_id).get()
            
            # Verifica se a lista NÃO está vazia (tem documentos)
            if len(existing_chats) > 0:
                raise KeyError("Chat já existe para esta atividade")
                
            # Prepara os dados para inserção
            chat_dict = {
                'id_atividade': activity_id,
                'criador': owner,
                'created_at': datetime.now()
            }
            
            # Adiciona o documento e obtém a referência
            doc_ref = self.collection.add(chat_dict)
            chat_id = doc_ref[1].id
            
            # Retorna o chat criado
            return ChatResponse(
                id=chat_id,
                id_atividade=activity_id,
                criador=owner,
                created_at=chat_dict['created_at']
            ) 
        
        except KeyError as e:
            raise HTTPException(status_code=409, detail='Chat já criado para essa atividade') from e
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao criar chat: {str(e)}") from e
    
    def get_chat(self, chat_id: str) -> ChatResponse:
        """Busca um chat específico por ID"""
        try:
            doc = self.collection.document(chat_id).get()
            
            if not doc.exists:
                raise HTTPException(status_code=404, detail="Chat não encontrado")
            
            data = doc.to_dict()
            return ChatResponse(
                id=doc.id,
                id_atividade=data['id_atividade'],
                criador=data['criador'],
                created_at=data['created_at']
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao buscar chat: {str(e)}")
    
    def get_all_chats(self) -> List[ChatResponse]:
        """Lista todos os chats"""
        try:
            docs = self.collection.stream()
            chats = []
            
            for doc in docs:
                data = doc.to_dict()
                chats.append(ChatResponse(
                    id=doc.id,
                    id_atividade=data['id_atividade'],
                    criador=data['criador'],
                    created_at=data['created_at']
                ))
            
            return chats
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao listar chats: {str(e)}")
    
    def get_chats_by_atividade(self, id_atividade: str) -> List[ChatResponse]:
        """Lista chats por ID de atividade"""
        try:
            docs = self.collection.where('id_atividade', '==', id_atividade).stream()
            chats = []
            
            for doc in docs:
                data = doc.to_dict()
                chats.append(ChatResponse(
                    id=doc.id,
                    id_atividade=data['id_atividade'],
                    criador=data['criador'],
                    created_at=data['created_at']
                ))
            
            return chats
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao buscar chats por atividade: {str(e)}")
    
    def delete_chat(self, chat_id: str, owner) -> dict:
        """Deleta um chat específico"""
        try:
            doc_ref = self.collection.document(chat_id)
            doc = doc_ref.get()

            if not doc.exists:
                raise HTTPException(status_code=404, detail="Chat não encontrado")
            
            elif doc.to_dict()['criador'] != owner:
                raise HTTPException(status_code=404, detail="Usuário não pode excluir esse chat")
            

            doc_ref.delete()
            return {"message": "Chat deletado com sucesso", "id": chat_id}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao deletar chat: {str(e)}")