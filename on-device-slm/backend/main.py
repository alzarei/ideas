"""
FastAPI Backend for On-Device LLM Assistant
Professional API server for local AI interactions
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
import uvicorn
import sys
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add parent directory to path for importing our existing modules
sys.path.append(str(Path(__file__).parent.parent))

try:
    from examples.hello_world import OllamaClient
    from examples.style_training import StyleTrainer
    from examples.token_management import TokenManager
except ImportError as e:
    print(f"Warning: Could not import modules: {e}")
    # We'll create fallback implementations

app = FastAPI(
    title="On-Device LLM Assistant API",
    description="Professional API for local language model interactions with style training",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI services
try:
    ollama_client = OllamaClient()
    style_trainer = StyleTrainer()
    token_manager = TokenManager()
    SERVICES_AVAILABLE = True
except:
    SERVICES_AVAILABLE = False
    print("Warning: AI services not available. Running in demo mode.")

# Pydantic models for API
class ChatRequest(BaseModel):
    message: str
    model: str = "llama3.2:3b"

class ChatResponse(BaseModel):
    response: str
    token_info: Dict[str, Any]
    response_time: float
    word_count: int
    model_used: str

class StyleRequest(BaseModel):
    prompt: str
    examples: List[str] = []
    word_limit: int = 200
    model: str = "llama3.2:3b"

class StyleResponse(BaseModel):
    generated_text: str
    word_count: int
    style_analysis: str
    response_time: float
    meets_word_limit: bool

class HealthResponse(BaseModel):
    status: str
    ollama_running: bool
    available_models: List[str]
    services_available: bool
    api_version: str

# API Routes
@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Check API and Ollama service health"""
    if not SERVICES_AVAILABLE:
        return HealthResponse(
            status="demo_mode",
            ollama_running=False,
            available_models=[],
            services_available=False,
            api_version="1.0.0"
        )
    
    try:
        is_running = ollama_client.is_running()
        models = ollama_client.list_models() if is_running else []
        
        return HealthResponse(
            status="healthy" if is_running else "ollama_offline",
            ollama_running=is_running,
            available_models=models,
            services_available=True,
            api_version="1.0.0"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.post("/api/chat", response_model=ChatResponse)
async def chat_completion(request: ChatRequest):
    """Generate chat response with token management"""
    if not SERVICES_AVAILABLE:
        # Demo response
        return ChatResponse(
            response="Demo mode: This would be a response from your local Llama model. Install Ollama and restart to enable full functionality.",
            token_info={"estimated_tokens": 20, "context_limit": 8192, "fits": True, "usage_percent": 0.24},
            response_time=0.5,
            word_count=25,
            model_used=request.model
        )
    
    try:
        start_time = time.time()
        
        # Check token limits
        token_check = token_manager.check_prompt_size(request.model, request.message)
        
        if not token_check["fits"]:
            raise HTTPException(
                status_code=400,
                detail=f"Prompt exceeds token limit: {token_check['estimated_tokens']} > {token_check['context_limit']}"
            )
        
        # Generate response
        response_text = ollama_client.generate(request.model, request.message)
        response_time = time.time() - start_time
        word_count = len(response_text.split())
        
        return ChatResponse(
            response=response_text,
            token_info=token_check,
            response_time=response_time,
            word_count=word_count,
            model_used=request.model
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat generation failed: {str(e)}")

@app.post("/api/style", response_model=StyleResponse)
async def style_generation(request: StyleRequest):
    """Generate text in the user's custom writing style"""
    if not SERVICES_AVAILABLE:
        # Demo response
        if request.examples:
            demo_text = f"Based on your writing style, here's how one might approach {request.prompt.lower()}: The careful attention to detail and thoughtful consideration of various perspectives suggests a nuanced understanding of the topic."
        else:
            demo_text = f"To write about {request.prompt.lower()}, one might consider the various aspects and implications, crafting a response that reflects careful thought and consideration."
        
        return StyleResponse(
            generated_text=demo_text,
            word_count=len(demo_text.split()),
            style_analysis="Demo mode: Custom style analysis available when Ollama is running.",
            response_time=0.3,
            meets_word_limit=len(demo_text.split()) <= request.word_limit
        )
    
    try:
        start_time = time.time()
        
        # Create a style-aware prompt
        if request.examples:
            # Use user's examples for style training
            style_prompt = "Study these writing examples and then write in the same style:\n\n"
            for i, example in enumerate(request.examples[:3], 1):  # Limit to 3 examples
                style_prompt += f"EXAMPLE {i}:\n{example.strip()}\n\n"
            style_prompt += f"Now write in the same style for this topic: {request.prompt}\n\n"
            style_prompt += f"Write approximately {request.word_limit} words.\n\nRESPONSE:"
        else:
            # Fallback to simple prompt
            style_prompt = f"Write about {request.prompt}. Write approximately {request.word_limit} words."
        
        # Generate response using Ollama
        response = ollama_client.generate(request.model, style_prompt)
        generated_text = response if response else "Failed to generate response."
        
        response_time = time.time() - start_time
        word_count = len(generated_text.split())
        
        # Analyze style elements
        if request.examples:
            # Analyze similarity to provided examples
            style_analysis = f"Generated {word_count} words based on your {len(request.examples)} writing examples. "
            style_analysis += "Style training applied successfully." if request.examples else "No examples provided for style reference."
        else:
            style_analysis = f"Generated {word_count} words without specific style examples."
        
        return StyleResponse(
            generated_text=generated_text,
            word_count=word_count,
            style_analysis=style_analysis,
            response_time=response_time,
            meets_word_limit=word_count <= request.word_limit
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Style generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Style generation failed: {str(e)}")

@app.get("/api/models")
async def get_available_models():
    """Get list of available Ollama models"""
    if not SERVICES_AVAILABLE:
        return {"models": ["llama3.2:3b", "llama3.2:1b"], "demo": True}
    
    try:
        models = ollama_client.list_models()
        return {"models": models, "demo": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch models: {str(e)}")

# Mount static files for React frontend
frontend_build_path = Path(__file__).parent.parent / "frontend" / "build"
if frontend_build_path.exists():
    app.mount("/static", StaticFiles(directory=frontend_build_path / "static"), name="static")

# Serve React frontend (when built)
@app.get("/")
async def serve_frontend():
    """Serve React frontend or fallback page"""
    frontend_path = Path(__file__).parent.parent / "frontend" / "build" / "index.html"
    
    if frontend_path.exists():
        return FileResponse(frontend_path)
    else:
        # Return simple status page
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>On-Device LLM Assistant</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; 
                       margin: 0; padding: 40px; background: #f5f5f5; }}
                .container {{ max-width: 800px; margin: 0 auto; background: white; 
                            padding: 40px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
                .status {{ background: #e8f5e8; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .api-link {{ display: inline-block; margin: 10px; padding: 12px 24px; 
                           background: #007acc; color: white; text-decoration: none; border-radius: 6px; }}
                .api-link:hover {{ background: #005999; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 On-Device LLM Assistant</h1>
                <div class="status">
                    <h3>✅ FastAPI Backend Running</h3>
                    <p>Professional API server operational on <code>http://localhost:8000</code></p>
                </div>
                <h3>Available Endpoints:</h3>
                <a href="/api/docs" class="api-link">📖 API Documentation</a>
                <a href="/api/health" class="api-link">🏥 Health Check</a>
                <a href="/api/models" class="api-link">🤖 Available Models</a>
                
                <h3>🔧 Next Steps:</h3>
                <ol>
                    <li>Create React frontend: <code>cd frontend && npm create react-app .</code></li>
                    <li>Build frontend: <code>npm run build</code></li>
                    <li>Refresh this page for full UI</li>
                </ol>
            </div>
        </body>
        </html>
        """)

# Catch-all route for React Router (SPA support)
@app.get("/{path:path}")
async def serve_react_app(path: str):
    """Serve React app for all routes (SPA routing support)"""
    frontend_path = Path(__file__).parent.parent / "frontend" / "build" / "index.html"
    
    if frontend_path.exists():
        return FileResponse(frontend_path)
    else:
        # Redirect to main page if React build doesn't exist
        return await serve_frontend()

# Mount static files when React build exists
frontend_static = Path(__file__).parent.parent / "frontend" / "build" / "static"
if frontend_static.exists():
    app.mount("/static", StaticFiles(directory=frontend_static), name="static")

if __name__ == "__main__":
    print("🚀 Starting On-Device LLM Assistant API...")
    print("📖 API Documentation: http://localhost:8000/api/docs")
    print("🏥 Health Check: http://localhost:8000/api/health")
    
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
