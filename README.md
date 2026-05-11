# AgriPulse PH: Agricultural Price Intelligence & Market Integration

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Project Overview

This project examines farmgate versus retail price transparency for major agricultural commodities in the Philippines from 2021 to 2025. Utilizing datasets from the Philippine Statistics Authority (PSA), the system analyzes price transmission mechanisms, marketing margins, and causal relationships between farmgate and retail prices to enhance supply chain transparency and inform policy decisions.

## Quick Facts

| **Aspect** | **Details** |
|------------|-------------|
| **Technical Stack** | Python 3.10+, FastAPI, Pandas, NumPy, Statsmodels |
| **Dataset Coverage** | 2021–2025 PSA data for 8 major commodities |
| **Key Commodities** | Banana, Mango, Pineapple, Coconut, Cassava, Ube, Palay, Corn |
| **Analysis Methods** | Marketing Margin Analysis, Granger Causality Testing |

## Key Features

- **Data Standardization**: Processes and standardizes raw PSA datasets into a unified format for consistent analysis.
- **Marketing Margin Analysis**: Calculates marketing margins and farmer's share for key commodities.
- **Granger Causality Testing**: Applies statistical tests using Statsmodels to determine if changes in farmgate prices Granger-cause changes in retail prices, assessing price transmission efficiency.

## Economic Significance

- **Supply Chain Transparency**: Identifies inefficiencies in price transmission from farmgate to retail markets.
- **Farmer Welfare**: Quantifies farmer's share in final retail prices to advocate for fair pricing policies.
- **Policy Insights**: Provides data-driven evidence for agricultural market reforms in the Philippines.
- **Market Integration**: Assesses how well farmgate price changes are reflected in retail prices over time.

## Project Structure

```
/
├── backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── requirements.txt        # Python dependencies
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── analysis.py         # Analysis-related API routes
│   │   └── prices.py           # Price data API routes
│   ├── services/
│   │   ├── __init__.py
│   │   ├── analytics_service.py # Analytics and statistical computations
│   │   ├── data_service.py     # Data loading and processing
│   │   └── price_service.py    # Price-specific calculations
│   ├── models/
│   │   ├── __init__.py
│   │   └── price_model.py      # Data models and schemas
│   ├── utils/
│   │   ├── __init__.py
│   │   └── standardizer.py     # Data standardization utilities
│   └── data/
│       └── FINAL Datasets - Farmgate&Retail Prices (Average, Margin).csv
├── frontend/
│   ├── main.py                 # Frontend application entry point
│   ├── requirements.txt        # Python dependencies
│   ├── routes/
│   │   └── __init__.py
│   └── static/
│       └── index.html          # Static HTML frontend
└── README.md                   # Project documentation
```

## Setup Instructions

### Prerequisites
- **Python**: 3.10 or higher
- **Package Manager**: pip

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd philippine-agri-price-analysis
   ```

2. **Install backend dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Install frontend dependencies**:
   ```bash
   cd ../frontend
   pip install -r requirements.txt
   ```

### Running the Application

1. **Start the backend API**:
   ```bash
   cd backend
   python main.py
   ```

2. **Start the frontend** (in a separate terminal):
   ```bash
   cd frontend
   python main.py
   ```

The backend will be available at `http://localhost:8000` and the frontend at `http://localhost:8080` (or as configured).

## API Endpoints

The backend provides RESTful API endpoints under the `/api/analysis/` prefix for various analytical operations:

### Margin Analysis
```http
GET /api/analysis/margins/{commodity}
```
Retrieve marketing margins and farmer's share for a specific commodity.

```http
POST /api/analysis/margins/batch
```
Calculate margins for multiple commodities.

### Trend Analysis
```http
GET /api/analysis/trends/{commodity}
```
Get price trend analysis for a commodity over time.

```http
GET /api/analysis/trends/comparison
```
Compare trends between farmgate and retail prices.

### Causality Testing
```http
GET /api/analysis/causality/{commodity}
```
Perform Granger causality test between farmgate and retail prices for a commodity.

```http
POST /api/analysis/causality/multiple
```
Run causality tests for multiple commodities.

## How to Interpret Results

In the context of Granger causality testing for Philippine agricultural price transparency:

- **Low p-value (< 0.05)**: Indicates strong evidence that farmgate price changes significantly predict retail price movements, suggesting efficient price transmission and good market integration.
- **High p-value (≥ 0.05)**: Suggests weak or no causal relationship, potentially indicating market inefficiencies, information asymmetries, or external factors disrupting price transmission in the agricultural supply chain.

## Contributors

| **Name** | **Role** | **Affiliation** |
|----------|----------|-----------------|
| [Your Name] | Project Lead & Developer | [Your Institution] |
| [Contributor 1] | Data Analyst | [Affiliation] |
| [Contributor 2] | Backend Developer | [Affiliation] |

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Causality Testing
- `GET /api/analysis/causality/{commodity}` - Perform Granger causality test between farmgate and retail prices for a commodity
- `POST /api/analysis/causality/multiple` - Run causality tests for multiple commodities

All endpoints return JSON responses with detailed analysis results, including statistical metrics and visualizations where applicable.
```
then open: 
http://127.0.0.1:8000/docs

---
## API Endpoints & Features

### 1. Marketing Margin Analysis
**Endpoint:** `/analysis/margin/{commodity}`  

- Computes price spread and farmer share  

**Formulas:**
- `Margin = Retail - Farmgate`  
- `Farmer's Share = (Farmgate / Retail) × 100`  

---

### 2. Granger Causality Test
**Endpoint:** `/analysis/causality/{commodity}`  

- Tests if farmgate prices predict retail prices  

**Interpretation:**
- `p-value < 0.05` → Significant relationship  
- Indicates responsive or delayed price transmission  

---

### 3. Time-Series Trends
**Endpoint:** `/analysis/trends`  

- Aggregates data monthly or yearly  
- Identifies trends, inflation, and seasonal patterns  

---

## Economic Significance

This system helps identify:

- **Market Inefficiency** → Large margins indicate high intermediary costs  
- **Price Rigidity** → Retail prices remain high despite falling farmgate prices  
- **Food Security Risks** → Volatility in staple crops like rice (palay) and corn  

## Dataset

- **Source**: Philippine Statistics Authority (PSA)  
- **Coverage**: 2021–2025  
- **Commodities**:  Rice, Corn, Coconut, Bananas, Pineapples, Mangoes, and Cassava

---

## Contributors
- **ARONG** – Lead Researcher
- **LOPEZ** - Frontend Developer 
- **LOSORATA** – Data Analyst & Backend Developer 
