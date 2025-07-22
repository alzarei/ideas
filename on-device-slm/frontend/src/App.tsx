import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

interface HealthStatus {
  status: string;
  ollama_running: boolean;
  available_models: string[];
  services_available: boolean;
  api_version: string;
}

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface ChatResponse {
  response: string;
  token_info: any;
  response_time: number;
  word_count: number;
  model_used: string;
}

const App: React.FC = () => {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [writeResults, setWriteResults] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'chat' | 'write'>('chat');
  const [stylePrompt, setStylePrompt] = useState('');
  const [styleExamples, setStyleExamples] = useState('');
  const [wordLimit, setWordLimit] = useState(200);

  useEffect(() => {
    checkHealth();
  }, []);

  const checkHealth = async () => {
    try {
      const response = await axios.get('/api/health');
      setHealth(response.data);
    } catch (error) {
      console.error('Health check failed:', error);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setLoading(true);

    try {
      const response = await axios.post<ChatResponse>('/api/chat', {
        message: inputMessage,
        model: 'llama3.2:3b'
      });

      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat failed:', error);
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const generateWithStyle = async () => {
    if (!stylePrompt.trim()) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: `Write about: ${stylePrompt}`,
      timestamp: new Date()
    };

    setWriteResults(prev => [...prev, userMessage]);
    setLoading(true);
    
    try {
      const response = await axios.post('/api/style', {
        prompt: stylePrompt,
        examples: styleExamples.trim() ? styleExamples.split('\n---\n').filter(ex => ex.trim()) : [],
        word_limit: wordLimit,
        model: 'llama3.2:3b'
      });

      const styledMessage: ChatMessage = {
        role: 'assistant',
        content: response.data.generated_text,
        timestamp: new Date()
      };

      const analysisMessage: ChatMessage = {
        role: 'assistant',
        content: `📊 Analysis: ${response.data.style_analysis}`,
        timestamp: new Date()
      };

      setWriteResults(prev => [...prev, styledMessage, analysisMessage]);
      setStylePrompt('');
    } catch (error) {
      console.error('Style generation failed:', error);
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error generating styled text. Please try again.',
        timestamp: new Date()
      };
      setWriteResults(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent, action: () => void) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      action();
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>🤖 On-Device LLM Assistant</h1>
        <div className="status-indicator">
          {health ? (
            <span className={`status ${health.status}`}>
              {health.ollama_running ? '🟢' : '🟡'} 
              {health.status === 'healthy' ? 'Online' : 
               health.status === 'demo_mode' ? 'Demo Mode' : 'Offline'}
            </span>
          ) : (
            <span className="status checking">🔄 Checking...</span>
          )}
        </div>
      </header>

      <nav className="tab-navigation">
        <button 
          className={`tab-button ${activeTab === 'chat' ? 'active' : ''}`}
          onClick={() => setActiveTab('chat')}
        >
          💬 Chat
        </button>
        <button 
          className={`tab-button ${activeTab === 'write' ? 'active' : ''}`}
          onClick={() => setActiveTab('write')}
        >
          ✍️ Write (My Style)
        </button>
      </nav>

      <main className="main-content">
        {activeTab === 'chat' ? (
          <div className="chat-container">
            <div className="messages-container">
              {messages.length === 0 ? (
                <div className="welcome-message">
                  <h3>Welcome to your On-Device AI Assistant!</h3>
                  <p>Start a conversation with your local language model.</p>
                  {health && !health.ollama_running && (
                    <div className="demo-notice">
                      <strong>Demo Mode:</strong> Install Ollama for full functionality
                    </div>
                  )}
                </div>
              ) : (
                messages.map((message, index) => (
                  <div key={index} className={`message ${message.role}`}>
                    <div className="message-content">
                      {message.content}
                    </div>
                    <div className="message-timestamp">
                      {message.timestamp.toLocaleTimeString()}
                    </div>
                  </div>
                ))
              )}
              {loading && (
                <div className="message assistant">
                  <div className="message-content typing">
                    🤔 Thinking...
                  </div>
                </div>
              )}
            </div>

            <div className="input-container">
              <div className="chat-input">
                <textarea
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={(e) => handleKeyPress(e, sendMessage)}
                  placeholder="Type your message here... (Press Enter to send)"
                  disabled={loading}
                  rows={3}
                />
                <button 
                  onClick={sendMessage}
                  disabled={loading || !inputMessage.trim()}
                  className="send-button"
                >
                  {loading ? '⏳' : '📤'} Send
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div className="write-container">
            {/* Input Section */}
            <div className="write-input-section">
              <div className="write-controls-row">
                <div className="style-controls">
                  <label>
                    Word Limit:
                    <input
                      type="number"
                      value={wordLimit}
                      onChange={(e) => setWordLimit(Number(e.target.value))}
                      min="50"
                      max="500"
                    />
                  </label>
                </div>
                <button 
                  onClick={generateWithStyle}
                  disabled={loading || !stylePrompt.trim()}
                  className="generate-button"
                >
                  {loading ? '⏳ Generating...' : '✍️ Write in My Style'}
                </button>
              </div>
              
              <div className="examples-section">
                <label>Your Writing Examples (separate with --- on new lines):</label>
                <textarea
                  value={styleExamples}
                  onChange={(e) => setStyleExamples(e.target.value)}
                  placeholder="Paste examples of your writing style here. Separate multiple examples with '---' on new lines."
                  rows={4}
                  className="examples-textarea"
                />
              </div>
              
              <div className="prompt-section">
                <label>What would you like to write about?</label>
                <textarea
                  value={stylePrompt}
                  onChange={(e) => setStylePrompt(e.target.value)}
                  onKeyPress={(e) => handleKeyPress(e, generateWithStyle)}
                  placeholder="Enter a topic or prompt to write about in your style..."
                  disabled={loading}
                  rows={2}
                  className="prompt-textarea"
                />
              </div>
            </div>

            {/* Content Section - Expands with content */}
            <div className="write-content-section">
              {writeResults.length === 0 ? (
                <div className="write-welcome">
                  <h3>✍️ Custom Style Writing</h3>
                  <p>Train the model to write in your specific style by providing examples, then generate content that matches your voice and tone.</p>
                  {health && !health.ollama_running && (
                    <div className="demo-notice">
                      <strong>Demo Mode:</strong> Install Ollama for full functionality
                    </div>
                  )}
                </div>
              ) : (
                <div className="write-results">
                  {writeResults.map((result, index) => (
                    <div key={index} className={`write-item ${result.role}`}>
                      {result.role === 'user' ? (
                        <div className="write-prompt">
                          <h4>📝 Writing Prompt</h4>
                          <p>{result.content.replace('Write about: ', '')}</p>
                          <span className="timestamp">{result.timestamp.toLocaleTimeString()}</span>
                        </div>
                      ) : result.content.startsWith('📊') ? (
                        <div className="write-analysis">
                          <h4>📊 Style Analysis</h4>
                          <p>{result.content.replace('📊 Analysis: ', '')}</p>
                        </div>
                      ) : (
                        <div className="write-output">
                          <h4>✨ Generated Content</h4>
                          <div className="generated-text">
                            {result.content}
                          </div>
                          <span className="timestamp">{result.timestamp.toLocaleTimeString()}</span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
              
              {loading && (
                <div className="write-loading">
                  <div className="loading-content">
                    <span className="loading-icon">✍️</span>
                    <p>Generating content in your style...</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </main>

      <footer className="app-footer">
        <div className="footer-info">
          <span>API: {health?.api_version || 'Unknown'}</span>
          <span>Models: {health?.available_models.length || 0}</span>
          <a href="/api/docs" target="_blank" rel="noopener noreferrer">
            📖 API Docs
          </a>
        </div>
      </footer>
    </div>
  );
};

export default App;
