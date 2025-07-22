/**
 * Model Configuration Hook
 * Provides centralized model management for the frontend
 */

import { useState, useEffect } from 'react';
import axios from 'axios';

export interface ModelConfig {
  id: string;
  name: string;
  description: string;
  category: string;
  size_gb: number;
  install_command: string;
  available?: boolean;
}

export interface ModelCategory {
  name: string;
  description: string;
}

export interface ModelConfiguration {
  available_models: ModelConfig[];
  default_model: string;
  categories: { [key: string]: ModelCategory };
  demo: boolean;
  ollama_models?: string[];
}

export const useModelConfig = () => {
  const [config, setConfig] = useState<ModelConfiguration | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadConfig = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get<ModelConfiguration>('/api/models/config');
      setConfig(response.data);
    } catch (err) {
      console.error('Failed to load model config:', err);
      setError('Failed to load model configuration');
    } finally {
      setLoading(false);
    }
  };

  const setDefaultModel = async (modelId: string) => {
    try {
      await axios.post('/api/models/config/default', { model_id: modelId });
      await loadConfig(); // Reload config
      return true;
    } catch (err) {
      console.error('Failed to set default model:', err);
      setError('Failed to set default model');
      return false;
    }
  };

  const enableModel = async (modelId: string) => {
    try {
      await axios.post('/api/models/config/enable', { model_id: modelId });
      await loadConfig(); // Reload config
      return true;
    } catch (err) {
      console.error('Failed to enable model:', err);
      setError('Failed to enable model');
      return false;
    }
  };

  const disableModel = async (modelId: string) => {
    try {
      await axios.post('/api/models/config/disable', { model_id: modelId });
      await loadConfig(); // Reload config
      return true;
    } catch (err) {
      console.error('Failed to disable model:', err);
      setError('Failed to disable model');
      return false;
    }
  };

  const addModel = async (modelData: Partial<ModelConfig>) => {
    try {
      await axios.post('/api/models/config/add', modelData);
      await loadConfig(); // Reload config
      return true;
    } catch (err) {
      console.error('Failed to add model:', err);
      setError('Failed to add model');
      return false;
    }
  };

  const getAvailableModels = () => {
    if (!config) return [];
    return config.available_models.filter(model => model.available);
  };

  const getEnabledModels = () => {
    if (!config) return [];
    return config.available_models;
  };

  const getModelsByCategory = (category: string) => {
    if (!config) return [];
    return config.available_models.filter(model => model.category === category);
  };

  const getModelById = (modelId: string) => {
    if (!config) return null;
    return config.available_models.find(model => model.id === modelId) || null;
  };

  useEffect(() => {
    loadConfig();
  }, []);

  return {
    config,
    loading,
    error,
    loadConfig,
    setDefaultModel,
    enableModel,
    disableModel,
    addModel,
    getAvailableModels,
    getEnabledModels,
    getModelsByCategory,
    getModelById
  };
};
