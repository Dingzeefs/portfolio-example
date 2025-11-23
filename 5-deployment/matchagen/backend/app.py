"""FastAPI backend for matcha recipe generator."""

from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from matchagen import RecipeGenerator

app = FastAPI(title="Matcha Recipe Generator", version="0.1.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model instance
model: RecipeGenerator | None = None


class GenerateRequest(BaseModel):
    """Request model for recipe generation."""

    temperature: float = 0.8
    inspiration: str = ""  # Comma-separated ingredients
    max_length: int = 512


@app.on_event("startup")
async def load_model():
    """Load the trained model on startup."""
    global model

    # Try multiple possible paths for model
    model_paths = [
        Path("artefacts/matcha-model"),
        Path("../artefacts/matcha-model"),
        Path("/app/artefacts/matcha-model"),
    ]

    for model_path in model_paths:
        if model_path.exists():
            print(f"Loading model from {model_path}")
            model = RecipeGenerator(str(model_path))
            print("Model loaded successfully!")
            return

    print("WARNING: Model not found. Please train the model first.")
    print("Run: python src/matchagen/main.py")


@app.get("/")
async def root():
    """Root endpoint - API info."""
    return {
        "app": "Matcha Recipe Generator",
        "version": "0.1.0",
        "endpoints": {
            "generate": "POST /generate",
            "health": "GET /health",
        },
    }


@app.post("/generate")
async def generate_recipe(request: GenerateRequest):
    """Generate a new matcha recipe.

    Args:
        request: Generation parameters

    Returns:
        JSON with generated recipe
    """
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please train model first.",
        )

    try:
        # Generate recipe
        recipe_text = model.generate(
            prompt=request.inspiration,
            temperature=request.temperature,
            max_length=request.max_length,
        )

        return JSONResponse(
            {
                "recipe": recipe_text,
                "temperature": request.temperature,
                "inspiration": request.inspiration,
            }
        )

    except Exception as e:
        error_msg = f"Generation failed: {str(e)}"
        raise HTTPException(status_code=500, detail=error_msg)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
