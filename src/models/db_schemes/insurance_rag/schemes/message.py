from .insurance_rag_base import SQLAlchemyBase
from sqlalchemy import Column, Integer, DateTime, func, String, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy import Index



class Message(SQLAlchemyBase):
    __tablename__ = "messages"

    message_id = Column(Integer, primary_key=True, autoincrement=True)
    message_uuid = Column(UUID(as_uuid=True), default=uuid.uuid4,  unique=True, nullable=False)

    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    message_conversation_id = Column(Integer, ForeignKey("conversations.conversation_id"), nullable=False)

    conversation = relationship(
        "Conversation",
        back_populates="messages"
    )


    __table_args__ = (
            Index("ix_message_conversation_id", message_conversation_id),
        )
