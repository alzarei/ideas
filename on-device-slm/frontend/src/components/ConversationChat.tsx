import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

interface Message {
  id: string;
  role: 'system' | 'user' | 'assistant';
  content: string;
  timestamp: string;
  token_count?: number;
}

interface Conversation {
  id: string;
  title: string;
  model_id: string;
  message_count: number;
  created_at: string;
  updated_at: string;
}

interface ChatResponse {
  response: string;
  token_info: {
    estimated_tokens: number;
    context_limit: number;
    fits: boolean;
    usage_percent: number;
  };
  response_time: number;
  word_count: number;
  model_used: string;
  conversation_id: string;
  message_id: string;
}

interface ConversationChatProps {
  selectedModel: string;
  availableModels: Array<{ id: string; name: string }>;
  // Persistent state props
  conversations: Conversation[];
  setConversations: React.Dispatch<React.SetStateAction<Conversation[]>>;
  currentConversation: string | null;
  setCurrentConversation: React.Dispatch<React.SetStateAction<string | null>>;
  messages: Message[];
  setMessages: (messagesOrUpdater: Message[] | ((prev: Message[]) => Message[])) => void;
  tokenInfo: ChatResponse['token_info'] | null;
  setTokenInfo: React.Dispatch<React.SetStateAction<ChatResponse['token_info'] | null>>;
}

const ConversationChat: React.FC<ConversationChatProps> = ({ 
  selectedModel, 
  availableModels,
  conversations,
  setConversations,
  currentConversation,
  setCurrentConversation,
  messages,
  setMessages,
  tokenInfo,
  setTokenInfo
}) => {
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [isInitialized, setIsInitialized] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll only when new messages are added (not when loading existing ones)
  const [shouldAutoScroll, setShouldAutoScroll] = useState(false);

  useEffect(() => {
    if (shouldAutoScroll) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
      setShouldAutoScroll(false);
    }
  }, [messages, shouldAutoScroll]);

  // Load conversations on mount (only once)
  useEffect(() => {
    if (!isInitialized) {
      loadConversations();
      setIsInitialized(true);
    }
  }, [isInitialized]);

  // Load conversation messages when conversation changes (only if not already loaded)
  useEffect(() => {
    if (currentConversation && messages.length === 0) {
      loadConversationMessages(currentConversation);
    }
  }, [currentConversation, messages.length]);

  const loadConversations = async () => {
    try {
      const response = await axios.get('/api/conversations');
      setConversations(response.data);
    } catch (error) {
      console.error('Failed to load conversations:', error);
    }
  };

  const loadConversationMessages = async (conversationId: string) => {
    try {
      const response = await axios.get(`/api/conversations/${conversationId}`);
      setMessages(response.data.messages || []);
      
      // Update token info based on conversation
      if (response.data.messages && response.data.messages.length > 0) {
        const totalTokens = response.data.messages.reduce(
          (sum: number, msg: Message) => sum + (msg.token_count || 0), 
          0
        );
        setTokenInfo({
          estimated_tokens: totalTokens,
          context_limit: response.data.max_tokens || 8192,
          fits: totalTokens < (response.data.max_tokens || 8192),
          usage_percent: (totalTokens / (response.data.max_tokens || 8192)) * 100
        });
      }
    } catch (error) {
      console.error('Failed to load conversation messages:', error);
    }
  };

  const createNewConversation = async () => {
    try {
      const response = await axios.post('/api/conversations', {
        model_id: selectedModel,
        title: `Chat with ${availableModels.find(m => m.id === selectedModel)?.name || selectedModel}`,
        max_tokens: 8192
      });
      
      const newConversation = response.data;
      setConversations(prev => [newConversation, ...prev]);
      setCurrentConversation(newConversation.id);
    } catch (error) {
      console.error('Failed to create conversation:', error);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    setLoading(true);

    try {
      // Add user message to UI immediately
      const tempUserMessage: Message = {
        id: 'temp-user',
        role: 'user',
        content: userMessage,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, tempUserMessage]);

      // Send to API
      const response = await axios.post<ChatResponse>('/api/chat', {
        message: userMessage,
        model: selectedModel,
        conversation_id: currentConversation
      });

      const { response: assistantResponse, conversation_id, token_info } = response.data;

      // Update current conversation if it was created
      if (!currentConversation && conversation_id) {
        setCurrentConversation(conversation_id);
        await loadConversations(); // Refresh conversation list
      }

      // Instead of reloading, update messages directly in UI
      const assistantMessage: Message = {
        id: response.data.message_id,
        role: 'assistant',
        content: assistantResponse,
        timestamp: new Date().toISOString(),
        token_count: Math.floor(response.data.word_count / 0.75) // Estimate tokens
      };

      // Remove temp message and add real messages
      setMessages(prev => {
        const withoutTemp = prev.filter(msg => msg.id !== 'temp-user');
        return [...withoutTemp, 
          {
            id: `user-${Date.now()}`,
            role: 'user' as const,
            content: userMessage,
            timestamp: new Date().toISOString(),
            token_count: Math.floor(userMessage.split(' ').length / 0.75)
          },
          assistantMessage
        ];
      });

      // Auto-scroll for new messages
      setShouldAutoScroll(true);
      setTokenInfo(token_info);

    } catch (error) {
      console.error('Failed to send message:', error);
      // Remove temp message on error
      setMessages(prev => prev.filter(msg => msg.id !== 'temp-user'));
      alert('Failed to send message. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const deleteConversation = async (conversationId: string) => {
    if (!window.confirm('Delete this conversation? This cannot be undone.')) return;

    try {
      await axios.delete(`/api/conversations/${conversationId}`);
      setConversations(prev => prev.filter(c => c.id !== conversationId));
      
      if (currentConversation === conversationId) {
        setCurrentConversation(null);
        setMessages([]);
        setTokenInfo(null);
      }
    } catch (error) {
      console.error('Failed to delete conversation:', error);
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  const getTokenUsageColor = (percentage: number) => {
    if (percentage < 50) return '#10b981'; // green
    if (percentage < 75) return '#f59e0b'; // yellow
    return '#ef4444'; // red
  };

  return (
    <div className="conversation-chat">
      <div className="chat-layout">
        {/* Sidebar with conversations */}
        <div className="conversations-sidebar">
          <div className="sidebar-header">
            <h3>Conversations</h3>
            <button onClick={createNewConversation} className="new-chat-btn">
              + New Chat
            </button>
          </div>
          
          <div className="conversations-list">
            {conversations.map(conv => (
              <div 
                key={conv.id}
                className={`conversation-item ${currentConversation === conv.id ? 'active' : ''}`}
                onClick={() => setCurrentConversation(conv.id)}
              >
                <div className="conversation-title">{conv.title}</div>
                <div className="conversation-meta">
                  {conv.message_count} messages • {new Date(conv.updated_at).toLocaleDateString()}
                </div>
                <button 
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteConversation(conv.id);
                  }}
                  className="delete-btn"
                  title="Delete conversation"
                >
                  ×
                </button>
              </div>
            ))}
            
            {conversations.length === 0 && (
              <div className="no-conversations">
                No conversations yet. Start a new chat!
              </div>
            )}
          </div>
        </div>

        {/* Main chat area */}
        <div className="chat-main">
          {currentConversation ? (
            <>
              {/* Chat header with token info */}
              <div className="chat-header">
                <div className="chat-title">
                  {conversations.find(c => c.id === currentConversation)?.title || 'Chat'}
                </div>
                {tokenInfo && (
                  <div className="token-info">
                    <span 
                      className="token-usage"
                      style={{ color: getTokenUsageColor(tokenInfo.usage_percent) }}
                    >
                      {tokenInfo.estimated_tokens}/{tokenInfo.context_limit} tokens 
                      ({tokenInfo.usage_percent.toFixed(1)}%)
                    </span>
                  </div>
                )}
              </div>

              {/* Messages */}
              <div className="messages-container">
                {messages
                  .filter(msg => msg.role !== 'system') // Hide system messages from UI
                  .map(message => (
                  <div key={message.id} className={`message ${message.role}`}>
                    <div className="message-content">{message.content}</div>
                    <div className="message-meta">
                      {formatTimestamp(message.timestamp)}
                      {message.token_count && (
                        <span className="token-count"> • {message.token_count} tokens</span>
                      )}
                    </div>
                  </div>
                ))}
                
                {loading && (
                  <div className="message assistant">
                    <div className="message-content typing">
                      <span></span><span></span><span></span>
                    </div>
                  </div>
                )}
                
                <div ref={messagesEndRef} />
              </div>

              {/* Input area */}
              <div className="chat-input-area">
                <div className="input-container">
                  <textarea
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        sendMessage();
                      }
                    }}
                    placeholder="Type your message... (Press Enter to send, Shift+Enter for new line)"
                    rows={3}
                    disabled={loading}
                  />
                  <button 
                    onClick={sendMessage} 
                    disabled={loading || !inputMessage.trim()}
                    className="send-btn"
                  >
                    {loading ? '...' : 'Send'}
                  </button>
                </div>
              </div>
            </>
          ) : (
            <div className="no-conversation">
              <h3>Welcome to Conversation Chat!</h3>
              <p>Select a conversation from the sidebar or create a new one to get started.</p>
              <p>This chat maintains conversation history and context across messages.</p>
              <button onClick={createNewConversation} className="start-chat-btn">
                Start New Conversation
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ConversationChat;
