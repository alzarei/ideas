"""
Token Management for Local LLMs
Check limits, count tokens, and manage context windows
"""

import requests
import time
import json
from typing import List, Dict, Optional


class TokenManager:
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url
        # Approximate token limits for common models
        self.model_limits = {
            "llama3.2:3b": 8192,
            "llama3.2:1b": 8192,
            "llama3.1:8b": 8192,
            "llama3.1:70b": 8192,
            "codellama:7b": 16384,
            "mistral:7b": 8192,
            "phi3:3.8b": 4096,
        }
    
    def estimate_tokens(self, text: str) -> int:
        """Rough token estimation (1 token ≈ 4 characters for English)"""
        return len(text) // 4
    
    def get_model_info(self, model_name: str) -> Dict:
        """Get detailed model information including context window"""
        try:
            response = requests.post(
                f"{self.base_url}/api/show",
                json={"name": model_name}
            )
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return {}
    
    def get_context_limit(self, model_name: str) -> int:
        """Get context window size for a model"""
        # Try to get from model info first
        model_info = self.get_model_info(model_name)
        if model_info:
            # Look for context length in model parameters
            modelfile = model_info.get('modelfile', '')
            if 'num_ctx' in modelfile:
                # Extract num_ctx value
                for line in modelfile.split('\n'):
                    if 'num_ctx' in line:
                        try:
                            return int(line.split()[-1])
                        except:
                            pass
        
        # Fallback to known limits
        for model_pattern, limit in self.model_limits.items():
            if model_pattern in model_name.lower():
                return limit
        
        return 4096  # Conservative default
    
    def check_prompt_size(self, model_name: str, prompt: str) -> Dict:
        """Check if prompt fits within model's context window"""
        estimated_tokens = self.estimate_tokens(prompt)
        context_limit = self.get_context_limit(model_name)
        
        return {
            "estimated_tokens": estimated_tokens,
            "context_limit": context_limit,
            "fits": estimated_tokens < context_limit * 0.8,  # Leave room for response
            "usage_percent": (estimated_tokens / context_limit) * 100,
            "tokens_remaining": context_limit - estimated_tokens
        }
    
    def truncate_prompt(self, prompt: str, max_tokens: int, keep_end: bool = True) -> str:
        """Truncate prompt to fit within token limit"""
        estimated_tokens = self.estimate_tokens(prompt)
        
        if estimated_tokens <= max_tokens:
            return prompt
        
        # Calculate characters to keep
        chars_to_keep = max_tokens * 4  # Rough conversion
        
        if keep_end:
            return "..." + prompt[-chars_to_keep:]
        else:
            return prompt[:chars_to_keep] + "..."


class OllamaClientWithTokens:
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url
        self.token_manager = TokenManager(base_url)
    
    def generate_with_token_check(self, model: str, prompt: str, max_tokens: Optional[int] = None) -> Dict:
        """Generate text with automatic token limit checking"""
        # Check prompt size
        token_check = self.token_manager.check_prompt_size(model, prompt)
        
        result = {
            "token_info": token_check,
            "original_prompt": prompt,
            "final_prompt": prompt,
            "response": None,
            "truncated": False
        }
        
        # Truncate if necessary
        if not token_check["fits"]:
            context_limit = token_check["context_limit"]
            safe_limit = int(context_limit * 0.6)  # Leave room for response
            result["final_prompt"] = self.token_manager.truncate_prompt(prompt, safe_limit)
            result["truncated"] = True
            print(f"⚠️ Prompt truncated: {token_check['estimated_tokens']} → {self.token_manager.estimate_tokens(result['final_prompt'])} tokens")
        
        # Generate response
        try:
            generation_params = {"model": model, "prompt": result["final_prompt"], "stream": False}
            
            # Add max tokens if specified
            if max_tokens:
                generation_params["options"] = {"num_predict": max_tokens}
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=generation_params,
                timeout=120
            )
            
            if response.status_code == 200:
                result["response"] = response.json().get('response', '')
            
        except Exception as e:
            result["error"] = str(e)
        
        return result


def demonstrate_token_limits():
    """Demonstrate token limit checking and management"""
    print("🔢 Token Limit Management Demo")
    
    client = OllamaClientWithTokens()
    model = "llama3.2:3b"
    
    # Test 1: Normal prompt
    print("\n1️⃣ Normal Prompt Test")
    prompt = "Explain the concept of machine learning in simple terms."
    result = client.generate_with_token_check(model, prompt)
    
    print(f"Tokens: {result['token_info']['estimated_tokens']}/{result['token_info']['context_limit']}")
    print(f"Usage: {result['token_info']['usage_percent']:.1f}%")
    print(f"Fits: {'✅' if result['token_info']['fits'] else '❌'}")
    
    if result["response"]:
        response_tokens = client.token_manager.estimate_tokens(result["response"])
        print(f"Response tokens: {response_tokens}")
    
    # Test 2: Very long prompt
    print("\n2️⃣ Long Prompt Test")
    long_prompt = "Explain artificial intelligence. " * 1000  # Very long prompt
    result = client.generate_with_token_check(model, long_prompt)
    
    print(f"Original tokens: {client.token_manager.estimate_tokens(long_prompt)}")
    print(f"Final tokens: {result['token_info']['estimated_tokens']}")
    print(f"Truncated: {'✅' if result['truncated'] else '❌'}")
    
    # Test 3: Model limits comparison
    print("\n3️⃣ Model Limits Comparison")
    test_models = ["llama3.2:3b", "llama3.2:1b", "codellama:7b", "phi3:3.8b"]
    
    for test_model in test_models:
        limit = client.token_manager.get_context_limit(test_model)
        print(f"{test_model:<15}: {limit:,} tokens")


def main():
    print("🎯 Token Management for Local LLMs")
    
    # Check if Ollama is running
    token_manager = TokenManager()
    try:
        response = requests.get(f"{token_manager.base_url}/api/tags", timeout=5)
        if response.status_code != 200:
            print("❌ Ollama not running")
            return
    except:
        print("❌ Ollama not running")
        return
    
    demonstrate_token_limits()
    
    print("\n💡 Key Features:")
    print("  ✅ No rate limits")
    print("  ✅ No cost per token")
    print("  ⚠️ Fixed context window per model")


if __name__ == "__main__":
    main()
