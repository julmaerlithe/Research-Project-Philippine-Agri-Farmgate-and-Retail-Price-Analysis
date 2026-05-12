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
| **Dataset Coverage** | 2021-2025 PSA monthly price data |
| **Key Commodities** | Rice, Corn, Coconut, Cassava, Banana, Pineapple, Mango |
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

### Marketing Margin Analysis
```http
GET /analysis/margin/{commodity}
GET /api/analysis/margin/{commodity}
```
Retrieve marketing margins and farmer's share for a specific commodity.

```http
Margin = Retail - Farmgate
Farmer's Share = (Farmgate / Retail) * 100
```

### Trend Analysis
```http
GET /analysis/trends?commodity={commodity}&frequency=monthly
GET /api/analysis/trends?commodity={commodity}&frequency=monthly
```
Get monthly or yearly price trend analysis for a commodity over time.

```http
GET /analysis/trends?frequency=yearly
GET /api/analysis/trends?frequency=yearly
```
Compare aggregated farmgate, retail, margin, and farmer share trends.

```http
Trend Equation: Yt = a + bt
Growth Rate = ((Pt - Pt-1) / Pt-1) * 100
```

### Causality Testing
```http
GET /analysis/causality/{commodity}
GET /api/analysis/causality/{commodity}
```
Perform Granger causality test between farmgate and retail prices for a commodity.

```http
p-value < 0.05 means farmgate prices significantly predict retail prices.
```

## How to Interpret Results

In the context of Granger causality testing for Philippine agricultural price transparency:

- **Low p-value (< 0.05)**: Indicates strong evidence that farmgate price changes significantly predict retail price movements, suggesting efficient price transmission and good market integration.
- **High p-value (≥ 0.05)**: Suggests weak or no causal relationship, potentially indicating market inefficiencies, information asymmetries, or external factors disrupting price transmission in the agricultural supply chain.

## Dataset

- **Source**: Philippine Statistics Authority (PSA)  
- **Coverage**: 2021-2025  
- **Commodities**: Rice, Corn, Coconut, Cassava, Bananas, Pineapples, and Mangoes.

---

## Contributors
- **ARONG** – Lead Researcher
- **LOPEZ** - Frontend Developer 
- **LOSORATA** – Data Analyst & Backend Developer 


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
