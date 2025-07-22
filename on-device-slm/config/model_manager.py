"""
Model Configuration Manager
Centralized configuration for available language models
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ModelConfig:
    """Configuration for a single model"""
    id: str
    name: str
    description: str
    category: str
    size_gb: float
    context_window: int
    recommended_use: List[str]
    install_command: str
    enabled: bool = True
    priority: int = 1


class ModelConfigManager:
    """Manages model configurations from JSON file"""
    
    def __init__(self, config_path: Optional[Path] = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "models.json"
        
        self.config_path = config_path
        self._config_data = None
        self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                self._config_data = json.load(f)
            return self._config_data
        except FileNotFoundError:
            print(f"Config file not found: {self.config_path}")
            return self._get_default_config()
        except json.JSONDecodeError as e:
            print(f"Invalid JSON in config file: {e}")
            return self._get_default_config()
    
    def save_config(self) -> bool:
        """Save current configuration to JSON file"""
        try:
            # Ensure config directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w') as f:
                json.dump(self._config_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Failed to save config: {e}")
            return False
    
    def get_available_models(self, enabled_only: bool = True, 
                           available_in_ollama: Optional[List[str]] = None) -> List[ModelConfig]:
        """Get list of available models"""
        models = []
        
        for model_data in self._config_data.get('available_models', []):
            # Skip disabled models if requested
            if enabled_only and not model_data.get('enabled', True):
                continue
            
            # Check if model is actually available in Ollama (if list provided)
            if available_in_ollama is not None:
                if not any(model_data['id'] in available for available in available_in_ollama):
                    continue
            
            model = ModelConfig(**model_data)
            models.append(model)
        
        # Sort by priority
        sort_by = self._config_data.get('config', {}).get('sort_by', 'priority')
        if sort_by == 'priority':
            models.sort(key=lambda x: x.priority)
        elif sort_by == 'name':
            models.sort(key=lambda x: x.name)
        
        return models
    
    def get_enabled_models(self) -> List[ModelConfig]:
        """Get only enabled models"""
        return self.get_available_models(enabled_only=True)
    
    def get_model_by_id(self, model_id: str) -> Optional[ModelConfig]:
        """Get a specific model by ID"""
        for model_data in self._config_data.get('available_models', []):
            if model_data['id'] == model_id:
                return ModelConfig(**model_data)
        return None
    
    def get_models_by_category(self, category: str) -> List[ModelConfig]:
        """Get models in a specific category"""
        models = self.get_enabled_models()
        return [model for model in models if model.category == category]
    
    def get_default_model(self) -> str:
        """Get the default model ID"""
        return self._config_data.get('default_model', 'llama3.2:3b')
    
    def set_default_model(self, model_id: str) -> bool:
        """Set the default model"""
        if self.get_model_by_id(model_id):
            self._config_data['default_model'] = model_id
            return self.save_config()
        return False
    
    def enable_model(self, model_id: str) -> bool:
        """Enable a model"""
        return self._set_model_enabled(model_id, True)
    
    def disable_model(self, model_id: str) -> bool:
        """Disable a model"""
        return self._set_model_enabled(model_id, False)
    
    def _set_model_enabled(self, model_id: str, enabled: bool) -> bool:
        """Set model enabled/disabled state"""
        for model_data in self._config_data.get('available_models', []):
            if model_data['id'] == model_id:
                model_data['enabled'] = enabled
                return self.save_config()
        return False
    
    def add_model(self, model_config: ModelConfig) -> bool:
        """Add a new model to the configuration"""
        # Check if model already exists
        if self.get_model_by_id(model_config.id):
            return False
        
        model_dict = {
            'id': model_config.id,
            'name': model_config.name,
            'description': model_config.description,
            'category': model_config.category,
            'size_gb': model_config.size_gb,
            'context_window': model_config.context_window,
            'recommended_use': model_config.recommended_use,
            'install_command': model_config.install_command,
            'enabled': model_config.enabled,
            'priority': model_config.priority
        }
        
        self._config_data['available_models'].append(model_dict)
        return self.save_config()
    
    def remove_model(self, model_id: str) -> bool:
        """Remove a model from the configuration"""
        original_length = len(self._config_data.get('available_models', []))
        self._config_data['available_models'] = [
            model for model in self._config_data.get('available_models', [])
            if model['id'] != model_id
        ]
        
        if len(self._config_data['available_models']) < original_length:
            return self.save_config()
        return False
    
    def get_categories(self) -> Dict[str, Dict[str, str]]:
        """Get available categories"""
        return self._config_data.get('categories', {})
    
    def get_config_settings(self) -> Dict[str, Any]:
        """Get configuration settings"""
        return self._config_data.get('config', {})
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration if file doesn't exist"""
        return {
            "available_models": [
                {
                    "id": "llama3.2:3b",
                    "name": "Llama 3.2 3B",
                    "description": "Fast, efficient model",
                    "category": "general",
                    "size_gb": 2.0,
                    "context_window": 8192,
                    "recommended_use": ["chat", "qa"],
                    "install_command": "ollama pull llama3.2:3b",
                    "enabled": True,
                    "priority": 1
                }
            ],
            "default_model": "llama3.2:3b",
            "categories": {
                "general": {"name": "General Purpose", "description": "General chat models"}
            },
            "config": {
                "auto_enable_available": True,
                "show_disabled_models": False,
                "max_models_shown": 10,
                "sort_by": "priority"
            }
        }
    
    def export_frontend_config(self) -> Dict[str, Any]:
        """Export configuration for frontend use"""
        models = self.get_enabled_models()
        return {
            "available_models": [
                {
                    "id": model.id,
                    "name": model.name,
                    "description": model.description,
                    "category": model.category,
                    "size_gb": model.size_gb,
                    "install_command": model.install_command
                }
                for model in models
            ],
            "default_model": self.get_default_model(),
            "categories": self.get_categories()
        }


# Global instance for easy access
model_config = ModelConfigManager()
