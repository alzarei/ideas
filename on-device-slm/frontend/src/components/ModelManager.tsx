/**
 * Model Management Component
 * Provides UI for managing model configuration
 */

import React, { useState } from 'react';
import { useModelConfig, ModelConfig } from '../hooks/useModelConfig';
import './ModelManager.css';

interface ModelManagerProps {
  isOpen: boolean;
  onClose: () => void;
}

const ModelManager: React.FC<ModelManagerProps> = ({ isOpen, onClose }) => {
  const {
    config,
    loading,
    error,
    enableModel,
    disableModel,
    setDefaultModel,
    addModel,
    getModelsByCategory
  } = useModelConfig();

  const [showAddForm, setShowAddForm] = useState(false);
  const [newModel, setNewModel] = useState<Partial<ModelConfig>>({
    id: '',
    name: '',
    description: '',
    category: 'general',
    size_gb: 0,
    install_command: ''
  });

  if (!isOpen) return null;

  const handleToggleModel = async (modelId: string, enabled: boolean) => {
    if (enabled) {
      await disableModel(modelId);
    } else {
      await enableModel(modelId);
    }
  };

  const handleSetDefault = async (modelId: string) => {
    await setDefaultModel(modelId);
  };

  const handleAddModel = async (e: React.FormEvent) => {
    e.preventDefault();
    if (newModel.id && newModel.name) {
      const success = await addModel({
        ...newModel,
        install_command: newModel.install_command || `ollama pull ${newModel.id}`
      });
      
      if (success) {
        setNewModel({
          id: '',
          name: '',
          description: '',
          category: 'general',
          size_gb: 0,
          install_command: ''
        });
        setShowAddForm(false);
      }
    }
  };

  const categories = config?.categories || {};
  const allModels = config?.available_models || [];

  return (
    <div className="model-manager-overlay">
      <div className="model-manager">
        <div className="model-manager-header">
          <h2>🤖 Model Configuration</h2>
          <button className="close-button" onClick={onClose}>✕</button>
        </div>

        {loading && <div className="loading">Loading configuration...</div>}
        {error && <div className="error">Error: {error}</div>}

        {config && (
          <div className="model-manager-content">
            <div className="model-manager-actions">
              <button 
                className="add-model-button"
                onClick={() => setShowAddForm(!showAddForm)}
              >
                {showAddForm ? '✕ Cancel' : '+ Add Model'}
              </button>
            </div>

            {showAddForm && (
              <form className="add-model-form" onSubmit={handleAddModel}>
                <h3>Add New Model</h3>
                <div className="form-row">
                  <input
                    type="text"
                    placeholder="Model ID (e.g., llama3.2:3b)"
                    value={newModel.id || ''}
                    onChange={(e) => setNewModel({...newModel, id: e.target.value})}
                    required
                  />
                  <input
                    type="text"
                    placeholder="Display Name"
                    value={newModel.name || ''}
                    onChange={(e) => setNewModel({...newModel, name: e.target.value})}
                    required
                  />
                </div>
                <div className="form-row">
                  <select
                    value={newModel.category || 'general'}
                    onChange={(e) => setNewModel({...newModel, category: e.target.value})}
                  >
                    {Object.entries(categories).map(([key, cat]) => (
                      <option key={key} value={key}>{cat.name}</option>
                    ))}
                  </select>
                  <input
                    type="number"
                    step="0.1"
                    placeholder="Size (GB)"
                    value={newModel.size_gb || ''}
                    onChange={(e) => setNewModel({...newModel, size_gb: parseFloat(e.target.value) || 0})}
                  />
                </div>
                <textarea
                  placeholder="Description"
                  value={newModel.description || ''}
                  onChange={(e) => setNewModel({...newModel, description: e.target.value})}
                  rows={2}
                />
                <input
                  type="text"
                  placeholder="Install command (optional)"
                  value={newModel.install_command || ''}
                  onChange={(e) => setNewModel({...newModel, install_command: e.target.value})}
                />
                <button type="submit" className="submit-button">Add Model</button>
              </form>
            )}

            <div className="model-categories">
              {Object.entries(categories).map(([categoryKey, category]) => {
                const categoryModels = getModelsByCategory(categoryKey);
                if (categoryModels.length === 0) return null;

                return (
                  <div key={categoryKey} className="model-category">
                    <h3>{category.name}</h3>
                    <p className="category-description">{category.description}</p>
                    
                    <div className="model-list">
                      {categoryModels.map((model) => (
                        <div key={model.id} className="model-item">
                          <div className="model-info">
                            <div className="model-header">
                              <h4>{model.name}</h4>
                              <div className="model-badges">
                                {model.available && <span className="badge available">Available</span>}
                                {model.id === config.default_model && <span className="badge default">Default</span>}
                                <span className="badge size">{model.size_gb.toFixed(1)} GB</span>
                              </div>
                            </div>
                            <p className="model-description">{model.description}</p>
                            <code className="install-command">{model.install_command}</code>
                          </div>
                          
                          <div className="model-actions">
                            <button
                              className={`toggle-button ${true ? 'enabled' : 'disabled'}`}
                              onClick={() => handleToggleModel(model.id, true)}
                              title="Toggle model enabled/disabled"
                            >
                              {true ? 'Enabled' : 'Disabled'}
                            </button>
                            
                            {model.id !== config.default_model && (
                              <button
                                className="default-button"
                                onClick={() => handleSetDefault(model.id)}
                                title="Set as default model"
                              >
                                Set Default
                              </button>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="config-info">
              <h3>Current Configuration</h3>
              <p><strong>Default Model:</strong> {config.default_model}</p>
              <p><strong>Total Models:</strong> {allModels.length}</p>
              <p><strong>Available Models:</strong> {allModels.filter(m => m.available).length}</p>
              {config.demo && <p className="demo-notice">⚠️ Running in demo mode</p>}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ModelManager;
