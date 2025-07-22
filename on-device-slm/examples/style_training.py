"""
Style Training with Few-Shot Prompting
Train a local model to mimic writing style using sample texts
"""

import requests
import time
import os
from pathlib import Path


class StyleTrainer:
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url
        self.style_samples = []
    
    def is_running(self):
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def load_writing_samples(self, samples_dir):
        """Load writing samples from text files"""
        samples_path = Path(samples_dir)
        if not samples_path.exists():
            return False
            
        for file_path in samples_path.glob("*.txt"):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    self.style_samples.append({
                        'filename': file_path.name,
                        'content': content
                    })
        return len(self.style_samples) > 0
    
    def create_style_prompt(self, writing_task, num_examples=3):
        """Create a few-shot prompt with writing samples"""
        if not self.style_samples:
            return writing_task
        
        # Use up to num_examples samples
        examples = self.style_samples[:num_examples]
        
        prompt = "Study these writing examples and then write in the same style:\n\n"
        
        # Add example writings
        for i, sample in enumerate(examples, 1):
            prompt += f"EXAMPLE {i}:\n{sample['content']}\n\n"
        
        prompt += f"Now write in the same style for this task: {writing_task}\n\n"
        prompt += "RESPONSE:"
        
        return prompt
    
    def generate_with_style(self, model, writing_task, temperature=0.7, max_words=200):
        """Generate text that mimics the learned style"""
        style_prompt = self.create_style_prompt(writing_task)
        style_prompt += f"\n\nWrite approximately {max_words} words."
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": style_prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "top_p": 0.9,
                        "top_k": 40,
                        "num_predict": max_words * 2  # Token limit (rough estimate)
                    }
                },
                timeout=120
            )
            return response.json().get('response', '') if response.status_code == 200 else None
        except:
            return None
    
    def analyze_style(self, text):
        """Simple style analysis"""
        sentences = text.split('.')
        words = text.split()
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        
        return {
            'word_count': len(words),
            'sentence_count': len(sentences),
            'avg_sentence_length': round(avg_sentence_length, 1)
        }


def create_sample_directory():
    """Create sample writing directory with examples"""
    samples_dir = Path("writing_samples")
    samples_dir.mkdir(exist_ok=True)
    
    # Create sample writing files
    samples = {
        "sample1.txt": """The morning sun filtered through the venetian blinds, casting zebra stripes across the hardwood floor. Coffee brewing in the kitchen promised warmth against the autumn chill. These small rituals anchor us to the day ahead, providing comfort in their predictable rhythm.""",
        
        "sample2.txt": """Technology promises to connect us, yet paradoxically leaves many feeling more isolated than ever. The glow of screens illuminates faces but dims genuine human interaction. Perhaps the solution lies not in abandoning these tools, but in wielding them more thoughtfully.""",
        
        "sample3.txt": """Walking through the old neighborhood revealed layers of memory embedded in familiar streets. The corner store remained unchanged, its faded awning a testament to persistence. Time moves forward relentlessly, but certain places serve as anchors to our past selves."""
    }
    
    for filename, content in samples.items():
        sample_path = samples_dir / filename
        if not sample_path.exists():
            with open(sample_path, 'w', encoding='utf-8') as f:
                f.write(content)
    
    return samples_dir


def main():
    print("🎨 Style Training with Local LLM")
    
    # Configuration
    MAX_WORDS = 200  # Configurable word limit
    
    trainer = StyleTrainer()
    
    # Check Ollama connection
    if not trainer.is_running():
        print("❌ Ollama not running. Install: winget install Ollama.Ollama")
        return
    
    # Create and load sample writings
    samples_dir = create_sample_directory()
    print(f"📁 Created sample directory: {samples_dir}")
    
    if not trainer.load_writing_samples(samples_dir):
        print("❌ No writing samples found")
        return
    
    print(f"✅ Loaded {len(trainer.style_samples)} writing samples")
    
    # Analyze style of samples
    print("\n📊 Style Analysis of Samples:")
    for sample in trainer.style_samples:
        analysis = trainer.analyze_style(sample['content'])
        print(f"  {sample['filename']}: {analysis['word_count']} words, {analysis['avg_sentence_length']} avg sentence length")
    
    # Single example about AI/ML tech leader
    writing_task = "Write about the daily life and challenges of an AI/ML Tech Leader at a major technology company in the era of artificial intelligence"
    
    model = "llama3.2:3b"  # Use available model
    
    print(f"\n✍️ Task: {writing_task}")
    print(f"📝 Target length: {MAX_WORDS} words")
    print("Generating styled response...")
    
    start = time.time()
    response = trainer.generate_with_style(model, writing_task, max_words=MAX_WORDS)
    
    if response:
        print(f"✅ Response ({time.time() - start:.1f}s):")
        print(f"{response.strip()}")
        
        # Analyze generated style
        analysis = trainer.analyze_style(response)
        print(f"📊 Generated: {analysis['word_count']} words, {analysis['avg_sentence_length']} avg sentence length")
        
        # Check if within target range
        word_diff = analysis['word_count'] - MAX_WORDS
        if abs(word_diff) <= 50:  # Within 50 words
            print(f"✅ Length target met (±{word_diff} words)")
        else:
            print(f"⚠️ Length off target by {word_diff} words")
    else:
        print("❌ Generation failed")


if __name__ == "__main__":
    main()
