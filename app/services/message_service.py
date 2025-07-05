from sqlalchemy.orm import Session
from app.models.message import Message
from app.models.connection import Connection # To check connection status
from app.schemas.message import MessageCreate
from typing import List, Optional
import uuid

class MessageService:
    def __init__(self, db: Session):
        self.db = db
        
    def get_message(self, message_id: uuid.UUID) -> Optional[Message]:
        return self.db.query(Message).filter(Message.message_id == message_id).first()

    def get_messages_by_connection(self, connection_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Message]:
        return self.db.query(Message).filter(Message.connection_id == connection_id).order_by(Message.created_at).offset(skip).limit(limit).all()

    def create_message(self, message_in: MessageCreate, sender_id: uuid.UUID) -> Message:
        # Ensure the connection exists and is in an 'ACCEPTED' state
        connection = self.db.query(Connection).filter(Connection.connection_id == message_in.connection_id).first()
        if not connection:
            raise ValueError("Connection not found.")
        
        # Ensure sender is part of the connection
        if sender_id not in [connection.requester_id, connection.recipient_id]:
            raise ValueError("Sender is not part of this connection.")
        
        # Only allow messages if connection is accepted
        if connection.status != "ACCEPTED":
            raise ValueError(f"Messages cannot be sent in a connection with status '{connection.status}'.")

        db_message = Message(
            connection_id=message_in.connection_id,
            sender_id=sender_id,
            text_content=message_in.text_content
        )
        self.db.add(db_message)
        self.db.commit()
        self.db.refresh(db_message)
        return db_message

    def mark_message_as_read(self, message_id: uuid.UUID) -> Optional[Message]:
        db_message = self.db.query(Message).filter(Message.message_id == message_id).first()
        if db_message and not db_message.is_read:
            db_message.is_read = True
            self.db.add(db_message)
            self.db.commit()
            self.db.refresh(db_message)
            return db_message
        return None