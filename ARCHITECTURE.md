# iPaddyCare Backend Architecture

## Clean Architecture Overview

This project follows clean architecture principles with clear separation of concerns:

```
app/
├── api/              # API Layer (HTTP endpoints)
├── services/         # Service Layer (Business logic)
├── ml/               # ML Layer (Model implementations)
│   ├── models/       # Individual model implementations
│   ├── loaders.py    # Model loading factory
│   └── registry.py   # Model registry
├── schemas/          # Data schemas (Request/Response)
├── core/             # Core configuration
└── utils/            # Utilities (Exceptions, etc.)
```

## Layer Responsibilities

### 1. API Layer (`app/api/`)
- **Purpose**: Handle HTTP requests/responses
- **Responsibilities**:
  - Route definitions
  - Request validation (via Pydantic schemas)
  - Response formatting
  - Error handling
- **Files**:
  - `api/v1/rice_variety.py`: Rice variety prediction endpoints
  - `api/v1/health.py`: Health check endpoint
  - `api/router.py`: Main API router

### 2. Service Layer (`app/services/`)
- **Purpose**: Business logic and orchestration
- **Responsibilities**:
  - Coordinate between API and ML layers
  - Transform data between layers
  - Handle business rules
- **Files**:
  - `services/rice_variety_service.py`: Rice variety prediction service

### 3. ML Layer (`app/ml/`)
- **Purpose**: Machine learning model management
- **Components**:
  - **Base Model** (`ml/base.py`): Abstract base class for all models
  - **Model Implementations** (`ml/models/`): Specific model implementations
  - **Model Loader** (`ml/loaders.py`): Factory for loading models
  - **Model Registry** (`ml/registry.py`): Central registry for loaded models

### 4. Schema Layer (`app/schemas/`)
- **Purpose**: Data validation and serialization
- **Files**:
  - `schemas/request.py`: Request schemas
  - `schemas/response.py`: Response schemas

## Model Architecture

### Rice Variety Model

The rice variety prediction model uses a unified XGBoost approach:

1. **Training Approach**: Single unified model with variety as a feature
2. **Prediction Strategy**: Predict yield for all varieties, select highest
3. **Features**: 16 base features + 6 variety features = 22 total features

#### Base Features:
- Numerical: pH, soil_moisture_pct, EC_dS_m, soil_temp_C, water_depth_cm, lat, lon
- Categorical (encoded): texture, prev_crop, season, soil_zone
- Derived: pH_EC_interaction, moisture_temp_interaction, water_moisture_ratio, dist_from_center, season_zone

#### Model Artifacts:
- `unified_model.pkl`: Trained XGBoost model
- `scaler.pkl`: RobustScaler for feature scaling
- `label_encoders.pkl`: Label encoders for categorical features
- `variety_encoder.pkl`: Label encoder for varieties
- `variety_ohe.pkl`: One-hot encoder for varieties
- `feature_columns.pkl`: Base feature column names
- `feature_columns_with_variety.pkl`: All feature column names
- `varieties.pkl`: List of available varieties

## Adding New Models

To add a new ML model:

1. **Create Model Class** (`app/ml/models/<model_name>/model.py`):
   ```python
   from app.ml.base import MLModel
   
   class NewModel(MLModel):
       def load(self, model_path: str) -> None:
           # Load model artifacts
           pass
       
       def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
           # Make predictions
           pass
       
       def is_loaded(self) -> bool:
           # Check if loaded
           pass
   ```

2. **Register in Loader** (`app/ml/loaders.py`):
   ```python
   _model_classes = {
       "rice_variety": RiceVarietyModel,
       "new_model": NewModel,  # Add here
   }
   ```

3. **Create Service** (`app/services/new_model_service.py`):
   ```python
   class NewModelService:
       MODEL_NAME = "new_model"
       # Implement service methods
   ```

4. **Create API Endpoints** (`app/api/v1/new_model.py`):
   ```python
   router = APIRouter()
   
   @router.post("/predict")
   async def predict(...):
       # Implement endpoint
   ```

5. **Register in Router** (`app/api/router.py`):
   ```python
   api_router.include_router(new_model.router, prefix="/new-model")
   ```

6. **Load on Startup** (`app/main.py`):
   ```python
   @app.on_event("startup")
   async def startup_event():
       # Load new model
       new_model = ModelLoader.load_model("new_model", model_path)
       ModelRegistry.register("new_model", new_model)
   ```

## Request Flow

```
Client Request
    ↓
API Endpoint (app/api/v1/rice_variety.py)
    ↓
Request Validation (Pydantic Schema)
    ↓
Service Layer (app/services/rice_variety_service.py)
    ↓
Model Registry (app/ml/registry.py)
    ↓
ML Model (app/ml/models/rice_variety/model.py)
    ↓
Preprocessing (Feature Engineering, Scaling)
    ↓
Model Prediction
    ↓
Post-processing
    ↓
Response Schema
    ↓
Client Response
```

## Error Handling

Custom exceptions are defined in `app/utils/exceptions.py`:
- `MLModelError`: Base exception for ML errors
- `ModelNotFoundError`: Model not found
- `ModelLoadError`: Model loading failed
- `PredictionError`: Prediction failed
- `InvalidInputError`: Invalid input data

## Configuration

- **Logging**: Configured in `app/core/logging.py`
- **Model Paths**: Defined in `app/main.py` startup event
- **Environment Variables**: Can be added via `.env` file (using python-dotenv)

## Testing the API

1. **Start the server**:
   ```bash
   uvicorn app.main:app --reload
   ```

2. **Access Swagger UI**: http://localhost:8000/docs

3. **Test Prediction**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/rice-variety/predict" \
     -H "Content-Type: application/json" \
     -d '{
       "pH": 6.0,
       "soil_moisture_pct": 45.0,
       "EC_dS_m": 1.5,
       "soil_temp_C": 28.0,
       "water_depth_cm": 5.0,
       "lat": 7.5,
       "lon": 80.5,
       "texture": "loamy",
       "prev_crop": "rice",
       "season": "Maha",
       "soil_zone": "Intermediate"
     }'
   ```

## Dependencies

### Core Dependencies:
- `fastapi`: Web framework
- `uvicorn`: ASGI server
- `pydantic`: Data validation

### ML Dependencies:
- `xgboost`: Gradient boosting model
- `scikit-learn`: Preprocessing and utilities
- `joblib`: Model serialization
- `numpy`: Numerical operations
- `pandas`: Data manipulation

## Future Enhancements

1. **Caching**: Add Redis for caching predictions
2. **Async Model Loading**: Load models asynchronously
3. **Model Versioning**: Support multiple model versions
4. **Batch Predictions**: Add endpoint for batch predictions
5. **Monitoring**: Add metrics and logging
6. **Authentication**: Add API authentication
7. **Rate Limiting**: Add rate limiting for API endpoints

