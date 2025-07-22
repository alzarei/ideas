"""
Conversation Manager for On-Device LLM Assistant
Maintains chat history and context across multiple messages
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import uuid


@dataclass
class ChatMessage:
    """Single message in a conversation"""
    id: str
    role: str  # 'system', 'user', 'assistant'
    content: str
    timestamp: datetime
    token_count: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatMessage':
        """Create from dictionary"""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


@dataclass
class Conversation:
    """A complete conversation thread"""
    id: str
    title: str
    model_id: str
    messages: List[ChatMessage]
    created_at: datetime
    updated_at: datetime
    total_tokens: int = 0
    max_tokens: int = 8192
    system_prompt: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'model_id': self.model_id,
            'messages': [msg.to_dict() for msg in self.messages],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'total_tokens': self.total_tokens,
            'max_tokens': self.max_tokens,
            'system_prompt': self.system_prompt
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Conversation':
        """Create from dictionary"""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        data['messages'] = [ChatMessage.from_dict(msg) for msg in data['messages']]
        return cls(**data)


class ConversationManager:
    """Manages multiple conversations and their state"""
    
    def __init__(self):
        self.conversations: Dict[str, Conversation] = {}
        self.default_system_prompt = """You are a helpful AI assistant running locally on the user's device. You are knowledgeable, friendly, and concise. You can help with a wide variety of tasks including:
- Answering questions and providing information
- Writing and creative tasks  
- Analysis and reasoning
- Coding and technical help
- General conversation

Respond naturally and be helpful while being mindful of context length."""
    
    def create_conversation(
        self, 
        model_id: str, 
        title: Optional[str] = None,
        system_prompt: Optional[str] = None,
        max_tokens: int = 8192
    ) -> str:
        """Create a new conversation and return its ID"""
        conversation_id = str(uuid.uuid4())
        now = datetime.now()
        
        # Generate title if not provided
        if not title:
            title = f"Chat {now.strftime('%Y-%m-%d %H:%M')}"
        
        # Use default system prompt if not provided
        if not system_prompt:
            system_prompt = self.default_system_prompt
        
        conversation = Conversation(
            id=conversation_id,
            title=title,
            model_id=model_id,
            messages=[],
            created_at=now,
            updated_at=now,
            max_tokens=max_tokens,
            system_prompt=system_prompt
        )
        
        # Add system message if system prompt provided
        if system_prompt:
            system_message = ChatMessage(
                id=str(uuid.uuid4()),
                role='system',
                content=system_prompt,
                timestamp=now
            )
            conversation.messages.append(system_message)
        
        self.conversations[conversation_id] = conversation
        return conversation_id
    
    def add_message(
        self, 
        conversation_id: str, 
        role: str, 
        content: str,
        token_count: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ChatMessage:
        """Add a message to a conversation"""
        if conversation_id not in self.conversations:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        conversation = self.conversations[conversation_id]
        
        message = ChatMessage(
            id=str(uuid.uuid4()),
            role=role,
            content=content,
            timestamp=datetime.now(),
            token_count=token_count,
            metadata=metadata
        )
        
        conversation.messages.append(message)
        conversation.updated_at = datetime.now()
        
        # Update total token count
        if token_count:
            conversation.total_tokens += token_count
        
        return message
    
    def get_conversation_for_model(self, conversation_id: str) -> List[Dict[str, str]]:
        """Get conversation in format suitable for LLM (OpenAI-style)"""
        if conversation_id not in self.conversations:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        conversation = self.conversations[conversation_id]
        
        # Convert to model format
        model_messages = []
        for message in conversation.messages:
            model_messages.append({
                'role': message.role,
                'content': message.content
            })
        
        return model_messages
    
    def trim_conversation(self, conversation_id: str, target_tokens: Optional[int] = None) -> int:
        """Trim old messages to fit within token limits"""
        if conversation_id not in self.conversations:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        conversation = self.conversations[conversation_id]
        
        if target_tokens is None:
            target_tokens = conversation.max_tokens * 0.75  # Use 75% of max
        
        if conversation.total_tokens <= target_tokens:
            return 0  # No trimming needed
        
        # Keep system message and recent messages
        system_messages = [msg for msg in conversation.messages if msg.role == 'system']
        other_messages = [msg for msg in conversation.messages if msg.role != 'system']
        
        # Remove oldest non-system messages until under target
        trimmed_count = 0
        current_tokens = conversation.total_tokens
        
        while current_tokens > target_tokens and len(other_messages) > 2:  # Keep at least last 2 messages
            removed_message = other_messages.pop(0)
            if removed_message.token_count:
                current_tokens -= removed_message.token_count
            trimmed_count += 1
        
        # Rebuild conversation
        conversation.messages = system_messages + other_messages
        conversation.total_tokens = current_tokens
        
        return trimmed_count
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by ID"""
        return self.conversations.get(conversation_id)
    
    def list_conversations(self) -> List[Dict[str, Any]]:
        """List all conversations with basic info"""
        return [
            {
                'id': conv.id,
                'title': conv.title,
                'model_id': conv.model_id,
                'message_count': len(conv.messages),
                'created_at': conv.created_at.isoformat(),
                'updated_at': conv.updated_at.isoformat()
            }
            for conv in sorted(self.conversations.values(), key=lambda x: x.updated_at, reverse=True)
        ]
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            return True
        return False
    
    def update_conversation_title(self, conversation_id: str, title: str) -> bool:
        """Update conversation title"""
        if conversation_id in self.conversations:
            self.conversations[conversation_id].title = title
            self.conversations[conversation_id].updated_at = datetime.now()
            return True
        return False
    
    def export_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Export conversation to JSON format"""
        if conversation_id in self.conversations:
            return self.conversations[conversation_id].to_dict()
        return None
    
    def import_conversation(self, data: Dict[str, Any]) -> str:
        """Import conversation from JSON format"""
        conversation = Conversation.from_dict(data)
        self.conversations[conversation.id] = conversation
        return conversation.id


# Global conversation manager instance
conversation_manager = ConversationManager()
