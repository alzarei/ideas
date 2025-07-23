"""
Simple Ollama Hello World Test
"""

import requests
import time


class OllamaClient:
    """Simple Ollama client with token management"""
    
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url
        self.model_limits = {
            "llama3.2:3b": 8192,
            "llama3.2:1b": 8192, 
            "llama3.1:8b": 8192,
            "codellama:7b": 16384,
            "mistral:7b": 8192,
        }
    
    def is_running(self):
        """Check if Ollama service is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def list_models(self):
        """Get available models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            return response.json().get('models', []) if response.status_code == 200 else []
        except requests.RequestException:
            return []
    
    def generate(self, model, prompt, timeout=60):
        """Generate text using Ollama model"""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False},
                timeout=timeout
            )
            return response.json().get('response', '') if response.status_code == 200 else None
        except requests.RequestException:
            return None
    
    def chat(self, model, messages, timeout=60):
        """Generate chat response with conversation history"""
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={"model": model, "messages": messages, "stream": False},
                timeout=timeout
            )
            if response.status_code == 200:
                return response.json().get('message', {}).get('content', '')
            return None
        except requests.RequestException:
            return None
    
    def estimate_tokens(self, text):
        """Estimate token count (1 token ≈ 4 characters)"""
        return len(text) // 4
    
    def get_token_limit(self, model_name):
        """Get context window size for model"""
        for model_pattern, limit in self.model_limits.items():
            if model_pattern in model_name.lower():
                return limit
        return 4096  # Conservative default
    
    def check_prompt_size(self, model_name, prompt):
        """Check if prompt fits in context window"""
        tokens = self.estimate_tokens(prompt)
        limit = self.get_token_limit(model_name)
        return {
            "tokens": tokens,
            "limit": limit,
            "fits": tokens < limit * 0.8,  # Leave room for response
            "usage_percent": (tokens / limit) * 100
        }


def main():
    print("� Ollama Test")
    
    client = OllamaClient()
    
    # Check connection
    if not client.is_running():
        print("❌ Ollama not running. Install: winget install Ollama.Ollama")
        return
    
    # Check models
    models = client.list_models()
    if not models:
        print("❌ No models. Run: ollama pull llama3.2:3b")
        return
    
    print(f"✅ Found model: {models[0]['name']}")
    
    # Test generation with token checking
    prompt = "Tell me something random and interesting about artificial intelligence."
    model_name = models[0]['name']
    
    # Check token limits
    token_info = client.check_prompt_size(model_name, prompt)
    print(f"Prompt: {prompt}")
    print(f"Tokens: {token_info['tokens']}/{token_info['limit']} ({token_info['usage_percent']:.1f}%)")
    
    if not token_info['fits']:
        print("⚠️ Prompt might be too long for optimal response")
    
    print("Generating response...")
    start = time.time()
    response = client.generate(model_name, prompt)
    
    if response:
        print(f"✅ Response ({time.time() - start:.1f}s): {response.strip()}")
    else:
        print("❌ Generation failed")


if __name__ == "__main__":
    main()
