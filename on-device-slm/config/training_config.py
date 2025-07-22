"""
Advanced Style Training Configuration
Provides different training approaches and model fine-tuning options
"""

# Fine-tuning approach using Unsloth (LoRA)
FINE_TUNING_CONFIG = {
    "model_name": "unsloth/llama-3.2-3b-bnb-4bit",
    "max_seq_length": 2048,
    "dtype": None,  # Auto-detect
    "load_in_4bit": True,
    "lora_r": 16,
    "lora_alpha": 16,
    "lora_dropout": 0,
    "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    "use_gradient_checkpointing": "unsloth",
    "random_state": 3407,
    "use_rslora": False,
    "loftq_config": None,
}

# Few-shot prompting parameters
FEW_SHOT_CONFIG = {
    "max_examples": 5,
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 40,
    "max_tokens": 500,
    "repeat_penalty": 1.1
}

# RAG (Retrieval-Augmented Generation) config
RAG_CONFIG = {
    "chunk_size": 512,
    "chunk_overlap": 50,
    "embedding_model": "all-MiniLM-L6-v2",
    "similarity_threshold": 0.7,
    "max_retrieved_chunks": 3
}

# Style analysis metrics
STYLE_METRICS = [
    "sentence_length",
    "vocabulary_complexity",
    "punctuation_patterns",
    "paragraph_structure",
    "tone_indicators",
    "rhetorical_devices"
]

# Training data preparation
DATA_PREPARATION = {
    "min_text_length": 100,
    "max_text_length": 2000,
    "clean_patterns": [
        r'\s+',  # Multiple whitespace
        r'[^\w\s\.\!\?\,\;\:\-\(\)]',  # Non-standard characters
    ],
    "format_template": "### Instruction:\nWrite in the style of the given examples.\n\n### Input:\n{examples}\n\n### Response:\n{response}"
}

def get_training_approach_info():
    """Return information about different training approaches"""
    return {
        "few_shot": {
            "difficulty": "Easy",
            "setup_time": "5 minutes",
            "effectiveness": "Good",
            "description": "Include writing samples in prompts",
            "pros": ["No training required", "Works immediately", "Easy to experiment"],
            "cons": ["Limited context window", "Not persistent", "Less consistent"]
        },
        "fine_tuning": {
            "difficulty": "Advanced",
            "setup_time": "2-4 hours",
            "effectiveness": "Excellent",
            "description": "Train model weights on training data",
            "pros": ["Persistent learning", "Highly effective", "Customizable"],
            "cons": ["Requires technical setup", "Time-consuming", "Needs good samples"]
        },
        "rag": {
            "difficulty": "Intermediate",
            "setup_time": "30-60 minutes",
            "effectiveness": "Very Good",
            "description": "Retrieve relevant examples dynamically",
            "pros": ["Scalable", "Good balance", "Easy to update"],
            "cons": ["Requires vector database", "More complex", "Slower inference"]
        }
    }
