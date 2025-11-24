from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List

from app.services.auth.user_token import get_current_user
from app.services.chat.chat_service import ChatService

router = APIRouter()

connections: Dict[str, List[WebSocket]] = {}
chat_service = ChatService()


async def connect_socket(chat_id: str, websocket: WebSocket):
    await websocket.accept()

    if chat_id not in connections:
        connections[chat_id] = []

    connections[chat_id].append(websocket)


async def disconnect_socket(chat_id: str, websocket: WebSocket):
    connections[chat_id].remove(websocket)

    if not connections[chat_id]:
        del connections[chat_id]


async def broadcast(chat_id: str, message: dict):
    """Envia mensagem para todos os usuários conectados no chat"""
    if chat_id in connections:
        for ws in connections[chat_id]:
            await ws.send_json(message)


@router.websocket("/ws/chat/{chat_id}")
async def chat_websocket(websocket: WebSocket, chat_id: str):
    token = websocket.query_params.get("token")
    user_doc = get_current_user(token)

    await connect_socket(chat_id, websocket)

    try:
        while True:
            data = await websocket.receive_json()

            # Verifica o tipo de evento
            event_type = data.get("type", "new_message")

            if event_type == "new_message":
                # CORRIGIDO: Não recebe de novo, usa o data que já foi recebido
                conteudo = data.get("conteudo")

                saved_message = chat_service.new_message(chat_id, user_doc, conteudo)

                # Converte datetime para string se necessário
                if "enviado_em" in saved_message and isinstance(
                    saved_message["enviado_em"], datetime
                ):
                    saved_message["enviado_em"] = saved_message[
                        "enviado_em"
                    ].isoformat()

                # ADICIONA o ID da mensagem que foi criada no Firestore
                # O Firestore gera um ID automaticamente, precisamos capturá-lo
                # Vamos modificar o new_message para retornar o ID também

                # Adiciona o tipo ao evento
                saved_message["type"] = "new_message"

                await broadcast(chat_id, saved_message)

            elif event_type == "edit_message":
                # Editar mensagem
                message_id = data.get("id")
                new_content = data.get("conteudo")

                try:
                    # Atualiza no banco
                    chat_service.update_message(
                        chat_id, message_id, user_doc, new_content
                    )

                    # Faz broadcast da edição
                    edit_event = {
                        "type": "edit_message",
                        "id": message_id,
                        "conteudo": new_content,
                    }
                    await broadcast(chat_id, edit_event)
                except Exception as e:
                    # Envia erro apenas para quem tentou editar
                    await websocket.send_json(
                        {
                            "type": "error",
                            "message": f"Erro ao editar mensagem: {str(e)}",
                        }
                    )

            elif event_type == "delete_message":
                message_id = data.get("id")

                try:
                    deleted_message_data = chat_service.delete_message(
                        chat_id, message_id, user_doc
                    )

                    delete_event = {
                        "type": "delete_message",
                        "id": message_id,
                        "conteudo": deleted_message_data.get("conteudo"),
                        "apagado": deleted_message_data.get("apagado"),
                        "editado": deleted_message_data.get("editado"),
                        "imagem_autor": deleted_message_data.get("imagem_autor"),
                    }
                    await broadcast(chat_id, delete_event)
                except Exception as e:
                    await websocket.send_json(
                        {
                            "type": "error",
                            "message": f"Erro ao deletar mensagem: {str(e)}",
                        }
                    )

    except WebSocketDisconnect:
        await disconnect_socket(chat_id, websocket)
    except Exception as e:
        print(f"Erro no WebSocket: {e}")
        await disconnect_socket(chat_id, websocket)
