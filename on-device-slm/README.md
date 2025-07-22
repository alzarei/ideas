# On-Device Small Language Model Integration

This project demonstrates how to integrate on-device small language models with Windows process monitoring for intelligent system analysis.

## Project Structure

- `ollama_integration.py` - Integration with Ollama for local LLM
- `llm_analyzer.py` - Core LLM-powered analysis functions
- `requirements.txt` - Python dependencies
- `examples/` - Example usage and demos

## Setup

1. Install Ollama: https://ollama.ai/download
2. Pull a model: `ollama pull llama3.2:3b`
3. Install Python dependencies: `pip install -r requirements.txt`
4. Run examples: `python examples/hello_world.py`

## Models Tested

- **Llama 3.2 3B** - Good balance of performance and resource usage
- **Llama 3.2 1B** - Lighter weight option
- **Code Llama** - Specialized for code analysis

## Use Cases

- Intelligent process analysis and recommendations
- Anomaly detection in system behavior
- Natural language system reports
- Automated optimization suggestions
