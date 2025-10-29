from datetime import datetime
from typing import List
from fastapi import HTTPException
from google.cloud import exceptions
from firebase_admin import firestore

from app.schemas.chat import ChatResponse
from app.db.firebase import firestore_db



class ChatService:
    def __init__(self):
        self.collection = firestore_db.collection("chats")

    def create_chat(self, activity_id: int, owner: str) -> ChatResponse:
        """Cria um novo chat no Firestore"""
        try:
            existing_chats = self.collection.where(
                "id_atividade", "==", activity_id
            ).get()

            # Verifica se a lista NÃO está vazia (tem documentos)
            if len(existing_chats) > 0:
                raise KeyError("Chat já existe para esta atividade")

            # Prepara os dados para inserção
            chat_dict = {
                "id_atividade": activity_id,
                "criador": owner,
                "created_at": datetime.now(),
            }

            # Adiciona o documento e obtém a referência
            doc_ref = self.collection.add(chat_dict)
            chat_id = doc_ref[1].id

            # Retorna o chat criado
            return ChatResponse(
                id=chat_id,
                id_atividade=activity_id,
                criador=owner,
                created_at=chat_dict["created_at"],
            )

        except KeyError as e:
            raise HTTPException(
                status_code=409, detail="Chat já criado para essa atividade"
            ) from e

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Erro ao criar chat: {str(e)}"
            ) from e

    def get_chat(self, chat_id: str) -> ChatResponse:
        """Busca um chat específico por ID"""
        try:
            doc = self.collection.document(chat_id).get()

            if not doc.exists:
                raise HTTPException(status_code=404, detail="Chat não encontrado")

            data = doc.to_dict()
            return ChatResponse(
                id=doc.id,
                id_atividade=data["id_atividade"],
                criador=data["criador"],
                created_at=data["created_at"],
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Erro ao buscar chat: {str(e)}"
            )

    def get_all_chats(self) -> List[ChatResponse]:
        """Lista todos os chats"""
        try:
            docs = self.collection.stream()
            chats = []

            for doc in docs:
                data = doc.to_dict()
                chats.append(
                    ChatResponse(
                        id=doc.id,
                        id_atividade=data["id_atividade"],
                        criador=data["criador"],
                        created_at=data["created_at"],
                    )
                )

            return chats
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Erro ao listar chats: {str(e)}"
            )

    def get_chats_by_activities(self, id_atividade: str) -> List[ChatResponse]:
        """Lista chats por ID de atividade"""
        try:
            docs = self.collection.where("id_atividade", "==", id_atividade).stream()
            chats = []

            for doc in docs:
                data = doc.to_dict()
                chats.append(
                    ChatResponse(
                        id=doc.id,
                        id_atividade=data["id_atividade"],
                        criador=data["criador"],
                        created_at=data["created_at"],
                    )
                )

            return chats
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Erro ao buscar chats por atividade: {str(e)}"
            )
        
    def check_chat(self, activity_id):
        existing_chats = self.collection.where(
                "id_atividade", "==", activity_id
            ).get()

        if len(existing_chats) == 1:
            return True
        else:
            return False

    def delete_chat(self, chat_id: str, owner) -> dict:
        """Deleta um chat específico"""
        try:
            doc_ref = self.collection.document(chat_id)
            doc = doc_ref.get()

            if not doc.exists:
                raise HTTPException(status_code=404, detail="Chat não encontrado")

            elif doc.to_dict()["criador"] != owner:
                raise HTTPException(
                    status_code=404, detail="Usuário não pode excluir esse chat"
                )

            doc_ref.delete()
            return {"message": "Chat deletado com sucesso", "id": chat_id}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Erro ao deletar chat: {str(e)}"
            )


    def new_message(self, chat_id: str, user: dict, conteudo: str):

        data = {
            "id_autor": user["id"],
            "nome_autor": user["nome"],
            "imagem_autor": user["image_url"],
            "conteudo": conteudo,
            "enviado_em": datetime.now(),
            "editado": False,
            "apagado": False
        }

        try:
            chat_ref = self.collection.document(chat_id)
            mensagem_ref = chat_ref.collection("mensagens").document()
            
            mensagem_ref.set(data)

            return data

        except exceptions.GoogleCloudError as e:
            raise exceptions.GoogleCloudError("Erro ao enviar mensagem") from e
        
    def list_messages(self, chat_id: str, limit: int = 50):
        """
        Retorna as mensagens de um chat, ordenadas por data de envio (mais antigas primeiro).
        """
        try:
            chat_ref = self.collection.document(chat_id)
            mensagens_ref = chat_ref.collection("mensagens")

            # Ordena pelo campo enviado_em (ascendente = mais antigas primeiro)
            mensagens = (
                mensagens_ref.order_by("enviado_em", direction=firestore.Query.ASCENDING)
                .limit(limit)
                .stream()
            )

            result = []
            for msg in mensagens:
                data = msg.to_dict()
                data["id"] = msg.id
                result.append(data)

            return {
                "success": True,
                "chat_id": chat_id,
                "total": len(result),
                "mensagens": result
            }

        except exceptions.NotFound:
            return {"success": False, "error": "Chat não encontrado"}
        except Exception as e:
            return {"success": False, "error": str(e)}
        
    
    def update_message(self, chat_id: str, mensagem_id, user: dict, conteudo: str):

        mensagem_ref = (
            self.collection
            .document(chat_id)
            .collection("mensagens")
            .document(mensagem_id)
        )

        data: dict = mensagem_ref.get().to_dict()
        if user["id"] != data["id_autor"]:
            raise HTTPException(
                status_code=401, detail="Usuário não pode editar uma mensagem que não enviou"
            )
        
        elif data["apagado"]:
            raise HTTPException(
                status_code=409, detail="Mensagem apagada"
            )
        
        elif data["conteudo"] == conteudo:
            return data

        else:
            data.update({
                "conteudo": conteudo,
                "editado": True
            })

            mensagem_ref.set(data)
            
            return data
        
    
    def delete_message(self, chat_id: str, mensagem_id, user: dict):
        mensagem_ref = (
            self.collection
            .document(chat_id)
            .collection("mensagens")
            .document(mensagem_id)
        )

        data: dict = mensagem_ref.get().to_dict()

        if user["id"] != data["id_autor"]:
            raise HTTPException(
                status_code=401, detail="Usuário não pode apagar uma mensagem que não enviou"
            )
        
        elif data["apagado"]:
            raise HTTPException(
                status_code=409, detail="Mensagem já está apagada"
            )
        
        else:
            data.update({
                "conteudo": None,
                "editado": False,
                "apagado": True,
                "imagem_autor": None
            })