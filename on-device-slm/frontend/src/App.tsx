import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import { useModelConfig, ModelConfig } from './hooks/useModelConfig';
import ModelManager from './components/ModelManager';
import ConversationChat from './components/ConversationChat';
import './components/ConversationChat.css';

interface HealthStatus {
  status: string;
  ollama_running: boolean;
  available_models: string[];
  services_available: boolean;
  api_version: string;
}

interface WriteMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface Conversation {
  id: string;
  title: string;
  model_id: string;
  message_count: number;
  created_at: string;
  updated_at: string;
}

interface Message {
  id: string;
  role: 'system' | 'user' | 'assistant';
  content: string;
  timestamp: string;
  token_count?: number;
}

interface TokenInfo {
  estimated_tokens: number;
  context_limit: number;
  fits: boolean;
  usage_percent: number;
}

const App: React.FC = () => {
  const {
    config: modelConfig,
    loading: modelConfigLoading,
    error: modelConfigError,
    getEnabledModels,
    getModelById
  } = useModelConfig();
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [writeResults, setWriteResults] = useState<WriteMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'chat' | 'write'>('chat');
  const [stylePrompt, setStylePrompt] = useState('');
  const [styleExamples, setStyleExamples] = useState('');
  const [wordLimit, setWordLimit] = useState(200);
  const [selectedModel, setSelectedModel] = useState('');
  const [showModelManager, setShowModelManager] = useState(false);

  // Persistent conversation state with caching
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversation, setCurrentConversation] = useState<string | null>(null);
  const [conversationCache, setConversationCache] = useState<Map<string, Message[]>>(new Map());
  const [tokenInfo, setTokenInfo] = useState<TokenInfo | null>(null);

  // Get messages for current conversation from cache
  const messages = currentConversation && conversationCache.has(currentConversation) 
    ? conversationCache.get(currentConversation) || []
    : [];

  // Function to update messages in cache
  const setMessages = (messagesOrUpdater: Message[] | ((prev: Message[]) => Message[])) => {
    if (!currentConversation) return;
    
    setConversationCache(prev => {
      const newCache = new Map(prev);
      const currentMessages = newCache.get(currentConversation) || [];
      
      const newMessages = typeof messagesOrUpdater === 'function' 
        ? messagesOrUpdater(currentMessages)
        : messagesOrUpdater;
      
      newCache.set(currentConversation, newMessages);
      return newCache;
    });
  };

  // Get available models from config
  const availableModels = modelConfig ? getEnabledModels() : [];

  useEffect(() => {
    checkHealth();
  }, []);

  // Set default model when config loads
  useEffect(() => {
    if (modelConfig && !selectedModel) {
      setSelectedModel(modelConfig.default_model);
    }
  }, [modelConfig, selectedModel]);

  const checkHealth = async () => {
    try {
      const response = await axios.get('/api/health');
      setHealth(response.data);
    } catch (error) {
      console.error('Health check failed:', error);
    }
  };

  const generateWithStyle = async () => {
    if (!stylePrompt.trim()) return;

    const userMessage: WriteMessage = {
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
        model: selectedModel
      });

      const styledMessage: WriteMessage = {
        role: 'assistant',
        content: response.data.generated_text,
        timestamp: new Date()
      };

      const analysisMessage: WriteMessage = {
        role: 'assistant',
        content: `📊 Analysis: ${response.data.style_analysis}`,
        timestamp: new Date()
      };

      setWriteResults(prev => [...prev, styledMessage, analysisMessage]);
      setStylePrompt('');
    } catch (error) {
      console.error('Style generation failed:', error);
      const errorMessage: WriteMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error generating styled text. Please try again.',
        timestamp: new Date()
      };
      setWriteResults(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const getSelectedModelInfo = () => {
    if (!modelConfig) return { 
      name: 'Loading...', 
      description: 'Loading model configuration...',
      install_command: ''
    };
    const model = getModelById(selectedModel) || availableModels[0];
    return model || { 
      name: 'No Models', 
      description: 'No models available',
      install_command: `ollama pull ${selectedModel}`
    };
  };

  const isModelAvailable = () => {
    return health?.available_models?.includes(selectedModel) || false;
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
        <div className="header-controls">
          <div className="model-selector">
            <label>Model:</label>
            <select 
              value={selectedModel} 
              onChange={(e) => setSelectedModel(e.target.value)}
              className="model-select"
              title={getSelectedModelInfo().description}
              disabled={modelConfigLoading}
            >
              {modelConfigLoading ? (
                <option value="">Loading models...</option>
              ) : availableModels.length > 0 ? (
                availableModels.map(model => (
                  <option key={model.id} value={model.id}>
                    {model.name} {health?.available_models?.includes(model.id) ? '✓' : '⚠️'}
                  </option>
                ))
              ) : (
                <option value="">No models configured</option>
              )}
            </select>
            <div className="model-status">
              {isModelAvailable() ? (
                <span className="model-available" title="Model is available">✓</span>
              ) : (
                <span className="model-unavailable" title="Model not installed - run: ollama pull">⚠️</span>
              )}
            </div>
          </div>
          <button 
            className="config-button"
            onClick={() => setShowModelManager(true)}
            title="Configure Models"
          >
            ⚙️ Models
          </button>
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
        {modelConfigError && (
          <div className="model-warning">
            <div className="warning-content">
              <span className="warning-icon">⚠️</span>
              <div className="warning-text">
                <strong>Configuration Error:</strong> {modelConfigError}
              </div>
            </div>
          </div>
        )}
        
        {!isModelAvailable() && health?.ollama_running && selectedModel && (
          <div className="model-warning">
            <div className="warning-content">
              <span className="warning-icon">⚠️</span>
              <div className="warning-text">
                <strong>Model not available:</strong> {getSelectedModelInfo().name} is not installed.
                <br />
                <span className="install-command">Run: <code>{getSelectedModelInfo().install_command || `ollama pull ${selectedModel}`}</code></span>
              </div>
            </div>
          </div>
        )}
        
        {activeTab === 'chat' ? (
          <ConversationChat 
            selectedModel={selectedModel}
            availableModels={availableModels.map(model => ({
              id: model.id,
              name: model.name
            }))}
            conversations={conversations}
            setConversations={setConversations}
            currentConversation={currentConversation}
            setCurrentConversation={setCurrentConversation}
            messages={messages}
            setMessages={setMessages}
            tokenInfo={tokenInfo}
            setTokenInfo={setTokenInfo}
          />
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

      <ModelManager 
        isOpen={showModelManager}
        onClose={() => setShowModelManager(false)}
      />

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
