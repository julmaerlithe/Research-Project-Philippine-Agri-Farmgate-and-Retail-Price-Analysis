# AgriPulse PH: Agricultural Price Intelligence & Market Integration

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)

## Project Overview

This project examines farmgate versus retail price transparency for major agricultural commodities in the Philippines from 2021 to 2025. Using Philippine Statistics Authority (PSA) price data, the system analyzes price transmission, marketing margins, farmer share, trends, and Granger causality relationships between farmgate and retail prices.

The project includes a Flask backend API and a Flask-served frontend dashboard for exploring agricultural price behavior and market integration.

## Quick Facts

| Aspect | Details |
| --- | --- |
| Technical Stack | Python 3.10+, Flask, Flask-CORS, Pandas, NumPy, SciPy, Statsmodels |
| Dataset Coverage | 2021-2025 PSA monthly price data |
| Key Commodities | Rice, Corn, Coconut, Cassava, Banana, Pineapple, Mango |
| Analysis Methods | Marketing Margin Analysis, Farmer Share, Trend Analysis, Granger Causality Testing |
| Backend Port | `http://localhost:5000` |
| Frontend Port | `http://localhost:5001` |

## Key Features

- **Data Standardization**: Loads the raw PSA dataset and converts it into a consistent long-form analytical structure.
- **Marketing Margin Analysis**: Calculates the difference between retail and farmgate prices.
- **Farmer Share Analysis**: Estimates the percentage of the retail price received at the farmgate level.
- **Trend Analysis**: Provides monthly and yearly summaries, growth rates, volatility, trend equations, and seasonal indicators.
- **Granger Causality Testing**: Uses Statsmodels to test whether farmgate price movements help predict retail price movements.
- **Dashboard Data Endpoint**: Provides a combined API response for frontend charts and summary cards.

## Economic Significance

- **Supply Chain Transparency**: Highlights differences between farmgate and retail prices.
- **Farmer Welfare**: Quantifies farmer share in final retail prices.
- **Policy Insights**: Provides evidence for agricultural market reforms and price monitoring.
- **Market Integration**: Assesses whether farmgate price changes are reflected in retail prices over time.

## Project Structure

```text
/
|-- backend/
|   |-- main.py                 # Flask backend API entry point
|   |-- requirements.txt        # Backend Python dependencies
|   |-- test.py                 # Local test/helper script
|   |-- verify.py               # Local verification/helper script
|   |-- routes/
|   |   |-- __init__.py
|   |   |-- analysis.py         # Analysis API routes
|   |   `-- prices.py           # Price data API routes
|   |-- services/
|   |   |-- __init__.py
|   |   |-- analytics_service.py # Analytics and statistical computations
|   |   |-- data_service.py      # Data loading and standardization
|   |   `-- price_service.py     # Price-related service module
|   |-- models/
|   |   |-- __init__.py
|   |   `-- price_model.py       # Data models and schemas
|   |-- utils/
|   |   |-- __init_.py
|   |   `-- standardizer.py      # Data standardization utilities
|   `-- data/
|       `-- FINAL Datasets - Farmgate&Retail Prices (Average, Margin).csv
|-- frontend/
|   |-- main.py                 # Flask frontend static server
|   |-- requirements.txt        # Frontend Python dependencies
|   |-- routes/
|   |   `-- __init__.py
|   `-- static/
|       |-- index.html          # Frontend dashboard
|       `-- logo-hehe.png       # Frontend logo asset
`-- README.md
```

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- pip

### Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd Research-Project-Philippine-Agri-Farmgate-and-Retail-Price-Analysis
   ```

2. Install backend dependencies:

   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Install frontend dependencies:

   ```bash
   cd ../frontend
   pip install -r requirements.txt
   ```

## Running the Application

1. Start the backend API:

   ```bash
   cd backend
   python main.py
   ```

   The backend API runs at:

   ```text
   http://localhost:5000
   ```

2. Start the frontend in a separate terminal:

   ```bash
   cd frontend
   python main.py
   ```

   The frontend dashboard runs at:

   ```text
   http://localhost:5001
   ```

The frontend calls the backend API at `http://localhost:5000/api`.

## API Endpoints

### Health Check

```http
GET /api/health
```

Checks whether the backend is running.

### Price Data

```http
GET /api/prices/all
```

Returns all standardized price records.

```http
GET /api/prices/commodities
```

Returns the available commodity names.

```http
GET /api/prices/{commodity}
```

Returns standardized price records for a specific commodity.

Supported commodity names and aliases include `Rice`, `Palay`, `Corn`, `Coconut`, `Cassava`, `Banana`, `Pineapple`, and `Mango`.

### Marketing Margin Analysis

```http
GET /api/analysis/margin/{commodity}
GET /analysis/margin/{commodity}
```

Returns monthly farmgate price, retail price, marketing margin, and farmer share for a specific commodity.

```text
Margin = Retail - Farmgate
Farmer Share = (Farmgate / Retail) * 100
```

### All Commodity Margins

```http
GET /api/analysis/margins/all
GET /analysis/margins/all
```

Returns average margin, farmgate price, retail price, and farmer share for all target commodities.

### Trend Analysis

```http
GET /api/analysis/trends?commodity={commodity}&frequency=monthly
GET /api/analysis/trends?commodity={commodity}&frequency=yearly
GET /analysis/trends?commodity={commodity}&frequency=monthly
GET /analysis/trends?commodity={commodity}&frequency=yearly
```

Returns trend, volatility, growth rate, inflation, and seasonal analysis for one commodity.

```http
GET /api/analysis/trends?frequency=monthly
GET /api/analysis/trends?frequency=yearly
GET /analysis/trends?frequency=monthly
GET /analysis/trends?frequency=yearly
```

Returns trend analysis for all target commodities.

```text
Trend Equation: Yt = a + bt
Growth Rate = ((Pt - Pt-1) / Pt-1) * 100
```

### Causality Testing

```http
GET /api/analysis/causality/{commodity}
GET /analysis/causality/{commodity}
```

Performs a Granger causality test between farmgate and retail prices for a commodity. The optional `max_lag` query parameter is supported and is capped between 1 and 3.

Example:

```http
GET /api/analysis/causality/Rice?max_lag=3
```

### Dashboard Data

```http
GET /api/analysis/dashboard-data
GET /analysis/dashboard-data
```

Returns the combined data model used by the frontend dashboard:

```text
commodities, margin, granger, trends, yearly
```

## How to Interpret Results

For Granger causality testing:

- **Low p-value below 0.05**: Farmgate price changes significantly help predict retail price changes, suggesting stronger price transmission.
- **High p-value at or above 0.05**: The test does not find significant predictive evidence from farmgate prices to retail prices, which may suggest weaker price transmission or other market influences.

For marketing margins:

- **Higher margin**: A larger gap between retail and farmgate prices.
- **Higher farmer share**: A larger percentage of the retail price is represented by the farmgate price.

## Dataset

- **Source**: Philippine Statistics Authority (PSA)
- **Coverage**: Monthly data from 2021 to 2025
- **Commodities**: Rice, Corn, Coconut, Cassava, Banana, Pineapple, and Mango
- **Dataset file**: `backend/data/FINAL Datasets - Farmgate&Retail Prices (Average, Margin).csv`

## Contributors

- **ARONG** - Lead Researcher
- **LOPEZ** - Frontend Developer and Frontend-Backend Integration
- **LOSORATA** - Data Analyst and Backend Developer
