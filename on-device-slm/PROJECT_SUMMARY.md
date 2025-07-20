# 🤖 On-Device Language Model Setup - Complete Guide

## Project Overview
This project demonstrates how to set up and use on-device language models for style training and text generation, with comprehensive token management.

## 📁 Project Structure
```
on-device-slm/
├── README.md                    # Project overview and setup
├── requirements.txt             # Python dependencies
├── TOKEN_LIMITS_GUIDE.md       # Token limits comparison (local vs cloud)
├── STYLE_TRAINING_GUIDE.md     # Complete style training guide
├── examples/
│   ├── hello_world.py          # Basic Ollama integration with token checking
│   ├── style_training.py       # Few-shot style mimicking
│   └── token_management.py     # Advanced token limit management
├── config/
│   └── training_config.py      # Configuration for different training approaches
└── writing_samples/            # Sample texts for style training
    ├── sample1.txt
    ├── sample2.txt
    └── sample3.txt
```

## 🚀 Quick Start

### 1. Install Ollama
```bash
winget install Ollama.Ollama
```

### 2. Download a Model
```bash
ollama pull llama3.2:3b
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Examples
```bash
# Basic test with token checking
python examples/hello_world.py

# Style training demo
python examples/style_training.py

# Advanced token management
python examples/token_management.py
```

## 🎯 Key Features

### ✅ What's Included
- **Basic Ollama Integration**: Simple client with token checking
- **Style Training**: Few-shot prompting to mimic writing styles
- **Token Management**: Automatic limit checking and truncation
- **Sample Data**: Pre-configured writing samples
- **Configuration**: Settings for different training approaches

### 🔍 Token Limits Explained
- **Local Models**: 4K-16K tokens, no rate limits, free
- **Cloud APIs**: 8K-128K tokens, rate limits, costs money
- **Your Model**: Llama 3.2 3B has 8,192 tokens (~32K characters)

## 🎨 Style Training Options

### 1. Few-Shot Prompting ⭐ (Recommended)
- **Setup**: 5 minutes
- **How**: Include examples in prompts
- **Best for**: Quick experiments, testing styles

### 2. Fine-Tuning (Advanced)
- **Setup**: 2-4 hours
- **How**: Train model weights on your data
- **Best for**: Production use, permanent learning

### 3. RAG (Intermediate)
- **Setup**: 30-60 minutes  
- **How**: Retrieve relevant examples dynamically
- **Best for**: Large sample collections

## 💡 Usage Examples

### Basic Generation with Token Checking
```python
from examples.hello_world import OllamaClient

client = OllamaClient()
prompt = "Write a professional email"

# Check if prompt fits
token_info = client.check_prompt_size("llama3.2:3b", prompt)
print(f"Tokens: {token_info['tokens']}/{token_info['limit']}")

# Generate response
response = client.generate("llama3.2:3b", prompt)
```

### Style Training
```python
from examples.style_training import StyleTrainer

trainer = StyleTrainer()
trainer.load_writing_samples("writing_samples")

# Generate in learned style
response = trainer.generate_with_style(
    "llama3.2:3b", 
    "Write about productivity"
)
```

## 🆚 Local vs Cloud Comparison

| Feature | Local (Ollama) | Azure OpenAI |
|---------|----------------|--------------|
| Cost | Free | ~$0.01-0.10/1K tokens |
| Rate Limits | None | Yes (RPM/TPM) |
| Context Window | 8K tokens | 8K-128K tokens |
| Privacy | Complete | Data sent to cloud |
| Internet | Not required | Required |
| Speed | Slower (8-30s) | Faster (1-5s) |

## 🔧 Configuration Options

### Model Settings
```python
# More creative
{"temperature": 0.8, "top_p": 0.9}

# More focused  
{"temperature": 0.5, "top_p": 0.7}

# Limit response length
{"num_predict": 200}
```

### Token Management
```python
# Auto-truncate long prompts
client.truncate_prompt(long_text, max_tokens=6000)

# Split conversations
chunks = client.split_long_conversation(messages, model)
```

## 🎯 Best Practices

### For Style Training
1. Use 5-20 high-quality writing samples
2. Ensure consistent style across samples
3. Test with different prompts and parameters
4. Monitor generation quality vs. speed

### For Token Management
1. Keep prompts under 80% of context limit
2. Monitor token usage with built-in tools
3. Truncate intelligently (keep important context)
4. Consider model-specific limits

## 🚨 Troubleshooting

### Common Issues
- **Slow generation**: Normal for local models (8-30 seconds)
- **Inconsistent style**: Add more/better training samples
- **Token limit exceeded**: Use truncation or chunking
- **Poor quality**: Adjust temperature or improve samples

### Performance Tips
- Start with few-shot prompting
- Use smaller models for faster responses
- Monitor system resources (RAM/CPU usage)
- Experiment with different parameter settings

## 🔄 Next Steps

1. **Experiment**: Try different writing samples and prompts
2. **Optimize**: Tune parameters for your specific use case  
3. **Scale**: Consider fine-tuning for production use
4. **Integrate**: Add to existing applications or workflows

## 📚 Additional Resources

- [Ollama Documentation](https://ollama.ai/docs)
- [Llama Model Cards](https://huggingface.co/meta-llama)
- [Fine-tuning Guide](STYLE_TRAINING_GUIDE.md)
- [Token Limits Explained](TOKEN_LIMITS_GUIDE.md)

---

**Ready to start? Run `python examples/hello_world.py` to test your setup!** 🚀
