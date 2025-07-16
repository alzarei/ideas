"""
Simple Ollama Hello World Test
"""

import requests
import time


class OllamaClient:
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url
    
    def is_running(self):
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def list_models(self):
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            return response.json().get('models', []) if response.status_code == 200 else []
        except:
            return []
    
    def generate(self, model, prompt):
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False},
                timeout=60
            )
            return response.json().get('response', '') if response.status_code == 200 else None
        except:
            return None


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
    
    # Test generation
    prompt = "Tell me something random and interesting about yourself."
    print(f"Prompt: {prompt}")
    print("Generating response...")
    start = time.time()
    response = client.generate(models[0]['name'], prompt)
    
    if response:
        print(f"✅ Response ({time.time() - start:.1f}s): {response.strip()}")
    else:
        print("❌ Generation failed")


if __name__ == "__main__":
    main()
