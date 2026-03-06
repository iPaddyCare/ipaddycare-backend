from pathlib import Path
from fastapi import FastAPI
from app.api.router import api_router
from app.ml.loaders import ModelLoader
from app.ml.registry import ModelRegistry
from app.utils.exceptions import ModelLoadError
from app.core.logging import setup_logging
import logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="iPaddyCare - AI Powered Paddy Field Monitoring System",
    description="iPaddyCare is an AI-powered paddy field monitoring system that uses machine learning to monitor and analyze paddy fields.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "iPaddyCare",
        "url": "https://ipaddycare.com",
        "email": "contact@ipaddycare.com",
    },
)


@app.on_event("startup")
async def startup_event():
    """Load ML models on application startup"""
    logger.info("Loading ML models...")
    
    # Get base directory (backend root)
    # __file__ is app/main.py, so parent.parent gives us backend/
    base_dir = Path(__file__).parent.parent
    
    # Load rice variety model (old)
    try:
        rice_variety_path = base_dir / "app" / "ml" / "models" / "rice_variety"
        logger.info(f"Loading old rice variety model from: {rice_variety_path}")
        rice_variety_model = ModelLoader.load_model("rice_variety", str(rice_variety_path))
        ModelRegistry.register("rice_variety", rice_variety_model)
        logger.info("Old rice variety model loaded successfully")
    except ModelLoadError as e:
        logger.error(f"Failed to load old rice variety model: {e}")
        # Don't raise - allow app to start but predictions will fail gracefully
    except Exception as e:
        logger.error(f"Unexpected error loading old rice variety model: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    # Load new rice variety model (tuned models)
    try:
        new_rice_variety_path = base_dir / "app" / "ml" / "models" / "rice_variety" / "new"
        logger.info(f"Loading new rice variety model from: {new_rice_variety_path}")
        new_rice_variety_model = ModelLoader.load_model("rice_variety_new", str(new_rice_variety_path))
        ModelRegistry.register("rice_variety_new", new_rice_variety_model)
        logger.info("New rice variety model loaded successfully")
    except ModelLoadError as e:
        logger.error(f"Failed to load new rice variety model: {e}")
        # Don't raise - allow app to start but predictions will fail gracefully
    except Exception as e:
        logger.error(f"Unexpected error loading new rice variety model: {e}")
        import traceback
        logger.error(traceback.format_exc())


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("Shutting down application...")


app.include_router(api_router)


@app.get("/")
def root():
    return {"message": "Welcome to iPaddyCare - AI Powered Paddy Field Monitoring System"}