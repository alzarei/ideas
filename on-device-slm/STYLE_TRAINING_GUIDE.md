# Style Training Guide for Local LLMs

## Overview
This guide shows how to train a local Llama model to write in a specific style using sample texts, with slight improvements to the original writing.

## Quick Start - Few-Shot Prompting (Recommended)

The easiest approach is to run the style training example:

```bash
cd examples
python style_training.py
```

This will:
1. Create sample writing files in `writing_samples/` directory
2. Load the writing samples 
3. Generate new text that mimics the style
4. Analyze style metrics for comparison

## Training Approaches

### 1. Few-Shot Prompting ⭐ (Start Here)
**Best for:** Quick experiments, testing different styles
- **Setup:** 5 minutes
- **Files needed:** Sample texts in `writing_samples/` folder
- **How it works:** Includes examples in every prompt
- **Effectiveness:** Good for consistent style mimicking

### 2. Fine-Tuning (Advanced)
**Best for:** Permanent style learning, production use
- **Setup:** 2-4 hours 
- **Requirements:** Python environment with training libraries
- **How it works:** Actually trains the model weights on training data
- **Effectiveness:** Excellent, persistent learning

### 3. RAG (Retrieval-Augmented Generation)
**Best for:** Large collections of sample texts
- **Setup:** 30-60 minutes
- **Requirements:** Vector database (ChromaDB/Pinecone)
- **How it works:** Retrieves relevant examples for each generation
- **Effectiveness:** Very good, scales well

## Setting Up Writing Samples

1. Create a `writing_samples/` directory
2. Add sample texts as `.txt` files
3. Each file should contain 100-2000 words
4. Include diverse examples of the target style

**Good sample structure:**
```
writing_samples/
├── email_style1.txt      # Professional emails
├── email_style2.txt      # More examples
├── blog_post1.txt        # Blog writing
└── creative_piece1.txt   # Creative writing
```

## Style Improvement Techniques

### Automated Improvements
The system can enhance writing by:
- **Clarity:** Simplifying complex sentences
- **Flow:** Improving transitions between ideas
- **Engagement:** Adding more dynamic language
- **Conciseness:** Removing redundant phrases

### Configuration Examples
```python
# For more creative writing
generation_params = {
    "temperature": 0.8,    # Higher = more creative
    "top_p": 0.9,
    "repeat_penalty": 1.1
}

# For professional writing
generation_params = {
    "temperature": 0.5,    # Lower = more consistent
    "top_p": 0.7,
    "repeat_penalty": 1.05
}
```

## Fine-Tuning Setup (Advanced)

### Requirements
```bash
pip install unsloth transformers datasets torch
```

### Training Data Format
Prepare training data as instruction-response pairs:
```json
{
    "instruction": "Write an email in the author's style about project updates",
    "input": "Project is 80% complete, minor delays in testing phase",
    "output": "Hi team,\n\nI wanted to give you a quick update on our project progress..."
}
```

### Training Command
```python
from unsloth import FastLanguageModel
import torch

# Load model for training
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/llama-3.2-3b-bnb-4bit",
    max_seq_length=2048,
    dtype=None,
    load_in_4bit=True,
)

# Add LoRA adapters
model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_alpha=16,
    lora_dropout=0,
    bias="none",
    use_gradient_checkpointing="unsloth",
    random_state=3407,
)
```

## Testing and Evaluation

### Style Metrics
The system analyzes:
- **Sentence length patterns**
- **Vocabulary complexity** 
- **Punctuation usage**
- **Paragraph structure**
- **Tone consistency**

### Quality Assessment
1. Generate multiple samples with the same prompt
2. Compare style metrics to original samples
3. Human evaluation for naturalness
4. A/B testing with different approaches

## Best Practices

### Sample Selection
- Use 5-20 high-quality examples
- Ensure consistent style across samples
- Include variety within the target style
- Remove any poor-quality examples

### Prompt Engineering
- Be specific about desired improvements
- Include context about the writing purpose
- Specify tone and audience
- Ask for specific enhancements

### Example Prompt
```
Study these writing samples and then write in the same style, but with improved clarity and engagement:

[Sample 1: Original author's text...]
[Sample 2: Another example...]

Task: Write a blog post about productivity tips.
Improvements: Make it more engaging, clearer structure, add specific examples.
```

## Troubleshooting

### Common Issues
- **Inconsistent style:** Add more/better samples
- **Too similar to examples:** Increase temperature
- **Poor quality:** Lower temperature, improve samples
- **Slow generation:** Use smaller model or optimize settings

### Performance Tips
- Start with few-shot prompting
- Use 3-5 examples per prompt for best results
- Fine-tune only if you need persistent learning
- Monitor generation quality vs. speed trade-offs

## Next Steps

1. Run `style_training.py` to test the approach
2. Add writing samples to `writing_samples/`
3. Experiment with different prompts and parameters
4. Consider fine-tuning for production use
