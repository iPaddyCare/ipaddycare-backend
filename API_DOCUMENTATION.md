# iPaddyCare API Documentation

## Rice Variety Prediction API

### Base URL
```
http://localhost:8000/api/v1/rice-variety
```

## Endpoints

### 1. Predict Best Rice Variety

**POST** `/predict`

Predict the best rice variety based on environmental and soil conditions.

#### Request Body

```json
{
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
  "soil_zone": "Intermediate",
  "top_n": 3
}
```

#### Request Parameters

| Parameter | Type | Required | Description | Constraints |
|-----------|------|----------|-------------|-------------|
| pH | float | Yes | Soil pH level | 0.0 - 14.0 |
| soil_moisture_pct | float | Yes | Soil moisture percentage | 0.0 - 100.0 |
| EC_dS_m | float | Yes | Electrical conductivity (dS/m) | >= 0.0 |
| soil_temp_C | float | Yes | Soil temperature in Celsius | 0.0 - 50.0 |
| water_depth_cm | float | Yes | Water depth in centimeters | >= 0.0 |
| lat | float | Yes | Latitude | 5.0 - 10.0 (Sri Lanka) |
| lon | float | Yes | Longitude | 79.0 - 82.0 (Sri Lanka) |
| texture | string | Yes | Soil texture type | "loamy", "sandy", "clayey" |
| prev_crop | string | Yes | Previous crop type | "rice", "maize", "fallow", "legume" |
| season | string | Yes | Season | "Maha", "Yala" |
| soil_zone | string | Yes | Soil zone type | "Dry", "Intermediate", "Wet" |
| top_n | int | No | Number of top recommendations | 1 - 7 (default: 3) |

#### Response

**200 OK**

```json
{
  "best_variety": "AT378",
  "expected_yield": 9486.79,
  "recommendations": [
    {
      "variety": "AT378",
      "predicted_yield": 9486.79,
      "rank": 1
    },
    {
      "variety": "AT362",
      "predicted_yield": 8591.04,
      "rank": 2
    },
    {
      "variety": "BG374",
      "predicted_yield": 8195.82,
      "rank": 3
    }
  ],
  "all_predictions": {
    "AT378": 9486.79,
    "AT362": 8591.04,
    "BG374": 8195.82,
    "BG352": 7830.89,
    "BG300": 6926.69,
    "LD365": 5612.45,
    "BW367": 5234.12
  }
}
```

#### Error Responses

**400 Bad Request** - Invalid input
```json
{
  "error": "Invalid value for texture: invalid_value. Valid values: ['loamy', 'sandy', 'clayey']"
}
```

**503 Service Unavailable** - Model not loaded
```json
{
  "error": "Model not available: Model 'rice_variety' not found"
}
```

**500 Internal Server Error** - Prediction failed
```json
{
  "error": "Prediction failed: <error message>"
}
```

### 2. Get Available Varieties

**GET** `/varieties`

Get list of all available rice varieties that can be predicted.

#### Response

**200 OK**

```json
{
  "varieties": [
    "AT378",
    "AT362",
    "BG374",
    "BG352",
    "BG300",
    "LD365",
    "BW367"
  ],
  "count": 7
}
```

## Example Usage

### Using cURL

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
    "soil_zone": "Intermediate",
    "top_n": 3
  }'
```

### Using Python requests

```python
import requests

url = "http://localhost:8000/api/v1/rice-variety/predict"
data = {
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
    "soil_zone": "Intermediate",
    "top_n": 3
}

response = requests.post(url, json=data)
print(response.json())
```

### Using JavaScript/Fetch

```javascript
const response = await fetch('http://localhost:8000/api/v1/rice-variety/predict', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    pH: 6.0,
    soil_moisture_pct: 45.0,
    EC_dS_m: 1.5,
    soil_temp_C: 28.0,
    water_depth_cm: 5.0,
    lat: 7.5,
    lon: 80.5,
    texture: "loamy",
    prev_crop: "rice",
    season: "Maha",
    soil_zone: "Intermediate",
    top_n: 3
  })
});

const result = await response.json();
console.log(result);
```

## Interactive API Documentation

FastAPI provides interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Architecture

The API follows clean architecture principles:

1. **Schemas** (`app/schemas/`): Request/response models
2. **Models** (`app/ml/models/`): ML model implementations
3. **Services** (`app/services/`): Business logic layer
4. **API** (`app/api/`): HTTP endpoints
5. **Registry** (`app/ml/registry.py`): Model management
6. **Loaders** (`app/ml/loaders.py`): Model loading factory

