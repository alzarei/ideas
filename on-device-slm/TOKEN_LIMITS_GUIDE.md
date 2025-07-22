# Token Limits: Local vs Cloud Comparison


**Local models have token limits, but they work very differently than Azure OpenAI!**

## Comparison Table

| Aspect | Local Models (Ollama) | Azure OpenAI | 
|--------|----------------------|--------------|
| **Context Window** | 4K-16K tokens (model dependent) | 8K-128K tokens (model dependent) |
| **Rate Limits** | ❌ None | ✅ Yes (RPM/TPM limits) |
| **Cost per Token** | ❌ Free | ✅ ~$0.01-0.10 per 1K tokens |
| **Monthly Quotas** | ❌ None | ✅ Yes (spending limits) |
| **Request Limits** | ❌ Unlimited | ✅ Limited by subscription |
| **Hardware Dependency** | ✅ Yes (local RAM/GPU) | ❌ No |
| **Internet Required** | ❌ No | ✅ Yes |

## Token Limits by Model

### Local Models (Ollama)
- **Llama 3.2 3B**: 8,192 tokens (~32,000 characters)
- **Llama 3.2 1B**: 8,192 tokens  
- **CodeLlama 7B**: 16,384 tokens
- **Mistral 7B**: 8,192 tokens
- **Phi-3 3.8B**: 4,096 tokens

### Azure OpenAI Models
- **GPT-4o**: 128,000 tokens
- **GPT-4**: 8,192 tokens (standard) / 32,768 tokens (turbo)
- **GPT-3.5-turbo**: 16,385 tokens
- **GPT-4o-mini**: 128,000 tokens

## Token Management Strategies

### For Local Models
```python
# Check token count before sending
def check_token_limit(prompt, model="llama3.2:3b"):
    estimated_tokens = len(prompt) // 4  # Rough estimate
    limit = 8192  # Llama 3.2 limit
    
    if estimated_tokens > limit * 0.8:  # Leave room for response
        print(f"⚠️ Prompt too long: {estimated_tokens} tokens")
        return False
    return True

# Auto-truncate long prompts
def truncate_prompt(prompt, max_tokens=6000):
    if len(prompt) // 4 > max_tokens:
        chars_to_keep = max_tokens * 4
        return "..." + prompt[-chars_to_keep:]
    return prompt
```

### For Azure OpenAI
```python
import tiktoken

def count_tokens_azure(text, model="gpt-4"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def check_azure_limits(prompt, model="gpt-4"):
    tokens = count_tokens_azure(prompt, model)
    limits = {"gpt-4": 8192, "gpt-4o": 128000}
    return tokens < limits.get(model, 8192)
```

## Best Practices

### Local Models
1. **Monitor context usage** - Keep prompts under 80% of limit
2. **Use model-specific limits** - Different models have different capacities
3. **No cost concerns** - Generate as much as needed

### Azure OpenAI  
1. **Optimize for cost** - Shorter prompts = lower costs
2. **Respect rate limits** - Implement backoff/retry logic
3. **Monitor usage** - Track token consumption

## Practical Examples

### Local Model Usage
```python
# Simple generation - no rate limits
response = ollama_client.generate(model, prompt)
```

### Azure OpenAI Usage
```python
# Handle rate limits
try:
    response = client.chat.completions.create(...)
except RateLimitError:
    time.sleep(60)
    response = client.chat.completions.create(...)
```

## When to Use Each

### Use Local Models When:
- 🔒 **Privacy critical** - Data stays on local machine
- 💰 **Cost sensitive** - No per-token charges
- 🚀 **High volume** - No rate limits
- 🌐 **Offline needed** - No internet dependency

### Use Azure OpenAI When:
- 🧠 **Need latest models** - GPT-4o, latest capabilities
- 📏 **Large context needed** - 128K+ token windows
- ⚡ **Speed critical** - Faster inference
- 🏢 **Enterprise features** - SLAs, support, compliance

## Summary

Local models are **free but limited by hardware and context size**. Azure OpenAI is **powerful but costs money and has usage limits**. 

For style training use cases, local models are ideal because:
- ✅ No cost for experimentation
- ✅ No rate limits for training iterations
- ✅ Privacy for sensitive writing samples
- ⚠️ Just need to manage the 8K token context window
